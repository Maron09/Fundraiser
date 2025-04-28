from django.urls import path
from authentication.views import UserRegistrationView, VerifyEmailView, RequestNewOTPView, LoginView, LogoutView, PasswordResetRequestView, PasswordResetView



urlpatterns = [
    path("auth/register/", UserRegistrationView.as_view()),
    path("auth/verify-email/", VerifyEmailView.as_view()),
    path("auth/request-new-otp/", RequestNewOTPView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/request-password-reset/", PasswordResetRequestView.as_view()),
    path("auth/reset-password/", PasswordResetView.as_view()),
]
