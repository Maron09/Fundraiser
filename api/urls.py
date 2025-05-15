from django.urls import path
from authentication.views import UserRegistrationView, VerifyEmailView, RequestNewOTPView, LoginView, LogoutView, PasswordResetRequestView, PasswordResetView
from users.views import UserProfileView
from campaign.views import CategoryListView, CampaignListView, CampaignDetailView

from accounts.views import PaystackBankListView



urlpatterns = [
    # Auth
    path("auth/register/", UserRegistrationView.as_view()),
    path("auth/verify-email/", VerifyEmailView.as_view()),
    path("auth/request-new-otp/", RequestNewOTPView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/request-password-reset/", PasswordResetRequestView.as_view()),
    path("auth/reset-password/", PasswordResetView.as_view()),
    
    # Users
    path("users/profile/", UserProfileView.as_view()),
    
    # Category
    path("categories/", CategoryListView.as_view()),
    
    # Campaign
    path("campaigns/", CampaignListView.as_view()),
    path("campaign/<str:slug>/", CampaignDetailView.as_view()),
    
    # Accounts
    path("accounts/banks/", PaystackBankListView.as_view()),
]
