import json
import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.db.models.fields import BooleanField, TextField
from django.dispatch import receiver
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.forms import models as forms_models
from wagtail.contrib.forms.models import (
    AbstractFormField,
    AbstractEmailForm,
    AbstractFormSubmission,
)

from wagtail.contrib.forms.views import SubmissionsListView
from wagtail.contrib.forms.forms import SelectDateForm
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel


class CustomFormSubmission(AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_data(self):
        form_data = super().get_data()
        form_data.update(
            {
                "username": self.user.username,
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

    allow_anonymous_submissions = BooleanField(
        default=False,
        help_text="Check this to allow users who are NOT logged in to complete"
        " forms.",
    )
    allow_multiple_submissions_per_user = BooleanField(
        default=False,
        help_text="Check this to allow users to complete a form more than" " once.",
    )

    show_results = BooleanField(
        default=False,
        help_text="Whether to show the form results to the user after they"
        " have submitted their answer(s).",
    )
    show_results_as_percentage = BooleanField(
        default=False,
        help_text="Whether to show the form results to the user after they"
        " have submitted their answer(s) as a percentage or as"
        " a number.",
    )

    multi_step = BooleanField(
        default=False,
        verbose_name="Multi-step",
        help_text="Whether to display the form questions to the user one at"
        " a time, instead of all at once.",
    )

    display_form_directly = BooleanField(
        default=False,
        verbose_name="Display Question Directly",
        help_text="This is similar to polls, in which the questions are "
        "displayed directly on the page, instead of displaying "
        "a link to another page to complete the form.",
    )
    your_words_competition = BooleanField(
        default=False,
        verbose_name="Is YourWords Competition",
        help_text="This will display the correct template for yourwords",
    )
    contact_form = BooleanField(
        default=False,
        verbose_name="Is Contact Form",
        help_text="This will display the correct template for contact forms",
    )

    content_panels = forms_models.AbstractForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("introduction", classname="full"),
        ImageChooserPanel("image"),
        StreamFieldPanel("description"),
        InlinePanel("form_fields", label="Form fields"),
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
                FieldPanel("show_results_as_percentage"),
                FieldPanel("multi_step"),
                FieldPanel("display_form_directly"),
                FieldPanel("your_words_competition"),
                FieldPanel("contact_form"),
            ],
            heading="Form Settings",
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

        # If you need to show results only on landing page,
        # you may need check request.method

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
                    answer = u", ".join(answer)

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
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
            user=form.user,
        )

    def serve(self, request, *args, **kwargs):
        if (
            self.allow_multiple_submissions_per_user is False
            and self.get_submission_class()
            .objects.filter(page=self, user__pk=request.user.pk)
            .exists()
        ):
            return render(request, self.template, self.get_context(request))
        if self.multi_step:
            session_key_data = "form_data-%s" % self.pk
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
                    form_data = request.session.get(session_key_data, {})
                    form_data.update(prev_form.cleaned_data)
                    request.session[session_key_data] = form_data

                    if prev_step.has_next():
                        # Create a new form for a following step, if the following step is present
                        form_class = self.get_form_class_for_step(step)
                        form = form_class(page=self, user=request.user)
                    else:
                        # If there is no next step, create form for all fields
                        form = self.get_form(
                            request.session[session_key_data],
                            page=self,
                            user=request.user,
                        )

                        if form.is_valid():
                            # Perform validation again for whole form.
                            # After successful validation, save data into DB,
                            # and remove from the session.
                            form_submission = self.process_form_submission(form)
                            del request.session[session_key_data]
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
