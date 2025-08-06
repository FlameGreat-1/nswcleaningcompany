from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerificationView,
    ResendVerificationView,
    ClientProfileView,
    AddressListCreateView,
    AddressDetailView,
    UserDeactivationView,
    UserListView,
    UserDetailView,
    UserStatsView,
    BulkUserActionView,
    GoogleAuthView,
    GoogleRegistrationView,
    SocialLoginView,
    AccountLinkingView,
    AccountUnlinkingView,
    SocialProfileListView,
    SocialProfileDetailView,
    user_dashboard,
    cleanup_expired_tokens,
    refresh_social_tokens,
    social_auth_stats,
    health_check,
)

app_name = "accounts"

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("auth/register/", UserRegistrationView.as_view(), name="register"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("auth/google/", GoogleAuthView.as_view(), name="google_auth"),
    path(
        "auth/google/register/",
        GoogleRegistrationView.as_view(),
        name="google_register",
    ),
    path("auth/social/login/", SocialLoginView.as_view(), name="social_login"),
    path("auth/password/change/", PasswordChangeView.as_view(), name="password_change"),
    path(
        "auth/password/reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/email/verify/", EmailVerificationView.as_view(), name="email_verify"),
    path(
        "auth/email/resend/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/client/", ClientProfileView.as_view(), name="client_profile"),
    path(
        "profile/deactivate/", UserDeactivationView.as_view(), name="user_deactivation"
    ),
    path(
        "profile/social/", SocialProfileListView.as_view(), name="social_profile_list"
    ),
    path(
        "profile/social/<int:pk>/",
        SocialProfileDetailView.as_view(),
        name="social_profile_detail",
    ),
    path("profile/social/link/", AccountLinkingView.as_view(), name="account_linking"),
    path(
        "profile/social/unlink/",
        AccountUnlinkingView.as_view(),
        name="account_unlinking",
    ),
    path("addresses/", AddressListCreateView.as_view(), name="address_list_create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address_detail"),
    path("dashboard/", user_dashboard, name="user_dashboard"),
    path("admin/users/", UserListView.as_view(), name="user_list"),
    path("admin/users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("admin/users/stats/", UserStatsView.as_view(), name="user_stats"),
    path(
        "admin/users/bulk-action/",
        BulkUserActionView.as_view(),
        name="bulk_user_action",
    ),
    path("admin/cleanup/", cleanup_expired_tokens, name="cleanup_expired_tokens"),
    path(
        "admin/social/refresh-tokens/",
        refresh_social_tokens,
        name="refresh_social_tokens",
    ),
    path("admin/social/stats/", social_auth_stats, name="social_auth_stats"),
]

api_v1_patterns = [
    path("v1/accounts/", include(urlpatterns)),
]
