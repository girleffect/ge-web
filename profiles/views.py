from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.http.request import QueryDict
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wagtail.core.models import Site

from . import forms
from .models import SecurityQuestionAnswer, GEUser, GEUserSettings, SecurityQuestion


class RegistrationView(FormView):
    """
    Handles user registration
    """

    form_class = forms.RegistrationForm
    template_name = "profiles/register.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        if User.objects.filter(username=username).exists():
            messages.error(self.request, _("Username is already taken"))
            return render(self.request, self.template_name, {"form": form})

        user = User.objects.create_user(username=username, password=password)
        GEUser.objects.create(user=user)

        for index, question in enumerate(self.questions):
            answer = form.cleaned_data.get("question_%s" % index)
            if answer:
                SecurityQuestionAnswer.objects.create(
                    user=user.geuser, question=question, answer=answer
                )
        authed_user = authenticate(
            request=self.request, username=username, password=password
        )
        login(self.request, authed_user)
        return HttpResponseRedirect(
            form.cleaned_data.get("next", "/profiles/register/done/")
        )

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        site = Site.find_for_request(self.request)
        self.questions = (
            SecurityQuestion.objects.descendant_of(site.root_page).live().filter()
        )
        kwargs["questions"] = self.questions
        kwargs["request"] = self.request
        return kwargs


class RegistrationDone(LoginRequiredMixin, FormView):
    form_class = forms.DoneForm
    template_name = "profiles/done.html"

    def form_valid(self, form):
        profile = self.request.user.geuser
        profile.date_of_birth = form.cleaned_data["date_of_birth"]
        profile.gender = form.cleaned_data["gender"]
        profile.location = form.cleaned_data["location"]
        profile.save()
        return HttpResponseRedirect(form.cleaned_data.get("next", "/"))


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get("next", "/"))


class MyProfileView(LoginRequiredMixin, TemplateView):
    """
    Enables viewing of the user's profile in the HTML site, by the profile
    owner.
    """

    template_name = "profiles/viewprofile.html"

    def get_context_data(self, **kwargs):
        context = super(MyProfileView, self).get_context_data(**kwargs)
        context["password_change_form"] = forms.ProfilePasswordChangeForm()
        return context


class MyProfileEdit(LoginRequiredMixin, UpdateView):
    model = GEUser
    form_class = forms.EditProfileForm
    template_name = "profiles/editprofile.html"
    success_url = "/profiles/view/myprofile/"

    def get_object(self, queryset=None):
        return self.request.user.geuser


class ProfilePasswordChangeView(LoginRequiredMixin, FormView):
    form_class = forms.ProfilePasswordChangeForm
    template_name = "profiles/change_password.html"

    def form_valid(self, form):
        user = self.request.user
        if user.check_password(form.cleaned_data["old_password"]):
            user.set_password(form.cleaned_data["new_password"])
            user.save()
            return HttpResponseRedirect("/profiles/view/myprofile/")
        messages.error(self.request, _("The old password is incorrect."))
        return render(self.request, self.template_name, {"form": form})


class ForgotPasswordView(FormView):
    form_class = forms.ForgotPasswordForm
    template_name = "profiles/forgot_password.html"

    def form_valid(self, form):
        site = Site.find_for_request(self.request)
        error_message = (
            "The username and security question(s) combination do not match."
        )
        profile_settings = GEUserSettings.for_site(site)

        if "forgot_password_attempts" not in self.request.session:
            self.request.session[
                "forgot_password_attempts"
            ] = profile_settings.password_recovery_retries

        # max retries exceeded
        if self.request.session["forgot_password_attempts"] <= 0:
            form.add_error(None, _("Too many attempts. Please try again later."))
            return self.render_to_response({"form": form})
        username = form.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.request.session["forgot_password_attempts"] += 1
            form.add_error(
                "username",
                _(
                    "The username that you entered appears to be "
                    "invalid. Please try again."
                ),
            )
            return self.render_to_response({"form": form})

        if not user.is_active:
            # add non_field_error
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({"form": form})

        # check security question answers
        answer_checks = []
        for i in range(profile_settings.num_security_questions):
            user_answer = form.cleaned_data.get("question_%s" % (i,))
            try:
                saved_answer = SecurityQuestionAnswer.objects.get(
                    user=user.geuser, question=self.security_questions[i]
                )
                answer_checks.append(saved_answer.check_answer(user_answer))
            except SecurityQuestionAnswer.DoesNotExist:
                form.add_error(
                    None,
                    _(
                        "There are no security questions "
                        "stored against your profile."
                    ),
                )
                return self.render_to_response({"form": form})

        # redirect to reset password page if username and security
        # questions were matched
        if all(answer_checks):
            token = default_token_generator.make_token(user)
            q = QueryDict(mutable=True)
            q["user"] = username
            q["token"] = token
            reset_password_url = "{0}?{1}".format(
                "/profiles/reset-password/", q.urlencode()
            )
            return HttpResponseRedirect(reset_password_url)
        else:
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({"form": form})

    def get_form_kwargs(self):
        # add security questions for form field generation
        # the security questions should be a random subset of
        # all the questions the user has answered
        site = Site.find_for_request(self.request)
        kwargs = super(ForgotPasswordView, self).get_form_kwargs()
        profile_settings = GEUserSettings.for_site(site)
        self.security_questions = SecurityQuestion.objects.descendant_of(
            site.root_page
        ).live()

        kwargs["questions"] = self.security_questions[
            : profile_settings.num_security_questions
        ]
        self.security_questions = self.security_questions[
            : profile_settings.num_security_questions
        ]
        return kwargs


class ResetPasswordView(FormView):
    form_class = forms.ResetPasswordForm
    template_name = "profiles/reset_password.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        token = form.cleaned_data["token"]

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        if not user.is_active:
            return HttpResponseForbidden()

        if not default_token_generator.check_token(user, token):
            return HttpResponseForbidden()

        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirm_password"]

        if password != confirm_password:
            form.add_error(
                None,
                _("The two PINs that you entered do not match. " "Please try again."),
            )
            return self.render_to_response({"form": form})

        user.set_password(password)
        user.save()
        self.request.session.flush()

        return HttpResponseRedirect("/profiles/reset-success/")

    def render_to_response(self, context, **response_kwargs):
        username = self.request.GET.get("user")
        token = self.request.GET.get("token")

        if not username or not token:
            return HttpResponseForbidden()

        context["form"].initial.update({"username": username, "token": token})

        return super(ResetPasswordView, self).render_to_response(
            context, **response_kwargs
        )
