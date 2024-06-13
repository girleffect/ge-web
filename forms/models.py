import json

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields import BooleanField
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms import models as forms_models
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtail.admin.edit_handlers import (  # isort:skip
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.contrib.forms.models import (  # isort:skip
    AbstractEmailForm,
    AbstractFormField,
    AbstractFormSubmission,
)


class CustomFormSubmission(AbstractFormSubmission):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )

    def get_data(self):
        form_data = super().get_data()
        for key, value in form_data.items():
            # Convert lists to strings so they display properly in the view
            if isinstance(value, list):
                form_data[key] = u", ".join(value)
        form_data.update(
            {
                "username": self.user.username if self.user else "Anonymous",
            }
        )

        return form_data


class FormField(AbstractFormField):
    page = ParentalKey("FormPage", on_delete=models.CASCADE, related_name="form_fields")


class FormsIndexPage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["forms.FormPage"]


class FormPage(AbstractEmailForm):
    parent_page_types = ["forms.FormsIndexPage"]
    subpage_types = []

    introduction = RichTextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    description = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    allow_anonymous_submissions = BooleanField(
        default=False,
        help_text=_(
            "Check this to allow users who are NOT logged in to complete" " forms."
        ),
    )
    allow_multiple_submissions_per_user = BooleanField(
        default=False,
        help_text=_("Check this to allow users to complete a form more than" " once."),
    )

    show_results = BooleanField(
        default=False,
        help_text=_(
            "Whether to show the form results to the user after they"
            " have submitted their answer(s)."
        ),
    )

    multi_step = BooleanField(
        default=False,
        verbose_name="Multi-step",
        help_text=_(
            "Whether to display the form questions to the user one at"
            " a time, instead of all at once."
        ),
    )
    your_words_competition = BooleanField(
        default=False,
        verbose_name="Is YourWords Competition",
        help_text=_("This will display the correct template for yourwords"),
    )
    contact_form = BooleanField(
        default=False,
        verbose_name="Is Contact Form",
        help_text=_("This will display the correct template for contact forms"),
    )

    content_panels = forms_models.AbstractForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("introduction", classname="full"),
        ImageChooserPanel("image"),
        StreamFieldPanel("description"),
        InlinePanel("form_fields", label=_("Form fields")),
        FieldPanel("thank_you_text", classname="full"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("from_address", classname="col6"),
                        FieldPanel("to_address", classname="col6"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            "Email",
        ),
    ]

    settings_panels = forms_models.AbstractForm.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("allow_anonymous_submissions"),
                FieldPanel("allow_multiple_submissions_per_user"),
                FieldPanel("show_results"),
                FieldPanel("multi_step"),
                FieldPanel("your_words_competition"),
                FieldPanel("contact_form"),
            ],
            heading=_("Form Settings"),
        )
    ]

    def get_data_fields(self):
        data_fields = [
            ("username", "Username"),
        ]
        data_fields += super().get_data_fields()

        return data_fields

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        if not self.show_results:
            # return early, without further processing
            return context
        results = dict()
        # Get information about form fields
        data_fields = [
            (field.clean_name, field.label) for field in self.get_form_fields()
        ]

        # Get all submissions for current page
        submissions = self.get_submission_class().objects.filter(page=self)
        for submission in submissions:
            data = submission.get_data()

            # Count results for each question
            for name, label in data_fields:
                answer = data.get(name)
                if answer is None:
                    # Something wrong with data.
                    # Probably you have changed questions
                    # and now we are receiving answers for old questions.
                    # Just skip them.
                    continue

                if type(answer) is list:
                    # Answer is a list if the field type is 'Checkboxes'
                    answer = ", ".join(answer)

                question_stats = results.get(label, {})
                question_stats[answer] = question_stats.get(answer, 0) + 1
                results[label] = question_stats

        context.update(
            {
                "results": results,
            }
        )
        return context

    def get_submission_class(self):
        return CustomFormSubmission

    def process_form_submission(self, form):
        user = form.user if not form.user.is_anonymous else None
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
            user=user,
        )

    @property
    def session_key_data(self):
        return "form_data-{}".format(self.pk)

    def load_data(self, request):
        return json.loads(request.session.get(self.session_key_data, "{}"))

    def save_data(self, request, data):
        request.session[self.session_key_data] = json.dumps(data, cls=DjangoJSONEncoder)

    def serve(self, request, *args, **kwargs):
        if (
            not self.allow_anonymous_submissions
            and not self.allow_multiple_submissions_per_user
            and self.get_submission_class()
            .objects.filter(page=self, user__pk=request.user.pk)
            .exists()
        ):
            return render(request, self.template, self.get_context(request))
        if not request.user.is_authenticated and not self.allow_anonymous_submissions:
            return render(request, self.template, self.get_context(request))
        if self.multi_step:
            is_last_step = False
            step_number = request.GET.get("p", 1)

            paginator = Paginator(self.get_form_fields(), per_page=1)
            try:
                step = paginator.page(step_number)
            except PageNotAnInteger:
                step = paginator.page(1)
            except EmptyPage:
                step = paginator.page(paginator.num_pages)
                is_last_step = True

            if request.method == "POST":
                # The first step will be submitted with step_number == 2,
                # so we need to get a form from previous step
                # Edge case - submission of the last step
                prev_step = (
                    step
                    if is_last_step
                    else paginator.page(step.previous_page_number())
                )

                # Create a form only for submitted step
                prev_form_class = self.get_form_class_for_step(prev_step)
                prev_form = prev_form_class(request.POST, page=self, user=request.user)
                if prev_form.is_valid():
                    # If data for step is valid, update the session
                    form_data = self.load_data(request)
                    form_data.update(prev_form.cleaned_data)
                    self.save_data(request, form_data)

                    if prev_step.has_next():
                        # Create a new form for a following step, if the following step is present
                        form_class = self.get_form_class_for_step(step)
                        form = form_class(page=self, user=request.user)
                    else:
                        # If there is no next step, create form for all fields
                        data = self.load_data(request)
                        form = self.get_form(
                            data,
                            page=self,
                            user=request.user,
                        )

                        if form.is_valid():
                            # Perform validation again for whole form.
                            # After successful validation, save data into DB,
                            # and remove from the session.
                            form_submission = self.process_form_submission(form)
                            del request.session[self.session_key_data]
                            # render the landing page
                            return self.render_landing_page(
                                request, form_submission, *args, **kwargs
                            )
                else:
                    # If data for step is invalid
                    # we will need to display form again with errors,
                    # so restore previous state.
                    form = prev_form
                    step = prev_step
            else:
                # Create empty form for non-POST requests
                form_class = self.get_form_class_for_step(step)
                form = form_class(page=self, user=request.user)

            context = self.get_context(request)
            context["form"] = form
            context["fields_step"] = step
            return render(request, self.template, context)
        return super().serve(request, *args, **kwargs)

    def get_form_class_for_step(self, step):
        return self.form_builder(step.object_list).get_form_class()
