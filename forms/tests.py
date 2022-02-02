from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.core.models import Page

from forms.models import (CustomFormSubmission, FormField, FormPage,
                          FormsIndexPage)


class FormsTestCaseMixin(object):
    def setup_cms(self):
        self.home = Page.objects.get(url_path="/home/")

        # Create index and form pages
        self.index = FormsIndexPage(title="forms", slug="forms")
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()
        self.form = FormPage(title="Check In", slug="health-check")
        self.index.add_child(instance=self.form)
        self.form_field = FormField.objects.create(
            page=self.form,
            label="How are you feeling?",
            field_type="singleline",
            required=True,
        )
        self.form.save_revision().publish()

    def login(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            username="user", email="user@email.com", password="pass"
        )

        # Login
        self.client.login(username="user", password="pass")


class TestAnonymousSubmission(TestCase, FormsTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_anonymous_submissions_not_allowed_by_default(self):
        """
        By default the flag should be False and users who aren't logged
        in shouldn't be able to submit
        """
        self.assertFalse(self.form.allow_anonymous_submissions)

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Please log in to take this form")
        self.assertEqual(CustomFormSubmission.objects.count(), 0)

    def test_anonymous_submissions_allowed(self):
        """
        If the flag is set to True then users who aren't logged in should
        be able to submit
        """
        self.form.allow_anonymous_submissions = True
        self.form.save_revision().publish()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)

    def test_multiple_anonymous_submissions_allowed(self):
        """
        If the flag is set to True then multiple users who aren't logged
        in should be able to submit
        """
        self.form.allow_anonymous_submissions = True
        self.form.save_revision().publish()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "bad"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 2)

    def test_logged_in_submissions_still_allowed(self):
        self.form.allow_anonymous_submissions = True
        self.form.save_revision().publish()

        self.login()
        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)


class TestMultipleSubmission(TestCase, FormsTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_multiple_submissions_not_allowed_by_default(self):
        """
        By default the flag should be False and users should only be able
        to submit once
        """
        self.assertFalse(self.form.allow_multiple_submissions_per_user)
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "You can fill in the from only one time.")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)

    def test_multiple_submissions_allowed(self):
        """
        If the flag is set to True then users should be able to submit multiple
        times
        """
        self.form.allow_multiple_submissions_per_user = True
        self.form.save_revision().publish()
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 2)


class TestShowResults(TestCase, FormsTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_show_results_off_by_default(self):
        """
        By default the user shouldn't be shown the results on form
        submission
        """
        self.assertFalse(self.form.show_results)
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertNotContains(response, "Results")

    def test_show_results_on(self):
        """
        If the flag is set to True then users should be shown the
        results on form submission
        """
        self.form.show_results = True
        self.form.save_revision().publish()
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertContains(response, "Results")
        self.assertContains(response, "well")


class TestCustomFormSubmission(TestCase, FormsTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_username_added_to_submission(self):
        """
        The username of the user submitting the form should be added
        to the submission data
        """
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )

        self.assertEqual(CustomFormSubmission.objects.count(), 1)
        submission = CustomFormSubmission.objects.first().get_data()
        self.assertEqual(submission["username"], "user")


class TestMultiStepForm(TestCase, FormsTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_multi_step_forms_serve_one_page_per_question(self):
        """
        Failing
        If the flag is set then forms should be served to the user one
        question at a time
        """
        field2 = FormField.objects.create(
            page=self.form,
            label="How much water have you drunk?",
            field_type="radio",
            choices=[
                "less than 1 glass",
                "1 - 3 glasses",
                "2 litres",
                "more than 2 litres",
            ],
            required=True,
        )
        field3 = FormField.objects.create(
            page=self.form,
            label="What did you eat today?",
            field_type="singleline",
            required=True,
        )
        self.form.save_revision().publish()
        self.login()

        response = self.client.get("/en/forms/health-check/")
        self.assertContains(response, self.form.title)
        self.assertContains(response, self.form_field.label)
        self.assertNotContains(response, field2.label)
        self.assertNotContains(response, field3.label)

        response = self.client.post(
            "/en/forms/health-check/",
            {"how_are_you_feeling": "well"},
            follow=True,
        )
        self.assertContains(response, self.form.title)
        self.assertNotContains(response, self.form_field.label)
        self.assertContains(response, field2.label)
        self.assertNotContains(response, field3.label)

        response = self.client.post(
            "/en/forms/health-check/",
            {"how_much_water_have_you_drunk": "less than 1 glass"},
            follow=True,
        )
        self.assertContains(response, self.form.title)
        self.assertNotContains(response, self.form_field.label)
        self.assertNotContains(response, field2.label)
        self.assertContains(response, field3.label)

        response = self.client.post(
            "/en/forms/health-check/",
            {"what_did_you_eat_today": "not enough"},
            follow=True,
        )
        self.assertContains(response, self.form.title)
        self.assertContains(response, "Thank you")
        self.assertEqual(CustomFormSubmission.objects.count(), 1)
