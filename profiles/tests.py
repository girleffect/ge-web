# -*- coding: utf-8 -*-
from datetime import date
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse
from django.http import QueryDict
from django.test import TestCase, Client
from django.contrib.auth.tokens import default_token_generator
from .forms import (
    ForgotPasswordForm,
    RegistrationForm,
    ProfilePasswordChangeForm,
    EditProfileForm,
)
from .models import (
    SecurityQuestion,
    SecurityQuestionAnswer,
    Profile,
    SecurityQuestionIndexPage,
    ProfileSettings,
)
from home.models import HomePage
from articles.models import FooterPage, FooterIndexPage
from wagtail.core.models import Site

from django.contrib.contenttypes.models import ContentType

from wagtail.core.models import Page


class ProfilesTestCaseMixin(object):
    def login(self):
        # Login
        self.client.post("/profiles/login/", {"username": "tester", "password": "0000"})

    def mk_root(self):
        page_content_type, created = ContentType.objects.get_or_create(
            model="page", app_label="wagtailcore"
        )
        self.root, _ = Page.objects.get_or_create(
            title="Root",
            slug="root",
            content_type=page_content_type,
            path="0001",
            depth=1,
            numchild=1,
            url_path="/",
        )

    def setup_cms(self):
        self.mk_root()

        # Create a new homepage
        self.main = HomePage.objects.first()

        # Create index page
        self.index = SecurityQuestionIndexPage(
            title="Security Questions", slug="security-questions"
        )
        self.main.add_child(instance=self.index)
        self.index.save_revision().publish()
        self.footer_index = FooterIndexPage(title="Footers", slug="footers")
        self.main.add_child(instance=self.footer_index)
        self.footer_index.save_revision().publish()
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="0000"
        )

        self.question = SecurityQuestion(
            title="How old are you?", slug="how-old-are-you"
        )
        self.index.add_child(instance=self.question)
        self.question.save_revision().publish()
        self.profile = Profile.objects.create(user=self.user)
        # create answers for this user
        self.a1 = SecurityQuestionAnswer.objects.create(
            user=self.user.profile, question=self.question, answer="20"
        )
        self.footer = FooterPage(title="terms footer", slug="terms-footer")
        self.footer_index.add_child(instance=self.footer)
        self.footer.save_revision().publish()
        self.site = Site.objects.get(is_default_site=True)
        self.profile_settings = ProfileSettings.for_site(self.site)
        self.profile_settings.terms_and_conditions = self.footer
        self.profile_settings.save()
        self.client = Client()


class RegisterTestCase(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_register_username_correct(self):
        form_data = {
            "username": "Jeyabal-1",
            "password": "1234",
            "terms_and_conditions": True,
        }
        form = RegistrationForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_register_username_incorrect(self):
        form_data = {
            "username": "Jeyabal#",
            "password": "1234",
            "terms_and_conditions": True,
        }
        form = RegistrationForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)

    def test_register_password_incorrect(self):
        form_data = {
            "username": "Jeyabal#",
            "password": "12345",
            "terms_and_conditions": True,
        }
        form = RegistrationForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_incorrect(self):
        form_data = {
            "old_password": "123",
            "new_password": "jey123",
            "confirm_password": "jey123",
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_correct(self):
        form_data = {
            "old_password": "1234",
            "new_password": "3456",
            "confirm_password": "3456",
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), True)

    def test_username_exists(self):
        User.objects.create_user("testing", "testing@example.com", "testing")
        form_data = {
            "username": "testing",
            "password": "1234",
        }
        form = RegistrationForm(
            data=form_data,
        )
        self.assertFalse(form.is_valid())
        [validation_error] = form.errors.as_data()["username"]
        self.assertEqual(
            "Sorry, but that is an invalid username. Please don't use your phone number or email address in your username.",
            validation_error.message,
        )

    def test_terms_and_conditions_is_required(self):
        form_data = {
            "username": "test",
            "password": "1234",
        }
        form = RegistrationForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)


