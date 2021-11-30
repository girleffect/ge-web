from . import views

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    path("logout/", views.logout_page, name="auth_logout"),
    # If user is not login it will redirect to login page
    path("login/", auth_views.LoginView.as_view(), name="auth_login"),
    path("register/", views.RegistrationView.as_view(), name="user_register"),
    path(
        "register/done/",
        views.RegistrationDone.as_view(template_name="profiles/done.html"),
        name="registration_done",
    ),
    path("view/myprofile/", views.MyProfileView.as_view(), name="view_my_profile"),
    path("edit/myprofile/", views.MyProfileEdit.as_view(), name="edit_my_profile"),
    path(
        "password-reset/",
        views.ProfilePasswordChangeView.as_view(),
        name="profile_password_change",
    ),
    path(
        "forgot-password/",
        views.ForgotPasswordView.as_view(),
        name="forgot_password",
    ),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path(
        "reset-success/",
        TemplateView.as_view(template_name="profiles/reset_password_success.html"),
        name="reset_password_success",
    ),
    path(
        "login-success/",
        TemplateView.as_view(template_name="profiles/login_success.html"),
        name="login_success",
    ),
]
