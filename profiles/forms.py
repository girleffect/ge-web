import datetime
import re

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.widgets import SelectDateWidget
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Profile

User = get_user_model()

REGEX_PHONE = getattr(
    settings, "REGEX_PHONE", r".*?(\(?\d{3})? ?[\.-]? ?\d{3} ?[\.-]? ?\d{4}.*?"
)

REGEX_EMAIL = getattr(settings, "REGEX_EMAIL", r"([\w\.-]+@[\w\.-]+)")


def validate_no_email_or_phone(input):

    regexes = [REGEX_PHONE, REGEX_EMAIL]

    for regex in regexes:
        match = re.search(regex, input)
        if match:
            return False

    return True


class DateOfBirthValidationMixin(object):
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get("date_of_birth")
        is_date = isinstance(date_of_birth, datetime.date)

        if date_of_birth and not is_date:
            date_of_birth = timezone.datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        else:
            user_input = (
                self.data.get("date_of_birth_year"),
                self.data.get("date_of_birth_month"),
                self.data.get("date_of_birth_day"),
            )
            if all(user_input):
                try:
                    date_of_birth = timezone.datetime(
                        *(int(i) for i in user_input)
                    ).date()
                except ValueError:
                    date_of_birth = None

        return date_of_birth


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r"^[\w.@+-]+$",
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            "invalid": _(
                "This value must contain only letters, numbers and underscores."
            ),
        },
    )
    password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True, render_value=False, type="password", autocomplete="off"
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _("This value must contain only numbers."),
        },
        label=_("PIN"),
    )
    terms_and_conditions = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        kwargs.pop("request", [])
        kwargs.pop("context", [])
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # Security questions fields are created dynamically.
        # This allows any number of security questions to be specified
        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=question.title,
                widget=forms.TextInput(
                    attrs=dict(
                        max_length=150,
                    )
                ),
            )

    def security_questions(self):
        return [
            field
            for field_name, field in self.fields.items()
            if field_name.startswith("question_")
        ]

    def clean_username(self):
        if User.objects.filter(username__iexact=self.cleaned_data["username"]).exists():
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use your phone number or email address in your username."
                )
            )

        if not validate_no_email_or_phone(self.cleaned_data["username"]):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use"
                    " your phone number or email address in your username."
                )
            )
        return self.cleaned_data["username"]


class DoneForm(DateOfBirthValidationMixin, forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(years=list(reversed(range(1930, timezone.now().year)))),
        label=_("Date of Birth"),
        required=False,
    )

    class Meta:
        model = Profile
        fields = ["date_of_birth", "gender", "location"]


class EditProfileForm(DateOfBirthValidationMixin, forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        ),
        label=_("Date of Birth"),
        required=False,
    )
    gender = forms.ChoiceField(
        label=_("Gender"), choices=Profile.Gender.choices, required=False
    )
    location = forms.CharField(label=_("Location"), required=False)

    class Meta:
        model = Profile
        fields = [
            "date_of_birth",
            "gender",
            "location",
        ]


class ProfilePasswordChangeForm(forms.Form):
    old_password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True, render_value=False, type="password", autocomplete="off"
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _(
                "This value must contain only  \
         numbers."
            )
        },
        label=_("Old Password"),
    )
    new_password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True, render_value=False, type="password", autocomplete="off"
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _(
                "This value must contain only  \
         numbers."
            )
        },
        label=_("New Password"),
    )
    confirm_password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type="password",
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _("This value must contain only numbers."),
        },
        label=_("Confirm Password"),
    )

    def clean(self):
        new_password = self.cleaned_data.get("new_password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)
        if new_password and confirm_password and (new_password == confirm_password):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_("New passwords do not match."))


class ForgotPasswordForm(forms.Form):
    username = forms.RegexField(
        regex=r"^[\w.@+-]+$",
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            "invalid": _(
                "This value must contain only letters, " "numbers and underscores."
            ),
        },
    )

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=question.title,
                widget=forms.TextInput(
                    attrs=dict(
                        required=True,
                        max_length=150,
                    )
                ),
            )


class ResetPasswordForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput())

    token = forms.CharField(widget=forms.HiddenInput())

    password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True, render_value=False, type="password", autocomplete="off"
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _("This value must contain only numbers."),
        },
        label=_("PIN"),
    )

    confirm_password = forms.RegexField(
        regex=r"^\d{4}$",
        widget=forms.PasswordInput(
            attrs=dict(
                required=True, render_value=False, type="password", autocomplete="off"
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            "invalid": _("This value must contain only numbers."),
        },
        label=_("Confirm PIN"),
    )