class PasswordRecoveryTestCase(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_username_and_security_answer(self):
        form_data = {"username": "tester", "question_0": "20"}
        form = ForgotPasswordForm(
            data=form_data,
            questions=[
                self.question,
            ],
        )
        self.assertEqual(form.is_valid(), True)


class RegistrationViewTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        cache.clear()
        self.setup_cms()

    def test_register_view(self):
        response = self.client.get("/profiles/register/")
        self.assertTrue(isinstance(response.context["form"], RegistrationForm))

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post("/profiles/register/", {})
        self.assertFormError(response, "form", "username", ["This field is required."])
        self.assertFormError(response, "form", "password", ["This field is required."])

    def test_logout(self):
        response = self.client.get(
            "%s?next=%s" % ("/profiles/logout/", "/profiles/register/")
        )
        self.assertRedirects(response, "/profiles/register/")

    def test_email_not_allowed_in_username(self):

        response = self.client.post(
            "/profiles/register/",
            {
                "username": "test@test.com",
                "password": "1234",
                "terms_and_conditions": True,
            },
        )

        expected_validation_message = "Sorry, but that is an invalid username. Please don&#x27;t use your phone number or email address in your username."
        self.assertContains(response, expected_validation_message)

    def test_ascii_code_not_allowed_in_username(self):
        response = self.client.post(
            "/profiles/register/",
            {
                "username": "A bad username 😁",
                "password": "1234",
                "terms_and_conditions": True,
            },
        )

        expected_validation_message = (
            "This value must contain only letters," " numbers and underscores."
        )
        self.assertContains(response, expected_validation_message)

    def test_phone_number_not_allowed_in_username(self):
        response = self.client.post(
            "/profiles/register/",
            {
                "username": "021123123123",
                "password": "1234",
                "terms_and_conditions": True,
            },
        )
        expected_validation_message = "Sorry, but that is an invalid username. Please don&#x27;t use your phone number or email address in your username."

        self.assertContains(response, expected_validation_message)


class RegistrationDone(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()
        self.login()

    def test_gender_on_done(self):
        response = self.client.get("/profiles/register/done/")
        self.assertContains(response, "Let us know more about yourself.")
        self.assertContains(response, "Thank you for joining!")

        response = self.client.post(
            "/profiles/register/done/",
            {
                "gender": "Male",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="tester")
        self.assertEqual(user.profile.gender, ("Male"))

    def test_location_on_done(self):
        response = self.client.get("/profiles/register/done/")
        response = self.client.post(
            "/profiles/register/done/",
            {
                "location": "mlazi",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="tester")
        self.assertEqual(user.profile.location, ("mlazi"))


class TestTermsAndConditions(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_terms_and_conditions_linked_to_terms_and_conditions_page(self):
        response = self.client.get(reverse("user_register"))
        self.assertContains(
            response,
            '<a href="/en/footer-pages/terms-and-conditions/">Terms and Conditions</a>',
        )


class MyProfileViewTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()
        self.user.profile.gender = "The Gender"
        self.user.profile.save()
        self.login()

    def test_view(self):
        response = self.client.get("/profiles/view/myprofile/")
        self.assertContains(response, "tester")
        self.assertContains(response, "The Gender")

        self.assertTrue(
            isinstance(
                response.context["password_change_form"],
                ProfilePasswordChangeForm,
            )
        )


class MyProfileEditTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()
        self.login()

    def test_view(self):
        response = self.client.get("/profiles/edit/myprofile/")
        form = response.context["form"]
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_no_input(self):
        response = self.client.post("/profiles/edit/myprofile/", {})
        self.assertEqual(response.status_code, 302)

    def test_update_dob(self):
        response = self.client.post(
            "/profiles/edit/myprofile/", {"date_of_birth": "2000-01-01"}
        )
        self.assertRedirects(response, "/profiles/view/myprofile/")
        self.assertEqual(
            Profile.objects.get(user=self.user).date_of_birth, date(2000, 1, 1)
        )

    def test_update_gender(self):
        response = self.client.post("/profiles/edit/myprofile/", {"gender": "Female"})
        self.assertRedirects(response, "/profiles/view/myprofile/")
        self.assertEqual(Profile.objects.get(user=self.user).gender, "Female")

    def test_update_location(self):
        response = self.client.post("/profiles/edit/myprofile/", {"location": "mlazi"})
        self.assertRedirects(response, "/profiles/view/myprofile/")
        self.assertEqual(Profile.objects.get(user=self.user).location, "mlazi")


class ProfilePasswordChangeViewTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()
        self.login()

    def test_view(self):
        response = self.client.get(reverse("profile_password_change"))
        form = response.context["form"]
        self.assertTrue(isinstance(form, ProfilePasswordChangeForm))

    def test_update_invalid_old_password(self):
        response = self.client.post(
            reverse("profile_password_change"),
            {
                "old_password": "1234",
                "new_password": "4567",
                "confirm_password": "4567",
            },
        )
        [message] = response.context["messages"]
        self.assertEqual(message.message, "The old password is incorrect.")

    def test_update_passwords_not_matching(self):
        response = self.client.post(
            reverse("profile_password_change"),
            {
                "old_password": "0000",
                "new_password": "1234",
                "confirm_password": "4567",
            },
        )
        form = response.context["form"]
        [error] = form.non_field_errors().as_data()
        self.assertEqual(error.message, "New passwords do not match.")

    def test_update_passwords(self):
        response = self.client.post(
            reverse("profile_password_change"),
            {
                "old_password": "0000",
                "new_password": "1234",
                "confirm_password": "1234",
            },
        )
        self.assertEqual(response["location"], "/profiles/view/myprofile/")
        # Avoid cache by loading from db
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password("1234"))


class ForgotPasswordViewTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_view(self):
        response = self.client.get(reverse("forgot_password"))
        form = response.context["form"]
        self.assertTrue(isinstance(form, ForgotPasswordForm))

    def test_unidentified_user_gets_error(self):
        error_message = "The details you have entered are invalid. Please try again."
        response = self.client.post(
            reverse("forgot_password"),
            {
                "username": "bogus",
                "question_0": "20",
            },
        )
        self.assertContains(response, error_message)

    def test_suspended_user_gets_error(self):
        error_message = (
            "The username and security question(s) combination " "do not match."
        )
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse("forgot_password"),
            {
                "username": "tester",
                "question_0": "20",
            },
        )
        self.assertContains(response, error_message)
        self.user.is_active = True
        self.user.save()

    def test_incorrect_security_answer_gets_error(self):
        error_message = (
            "The username and security question(s) combination " "do not match."
        )
        response = self.client.post(
            reverse("forgot_password"),
            {
                "username": "tester",
                "question_0": "21",
            },
        )
        self.assertContains(response, error_message)

    def test_too_many_retries_result_in_error(self):
        error_message = "Too many attempts"
        profile_settings = ProfileSettings.for_site(self.site)

        # post more times than the set number of retries
        for i in range(profile_settings.password_recovery_retries + 5):
            response = self.client.post(
                reverse("forgot_password"),
                {
                    "username": self.user.username,
                    "question_0": "200",
                },
            )
        self.assertContains(response, error_message)


class ResetPasswordViewTest(TestCase, ProfilesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def proceed_to_reset_password_page(self):
        expected_token = default_token_generator.make_token(self.user)
        expected_query_params = QueryDict(mutable=True)
        expected_query_params["user"] = self.user.username
        expected_query_params["token"] = expected_token
        expected_redirect_url = "{0}?{1}".format(
            reverse("reset_password"), expected_query_params.urlencode()
        )

        return expected_token, expected_redirect_url

    def test_reset_password_view_pin_mismatch(self):
        expected_token, expected_redirect_url = self.proceed_to_reset_password_page()

        response = self.client.post(
            expected_redirect_url,
            {
                "username": self.user.username,
                "token": expected_token,
                "password": "1234",
                "confirm_password": "4321",
            },
        )
        self.assertContains(
            response, "The two PINs that you entered do not " "match. Please try again."
        )

    def test_reset_password_view_invalid_username(self):
        expected_token, expected_redirect_url = self.proceed_to_reset_password_page()

        response = self.client.post(
            expected_redirect_url,
            {
                "username": "invalid",
                "token": expected_token,
                "password": "1234",
                "confirm_password": "1234",
            },
        )

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_inactive_user(self):
        expected_token, expected_redirect_url = self.proceed_to_reset_password_page()

        self.user.is_active = False
        self.user.save()

        response = self.client.get(
            expected_redirect_url,
            {
                "username": self.user.username,
                "token": expected_token,
                "password": "1234",
                "confirm_password": "1234",
            },
        )

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_token(self):
        expected_token, expected_redirect_url = self.proceed_to_reset_password_page()

        response = self.client.get(
            expected_redirect_url,
            {
                "username": self.user.username,
                "token": "invalid",
                "password": "1234",
                "confirm_password": "1234",
            },
        )

        self.assertEqual(403, response.status_code)

    def test_happy_path(self):
        expected_token, expected_redirect_url = self.proceed_to_reset_password_page()

        response = self.client.post(
            expected_redirect_url,
            {
                "username": self.user.username,
                "token": expected_token,
                "password": "1234",
                "confirm_password": "1234",
            },
        )

        self.assertRedirects(response, reverse("reset_password_success"))

        self.assertTrue(self.client.login(username="tester", password="1234"))
