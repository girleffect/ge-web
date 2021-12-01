from django import forms
from django.apps import apps
from django.conf import settings
from django.shortcuts import render
from django.utils.html import escape
from django.forms import ModelChoiceField
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from molo.commenting.models import MoloComment, CannedResponse
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, ValidationError


from django_comments import signals
from django_comments import get_form
from django_comments.forms import CommentForm
from django_comments.views.utils import next_redirect
from django_comments.views.comments import CommentPostBadRequest

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class MoloCommentForm(CommentForm):
    email = forms.EmailField(label=_("Email address"), required=False)
    parent = forms.ModelChoiceField(
        queryset=MoloComment.objects.all(),
        required=False, widget=forms.HiddenInput)
    comment = forms.CharField(
        label=_('Comment'), widget=forms.Textarea,
        max_length=COMMENT_MAX_LENGTH)

    def get_comment_model(self, site_id=None):
        # Use our custom comment model instead of the built-in one.
        return MoloComment

    def get_comment_create_data(self, site_id=None):
        # Use the data of the superclass, and add in the parent field field
        data = super(MoloCommentForm, self)\
            .get_comment_create_data(site_id=site_id)
        data['parent'] = self.cleaned_data['parent']
        return data

    def get_comment_object(self, site_id=None):
        """
        NB: Overridden to remove dupe comment check for admins (necessary for
        canned responses)
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.
        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError(
                "get_comment_object may only be called on valid forms")

        CommentModel = self.get_comment_model(site_id=site_id)
        new = CommentModel(**self.get_comment_create_data())

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=new.user_name)
            if not user.is_staff:
                new = self.check_for_duplicate_comment(new)
        except user_model.DoesNotExist:
            # post_molo_comment may have set the username to 'Anonymous'
            new = self.check_for_duplicate_comment(new)

        return new

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MoloCommentForm, self).__init__(*args, **kwargs)


class AdminMoloCommentReplyForm(MoloCommentForm):
    parent = forms.ModelChoiceField(
        queryset=MoloComment.objects.all(), widget=forms.HiddenInput,
        required=False)
    email = forms.EmailField(
        label=_("Email address"), required=False, widget=forms.HiddenInput)
    url = forms.URLField(
        label=_("URL"), required=False, widget=forms.HiddenInput)
    name = forms.CharField(
        label=_("Name"), required=False, widget=forms.HiddenInput)
    honeypot = forms.CharField(
        required=False, widget=forms.HiddenInput)

    canned_response = ModelChoiceField(queryset=CannedResponse.objects.all(),
                                       label="Or add a canned response",
                                       to_field_name="response",
                                       required=False)

    def __init__(self, *args, **kwargs):
        parent = MoloComment.objects.get(pk=kwargs.pop('parent'))
        super(AdminMoloCommentReplyForm, self).__init__(
            parent.content_object, *args, **kwargs
        )

    def post_comment(self, request, next=None, using=None):
        """
        see from django_comments.views.comments import post_comment
        had to copy post_comment func
        to be able to pass form kwargs namely the request
        kept everything else the same not to loose on some
        django_comments features
        """

        data = request.POST.copy()
        if request.user.is_authenticated:
            if not data.get('name', ''):
                data["name"] = request.user.get_full_name()\
                    or request.user.get_username()
            if not data.get('email', ''):
                data["email"] = request.user.email

        ctype = data.get("content_type")
        object_pk = data.get("object_pk")

        if ctype is None or object_pk is None:
            return CommentPostBadRequest(
                "Missing content_type or object_pk field.")
        try:
            model = apps.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(using).get(pk=object_pk)
        except TypeError:
            return CommentPostBadRequest(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            return CommentPostBadRequest(
                "The given content-type %r does "
                "not resolve to a valid model." % escape(ctype))
        except ObjectDoesNotExist:
            return CommentPostBadRequest(
                "No object matching content-type %r "
                "and object PK %r exists." % (
                    escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError) as e:
            return CommentPostBadRequest(
                "Attempting go get content-type %r and "
                "object PK %r exists raised %s" % (
                    escape(ctype), escape(object_pk), e.__class__.__name__))

        preview = "preview" in data
        form = get_form()(target, data=data, request=request)

        if form.security_errors():
            return CommentPostBadRequest(
                "The comment form failed security verification: %s"
                % escape(str(form.security_errors())))

        if form.errors or preview:
            template_list = [
                "comments/%s_%s_preview.html" % (
                    model._meta.app_label, model._meta.model_name),
                "comments/%s_preview.html" % model._meta.app_label,
                "comments/%s/%s/preview.html" % (
                    model._meta.app_label, model._meta.model_name),
                "comments/%s/preview.html" % model._meta.app_label,
                "comments/preview.html",
            ]
            return render(
                request,
                template_list, {
                    "comment": form.data.get("comment", ""),
                    "form": form, "next": data.get("next", next),
                },
            )

        comment = form.get_comment_object(site_id=get_current_site(request).id)
        comment.ip_address = request.META.get("REMOTE_ADDR", None) or None
        if request.user.is_authenticated:
            comment.user = request.user

        responses = signals.comment_will_be_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=request
        )

        for (receiver, response) in responses:
            if response is False:
                return CommentPostBadRequest(
                    "comment_will_be_posted receiver %r killed the comment"
                    % receiver.__name__
                )

        comment.save()
        signals.comment_was_posted.send(
            sender=comment.__class__,
            comment=comment,
            request=request
        )
        return next_redirect(
            request,
            fallback=next or 'comments-comment-done',
            c=comment._get_pk_val()
        )
