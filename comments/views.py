from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView, CreateView

import django_comments
from django_comments.views.moderation import perform_flag
from django_comments.views.comments import post_comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from threadedcomments.forms import ThreadedCommentForm
from threadedcomments.models import ThreadedComment
from django.views.generic.base import ContextMixin


class AdminCommentReplyView(FormView, ContextMixin):
    form_class = ThreadedCommentForm
    template_name = "admin/reply.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent"] = self.get_form_kwargs()["target_object"]
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AdminCommentReplyView, self).get_form_kwargs(*args, **kwargs)
        kwargs["parent"] = self.kwargs["parent"]
        kwargs["target_object"] = ThreadedComment.objects.get(pk=self.kwargs["parent"])
        del kwargs["prefix"]
        return kwargs

    #
    # def form_valid(self, form):
    #     print("inside form valid")
    #     self.request.POST = self.request.POST.copy()
    #     self.request.POST["name"] = ""
    #     self.request.POST["url"] = ""
    #     self.request.POST["email"] = ""
    #     self.request.POST["parent"] = self.kwargs["parent"]
    #     reply = post_comment(self.request, next=self.success_url)
    #     messages.success(self.request, _("Reply successfully created."))
    #     return reply
