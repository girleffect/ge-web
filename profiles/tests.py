# -*- coding: utf-8 -*-
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from .forms import (
    ForgotPasswordForm, RegistrationForm, ProfilePasswordChangeForm, DoneForm)
from .models import (SecurityQuestion, SecurityQuestionIndexPage,
                                  GEUserSettings)

from wagtail.core.models import Site


class RegisterTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='tester')

    def test_register_username_correct(self):
        form_data = {
            'username': 'Jeyabal@-1',
            'password': '1234',
            'terms_and_conditions': True
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)

    def test_register_username_incorrect(self):
        form_data = {
            'username': 'Jeyabal#',
            'password': '1234',
            'terms_and_conditions': True

        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)

    def test_register_password_incorrect(self):
        form_data = {
            'username': 'Jeyabal#',
            'password': '12345',
            'terms_and_conditions': True

        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_incorrect(self):
        form_data = {
            'old_password': '123',
            'new_password': 'jey123',
            'confirm_password': 'jey123',
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), False)

    def test_password_change_correct(self):
        form_data = {
            'old_password': '1234',
            'new_password': '3456',
            'confirm_password': '3456',
        }
        form = ProfilePasswordChangeForm(
            data=form_data,
        )
        self.assertEqual(form.is_valid(), True)

    def test_username_exists(self):
        User.objects.create_user(
            'testing', 'testing@example.com', 'testing')
        form_data = {
            'username': 'testing',
            'password': '1234',
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertFalse(form.is_valid())
        [validation_error] = form.errors.as_data()['username']
        self.assertEqual(
            'Username already exists.', validation_error.message)

    def test_terms_and_conditions_is_required(self):
        form_data = {
            'username': 'test',
            'password': '1234',
        }
        form = RegistrationForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), False)


class PasswordRecoveryTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_username_and_security_answer(self):
        form_data = {
            "username": "tester",
            "question_0": "20"
        }
        form = ForgotPasswordForm(
            data=form_data,
            questions=[self.question, ]
        )
        self.assertEqual(form.is_valid(), True)


# -*- coding: utf-8 -*-
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator

from django.urls import reverse
from django.http import QueryDict
from django.test import TestCase, override_settings, Client

from .forms import (
    RegistrationForm, EditProfileForm,
    ProfilePasswordChangeForm, ForgotPasswordForm)
from .models import (
    SecurityQuestion, SecurityAnswer,
    UserProfile, SecurityQuestionIndexPage, UserProfilesSettings
)
from wagtail.core.models import Site


class RegistrationViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        cache.clear()
        self.mk_main()
        self.client = Client()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.security_index2 = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions_2',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.main2.add_child(instance=self.security_index2)
        self.security_index2.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_register_view(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertTrue(isinstance(response.context['form'], RegistrationForm))

    def test_password_auto_complete(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'autocomplete="off"')

        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'autocomplete="off"')

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('molo.profiles:user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])

    def test_logout(self):
        response = self.client.get('%s?next=%s' % (
            reverse('molo.profiles:auth_logout'),
            reverse('molo.profiles:user_register')))
        self.assertRedirects(response, reverse('molo.profiles:user_register'))

    def test_login(self):
        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'Forgotten your password?')

    def test_email_or_phone_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        expected_validation_message = "Sorry, but that is an invalid " \
                                      "username. Please don&#x27;t use " \
                                      "your phone number or email address " \
                                      "in your username."

        self.assertContains(response, expected_validation_message)

    def test_email_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#x27;t use" \
                                      " your email address in your" \
                                      " username."

        self.assertContains(response, expected_validation_message)

    def test_ascii_code_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'A bad username 😁',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "This value must contain only letters,"\
                                      " numbers and underscores."
        self.assertContains(response, expected_validation_message)

    def test_phone_number_not_allowed_in_username(self):
        site = Site.objects.first()
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': '021123123123',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#x27;t use" \
                                      " your phone number in your username."

        self.assertContains(response, expected_validation_message)

    def test_security_questions(self):
        # setup for site 1
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        sq = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
        )
        self.security_index.add_child(instance=sq)
        sq.save()
        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = True
        profile_settings.save()

        # setup for site 2
        profile_settings2 = UserProfilesSettings.for_site(
            self.main2.get_site())
        sq2 = SecurityQuestion(
            title="Who are you?",
            slug="who-are-you",
        )
        self.security_index2.add_child(instance=sq2)
        sq2.save()
        profile_settings2.show_security_question_fields = True
        profile_settings2.security_questions_required = True
        profile_settings2.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, "What is your name")
        self.assertNotContains(response, "Who are you")

        # register with security questions
        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "answer",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        client = Client(HTTP_HOST=self.site2.hostname)
        response = client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, "What is your name")
        self.assertContains(response, "Who are you")

        # register with security questions
        response = client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "answer",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class RegistrationDone(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.mk_main2()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_correct_fields_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.date_of_birth, date(2000, 1, 1))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # test not required for site 2
        profile_settings2 = UserProfilesSettings.for_site(
            self.main2.get_site())
        profile_settings2.activate_dob = False
        profile_settings2.save()
        client = Client(HTTP_HOST=self.main2.get_site().hostname)
        client.post('/profiles/register/', {
            'username': 'testing2',
            'password': '1234',
            'terms_and_conditions': True

        })
        response = client.get(reverse('molo.profiles:registration_done'))
        self.assertNotContains(response, "SELECT DATE OF BIRTH")

    def test_gender_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'gender': 'male',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.gender, ('male'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_location_on_done(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, 'Let us know more about yourself '
                            'to get access to exclusive content.')
        self.assertContains(response, 'Thank you for joining!')
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'location': 'mlazi',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.location, ('mlazi'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TestTermsAndConditions(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.footer = FooterPage(
            title='terms and conditions', slug='terms-and-conditions')
        self.footer_index.add_child(instance=self.footer)
        self.footer.save()
        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_terms_and_conditions_linked_to_terms_and_conditions_page(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(
            response,
            '<a href="/footer-pages/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')
        self.assertContains(
            response,
            '<label for="id_terms_and_conditions"'
            ' class="profiles__terms">'
            'I accept the Terms and Conditions</label>')

        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        profile_settings.terms_and_conditions = self.footer
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(
            response,
            '<a href="/footers-main-1/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')


class MyProfileViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()

    def test_view(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'tester')
        self.assertContains(response, 'The Alias')

        self.assertTrue(isinstance(
            response.context['password_change_form'],
            ProfilePasswordChangeForm,
        ))

class LoginTestView(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='1234')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()

    def test_login_success(self):
        self.client.login(username='tester', password='1234')

        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'value="/profiles/login-success/"')

        response = self.client.get(reverse('molo.profiles:login_success'))
        self.assertContains(response, 'Welcome Back!')

    def test_login_success_redirects(self):
        self.client.login(username='tester', password='1234')

        response = self.client.post(
            reverse('molo.profiles:auth_login'),
            data={'username': 'tester', 'password': '1234',
                  'next': '/profiles/login-success/'},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse('molo.profiles:login_success'))


class MyProfileEditTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.mk_main2()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_view(self):
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_no_input(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {})
        self.assertEqual(response.status_code, 302)

    def test_update_dob(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
        {
            'date_of_birth': '2000-01-01'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).date_of_birth,
                         date(2000, 1, 1))

    def test_update_gender(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_gender = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).gender,
                         'male')

    def test_update_location(self):
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)
        profile_settings.activate_location = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': 'mlazi'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).location,
                         'mlazi')

class ProfilePasswordChangeViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='0000')
        self.client = Client()
        self.client.login(username='tester', password='0000')

    def test_view(self):
        response = self.client.get(
            reverse('molo.profiles:profile_password_change'))
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfilePasswordChangeForm))

    def test_update_invalid_old_password(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '1234',
                'new_password': '4567',
                'confirm_password': '4567',
            })
        [message] = response.context['messages']
        self.assertEqual(message.message, 'The old password is incorrect.')

    def test_update_passwords_not_matching(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '4567',
            })
        form = response.context['form']
        [error] = form.non_field_errors().as_data()
        self.assertEqual(error.message, 'New passwords do not match.')

    def test_update_passwords(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '1234',
            })
        self.assertEqual(response['location'], '/profiles/view/myprofile/')
        # Avoid cache by loading from db
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password('1234'))


class ForgotPasswordViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=self.question, answer="20"
        )

    def test_view(self):
        response = self.client.get(
            reverse("molo.profiles:forgot_password"))
        form = response.context["form"]
        self.assertTrue(isinstance(form, ForgotPasswordForm))

    def test_unidentified_user_gets_error(self):
        error_message = ("The username that you entered appears to be invalid."
                         " Please try again.")
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "bogus",
                "question_0": "20",
            }
        )
        self.assertContains(response, error_message)

    def test_suspended_user_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            }
        )
        self.assertContains(response, error_message)
        self.user.is_active = True
        self.user.save()

    def test_incorrect_security_answer_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "21",
            }
        )
        self.assertContains(response, error_message)

    def test_too_many_retries_result_in_error(self):
        error_message = ("Too many attempts")
        site = Site.objects.get(is_default_site=True)
        profile_settings = UserProfilesSettings.for_site(site)

        # post more times than the set number of retries
        for i in range(profile_settings.password_recovery_retries + 5):
            response = self.client.post(
                reverse("molo.profiles:forgot_password"), {
                    "username": self.user.username,
                    "question_0": "200",
                }
            )
        self.assertContains(response, error_message)

    def test_correct_username_and_answer_results_in_redirect(self):
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            },
            follow=True
        )
        self.assertContains(response, "Reset PIN")

    def test_user_with_no_security_questions(self):
        # register without security questions
        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "newuser",
                "password": "0000",
                'terms_and_conditions': True
            },
            follow=True
        )
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        sq = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
        )
        self.security_index.add_child(instance=sq)
        sq.save()

        sq2 = SecurityQuestion(
            title="What is your pet name?",
            slug="what-is-your-pet-name",
        )
        self.security_index.add_child(instance=sq2)
        sq2.save()

        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = False
        profile_settings.save()

        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "newuser",
                "question_0": "saeed",
                "question_1": "pishy",
            }
        )
        self.assertContains(
            response,
            "There are no security questions"
            " stored against your profile.")


class ResetPasswordViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")

        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=self.question, answer="20"
        )

    def proceed_to_reset_password_page(self):
        expected_token = default_token_generator.make_token(self.user)
        expected_query_params = QueryDict(mutable=True)
        expected_query_params["user"] = self.user.username
        expected_query_params["token"] = expected_token
        expected_redirect_url = "{0}?{1}".format(
            reverse("molo.profiles:reset_password"),
            expected_query_params.urlencode()
        )

        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": self.user.username,
                "question_0": "20",
            }
        )
        self.assertRedirects(response, expected_redirect_url)

        return expected_token, expected_redirect_url

    def test_reset_password_view_pin_mismatch(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "4321"
        })
        self.assertContains(response, "The two PINs that you entered do not "
                                      "match. Please try again.")

    def test_reset_password_view_invalid_username(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": "invalid",
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_inactive_user(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        self.user.is_active = False
        self.user.save()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_token(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": "invalid",
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_happy_path(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertRedirects(
            response,
            reverse("molo.profiles:reset_password_success")
        )

        self.assertTrue(
            self.client.login(username="tester", password="1234")
        )
