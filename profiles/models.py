from django.db import models
from django.contrib.auth.models import User
from wagtail.core.models import Page
from wagtail.contrib.settings.models import BaseSetting, register_setting
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import hashers
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel


class GEUser(models.Model):
    class Gender(models.TextChoices):
        FEMALE = _("Female")
        MALE = _("Male")
        TRANSGENDER = _("Transgender")
        NON_CONFORMING_NON_BINARY = _("Non-conforming/Non-binary")
        OTHER = _("Other")
        NOT_GIVEN = _("Not comfortable sharing")

    gender = models.CharField(
        max_length=50,
        choices=Gender.choices,
        null=True,
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=128, blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    terms_and_conditions = models.BooleanField(default=False)
    user_questions = models.ManyToManyField(
        "profiles.SecurityQuestion", through="SecurityQuestionAnswer"
    )


class SecurityQuestionIndexPage(Page):
    subpage_types = ["profiles.SecurityQuestion"]
    parent_page_type = ["home.HomePage"]


class SecurityQuestion(Page):
    parent_page_type = ["profiles.SecurityQuestionIndexPage"]


class SecurityQuestionAnswer(models.Model):
    user = models.ForeignKey("profiles.GEUser", on_delete=models.CASCADE)
    question = models.ForeignKey("profiles.SecurityQuestion", on_delete=models.CASCADE)
    answer = models.CharField(max_length=250, null=False)

    def set_answer(self, raw_answer):
        self.answer = hashers.make_password(raw_answer.strip().lower())

    def check_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_answer(raw_answer)
            self.save(update_fields=["answer"])

        return hashers.check_password(
            raw_answer.strip().lower() if raw_answer else None, self.answer, setter
        )

    def save(self, is_import=False, *args, **kwargs):
        # checks if this save is coming from an import so we don't hash a hash
        if not is_import and not self.id:
            self.set_answer(self.answer)
        super(SecurityQuestionAnswer, self).save(*args, **kwargs)


@register_setting
class GEUserSettings(BaseSetting):
    prevent_phone_number_in_username = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Prevent phone number in username / display name"),
    )

    prevent_email_in_username = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Prevent email in username / display name"),
    )

    num_security_questions = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Number of security questions asked for " "password recovery"),
    )
    password_recovery_retries = models.PositiveSmallIntegerField(
        default=5,
        verbose_name=_("Max number of password recovery retries before " "lockout"),
    )
    terms_and_conditions = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Choose a footer page"),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("num_security_questions"),
                FieldPanel("password_recovery_retries"),
            ],
            heading="Security Question Settings",
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("terms_and_conditions"),
            ],
            heading="Terms and Conditions on registration",
        ),
    ]
