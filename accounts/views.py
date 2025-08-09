from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from datetime import timedelta
from .models import (
    User,
    ClientProfile,
    Address,
    EmailVerification,
    PasswordReset,
    UserSession,
    SocialAuthProfile,
)
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    AddressSerializer,
    ClientProfileSerializer,
    ClientProfileUpdateSerializer,
    UserDeactivationSerializer,
    ResendVerificationSerializer,
    UserStatsSerializer,
    BulkUserActionSerializer,
    UserListSerializer,
    GoogleAuthSerializer,
    GoogleRegistrationSerializer,
    SocialLoginSerializer,
    SocialAuthProfileSerializer,
    AccountLinkingSerializer,
    AccountUnlinkingSerializer,
)
from .permissions import (
    IsOwner,
    IsOwnerOrStaff,
    IsClientUser,
    IsNDISClient,
    IsAdminUser,
    IsStaffOrAdmin,
    IsVerifiedUser,
    CanManageUsers,
    CanAccessClientProfile,
    CanModifyAddress,
    IsUnauthenticated,
    CanResetPassword,
    CanVerifyEmail,
    CanAccessAdminDashboard,
    CanBulkManageUsers,
    NDISCompliancePermission,
)
from .utils import (
    send_verification_email,
    send_password_reset_email,
    send_welcome_email,
    send_password_changed_email,
    send_social_account_linked_email,
    send_social_account_unlinked_email,
    send_login_notification_email,
    send_profile_completion_reminder,
    send_account_locked_email,
    get_client_ip,
)
from .google_auth import GoogleOAuthHandler
from .social_auth import SocialAuthBackend


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data["access_token"]
            user_type = serializer.validated_data.get("user_type", "client")
            client_type = serializer.validated_data.get("client_type", "general")

            google_handler = GoogleOAuthHandler()
            google_user_data = google_handler.get_user_info(access_token)

            if not google_user_data:
                return Response(
                    {"error": "Invalid Google access token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(email=google_user_data["email"])
                if not user.is_google_user:
                    return Response(
                        {
                            "error": "Email already exists with different authentication method"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found. Please register first."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not user.is_active:
                return Response(
                    {"error": "User account is disabled"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            social_profile, created = SocialAuthProfile.objects.get_or_create(
                user=user,
                provider="google",
                defaults={
                    "provider_id": google_user_data["id"],
                    "provider_email": google_user_data["email"],
                    "access_token": access_token,
                    "profile_data": google_user_data,
                },
            )

            if not created:
                social_profile.access_token = access_token
                social_profile.profile_data = google_user_data
                social_profile.save()

            token, created = Token.objects.get_or_create(user=user)

            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            UserSession.objects.create_session(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            send_login_notification_email(user, ip_address, user_agent, "google")

            return Response(
                {
                    "message": "Google authentication successful",
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "user_type": user.user_type,
                        "client_type": user.client_type,
                        "is_verified": user.is_verified,
                        "is_google_user": user.is_google_user,
                        "avatar_url": user.avatar_url,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data["access_token"]
            user_type = serializer.validated_data.get("user_type", "client")
            client_type = serializer.validated_data.get("client_type", "general")
            phone_number = serializer.validated_data.get("phone_number", "")

            google_handler = GoogleOAuthHandler()
            google_user_data = google_handler.get_user_info(access_token)

            if not google_user_data:
                return Response(
                    {"error": "Invalid Google access token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects.filter(email=google_user_data["email"]).exists():
                return Response(
                    {"error": "User with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                user = User.objects.create_user(
                    email=google_user_data["email"],
                    first_name=google_user_data.get("given_name", ""),
                    last_name=google_user_data.get("family_name", ""),
                    phone_number=phone_number,
                    user_type=user_type,
                    client_type=client_type,
                    auth_provider="google",
                    google_id=google_user_data["id"],
                    avatar_url=google_user_data.get("picture", ""),
                    is_verified=True,
                )

                user.set_unusable_password()
                user.save()

                SocialAuthProfile.objects.create(
                    user=user,
                    provider="google",
                    provider_id=google_user_data["id"],
                    provider_email=google_user_data["email"],
                    access_token=access_token,
                    profile_data=google_user_data,
                )

                send_welcome_email(user)

                token, created = Token.objects.get_or_create(user=user)

                return Response(
                    {
                        "message": "Google registration successful",
                        "user_id": user.id,
                        "email": user.email,
                        "token": token.key,
                        "user_type": user.user_type,
                        "is_verified": user.is_verified,
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SocialLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            provider = serializer.validated_data["provider"]
            access_token = serializer.validated_data["access_token"]

            social_backend = SocialAuthBackend()
            user = social_backend.authenticate_social_user(provider, access_token)

            if not user:
                return Response(
                    {"error": "Social authentication failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not user.is_active:
                return Response(
                    {"error": "User account is disabled"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token, created = Token.objects.get_or_create(user=user)

            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            UserSession.objects.create_session(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            send_login_notification_email(user, ip_address, user_agent, provider)

            return Response(
                {
                    "message": "Social login successful",
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "user_type": user.user_type,
                        "client_type": user.client_type,
                        "auth_provider": user.auth_provider,
                        "is_verified": user.is_verified,
                        "avatar_url": user.avatar_url,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountLinkingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountLinkingSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            provider = serializer.validated_data["provider"]
            access_token = serializer.validated_data["access_token"]

            social_backend = SocialAuthBackend()
            provider_data = social_backend.get_provider_user_data(
                provider, access_token
            )

            if not provider_data:
                return Response(
                    {"error": f"Invalid {provider} access token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                User.objects.filter(email=provider_data["email"])
                .exclude(id=request.user.id)
                .exists()
            ):
                return Response(
                    {"error": "This social account is already linked to another user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            social_profile, created = SocialAuthProfile.objects.get_or_create(
                user=request.user,
                provider=provider,
                defaults={
                    "provider_id": provider_data["id"],
                    "provider_email": provider_data["email"],
                    "access_token": access_token,
                    "profile_data": provider_data,
                },
            )

            if not created:
                social_profile.access_token = access_token
                social_profile.profile_data = provider_data
                social_profile.is_active = True
                social_profile.save()

            send_social_account_linked_email(request.user, provider)

            return Response(
                {
                    "message": f"{provider.title()} account linked successfully",
                    "social_profile": SocialAuthProfileSerializer(social_profile).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountUnlinkingView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountUnlinkingSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            provider = serializer.validated_data["provider"]

            social_profile = SocialAuthProfile.objects.get(
                user=request.user, provider=provider, is_active=True
            )

            social_profile.is_active = False
            social_profile.save()

            send_social_account_unlinked_email(request.user, provider)

            return Response(
                {"message": f"{provider.title()} account unlinked successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        # Add debug logging here
        logger.error(f"=== REGISTRATION DEBUG ===")
        logger.error(f"Request data: {request.data}")
        logger.error(f"Content-Type: {request.content_type}")

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            logger.error("Serializer is valid, proceeding with user creation")
            with transaction.atomic():
                user = serializer.save()

                verification = EmailVerification.objects.create_verification(user)
                send_verification_email(user, verification.token)
                send_welcome_email(user, verification.token)

                token, created = Token.objects.get_or_create(user=user)

                response_data = {
                    "success": True,  # ✅ Added this field
                    "data": {  # ✅ Wrapped everything in 'data'
                        "message": "Registration successful. Please check your email for verification.",
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "user_type": user.user_type,
                            "is_verified": user.is_verified,
                        },
                        "token": token.key,
                        "requires_verification": True,
                    },
                }

                # 🔍 DEBUG: Log the exact response being sent
                logger.error(f"🔍 RESPONSE DEBUG - Sending response: {response_data}")

                return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # Add detailed error logging
            logger.error(f"Serializer validation failed!")
            logger.error(f"Validation errors: {serializer.errors}")
            for field, errors in serializer.errors.items():
                logger.error(f"Field '{field}' errors: {errors}")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            token, created = Token.objects.get_or_create(user=user)

            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            UserSession.objects.create_session(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            send_login_notification_email(user, ip_address, user_agent, "email")

            return Response(
                {
                    "message": "Login successful",
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "user_type": user.user_type,
                        "client_type": user.client_type,
                        "auth_provider": user.auth_provider,
                        "is_verified": user.is_verified,
                        "is_ndis_client": user.is_ndis_client,
                        "is_google_user": user.is_google_user,
                        "avatar_url": user.avatar_url,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.deactivate_session(session_key)

            request.user.auth_token.delete()
            logout(request)

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            old_data = {
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "phone_number": instance.phone_number,
            }

            serializer.save()

            new_data = {
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "phone_number": instance.phone_number,
            }

            missing_fields = []
            for field, value in new_data.items():
                if not value or value.strip() == "":
                    missing_fields.append(field.replace("_", " ").title())

            if missing_fields and len(missing_fields) > 0:
                send_profile_completion_reminder(instance, ", ".join(missing_fields))

            return Response(
                {"message": "Profile updated successfully", "user": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        if request.user.is_google_user:
            return Response(
                {
                    "error": "Google users cannot change password. Use Google account settings."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()

            send_password_changed_email(request.user)

            UserSession.objects.deactivate_user_sessions(request.user)

            return Response(
                {"message": "Password changed successfully. Please login again."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email, is_active=True)

            if user.is_google_user:
                return Response(
                    {
                        "error": "Google users cannot reset password. Use Google account recovery."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ip_address = get_client_ip(request)
            reset = PasswordReset.objects.create_reset(user, ip_address)
            send_password_reset_email(user, reset.token)

            return Response(
                {"message": "Password reset email sent successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            new_password = serializer.validated_data["new_password"]

            user = PasswordReset.objects.use_token(token, new_password)
            if user:
                if user.is_google_user:
                    return Response(
                        {"error": "Cannot reset password for Google users"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                send_password_changed_email(user)

                UserSession.objects.deactivate_user_sessions(user)

                return Response(
                    {
                        "message": "Password reset successful. Please login with your new password."
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            user = EmailVerification.objects.verify_token(token)

            if user:
                return Response(
                    {
                        "message": "Email verified successfully",
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "is_verified": user.is_verified,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "Invalid or expired verification token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email, is_active=True)

            if user.is_google_user:
                return Response(
                    {"message": "Google users are automatically verified"},
                    status=status.HTTP_200_OK,
                )

            verification = EmailVerification.objects.create_verification(user)
            send_verification_email(user, verification.token)

            return Response(
                {"message": "Verification email sent successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, CanAccessClientProfile]

    def get_object(self):
        profile, created = ClientProfile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        serializer = ClientProfileUpdateSerializer(
            self.get_object(), data=request.data, partial=True
        )

        if serializer.is_valid():
            old_profile = self.get_object()
            old_data = {
                "ndis_number": old_profile.ndis_number,
                "accessibility_needs": old_profile.accessibility_needs,
                "emergency_contact_name": getattr(
                    old_profile, "emergency_contact_name", ""
                ),
                "emergency_contact_phone": getattr(
                    old_profile, "emergency_contact_phone", ""
                ),
            }

            serializer.save()

            new_profile = self.get_object()
            missing_fields = []

            if not new_profile.ndis_number:
                missing_fields.append("NDIS Number")
            if not new_profile.accessibility_needs:
                missing_fields.append("Accessibility Needs")
            if not getattr(new_profile, "emergency_contact_name", ""):
                missing_fields.append("Emergency Contact Name")
            if not getattr(new_profile, "emergency_contact_phone", ""):
                missing_fields.append("Emergency Contact Phone")

            if missing_fields:
                send_profile_completion_reminder(
                    request.user, ", ".join(missing_fields)
                )

            return Response(
                {
                    "message": "Client profile updated successfully",
                    "profile": ClientProfileSerializer(self.get_object()).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, CanModifyAddress]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class UserDeactivationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDeactivationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.is_active = False
            user.save()

            UserSession.objects.deactivate_user_sessions(user)

            return Response(
                {"message": "Account deactivated successfully"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get("user_type")
        client_type = self.request.query_params.get("client_type")
        auth_provider = self.request.query_params.get("auth_provider")
        is_active = self.request.query_params.get("is_active")
        is_verified = self.request.query_params.get("is_verified")
        search = self.request.query_params.get("search")

        if user_type:
            queryset = queryset.filter(user_type=user_type)
        if client_type:
            queryset = queryset.filter(client_type=client_type)
        if auth_provider:
            queryset = queryset.filter(auth_provider=auth_provider)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == "true")
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        return queryset.order_by("-date_joined")


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, CanManageUsers]


class UserStatsView(APIView):
    permission_classes = [IsAuthenticated, CanAccessAdminDashboard]

    def get(self, request):
        now = timezone.now()
        last_30_days = now - timedelta(days=30)

        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "verified_users": User.objects.filter(is_verified=True).count(),
            "client_users": User.objects.filter(user_type="client").count(),
            "ndis_clients": User.objects.filter(
                user_type="client", client_type="ndis"
            ).count(),
            "general_clients": User.objects.filter(
                user_type="client", client_type="general"
            ).count(),
            "staff_users": User.objects.filter(user_type="staff").count(),
            "admin_users": User.objects.filter(user_type="admin").count(),
            "google_users": User.objects.filter(auth_provider="google").count(),
            "recent_registrations": User.objects.filter(
                date_joined__gte=last_30_days
            ).count(),
        }

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BulkUserActionView(APIView):
    permission_classes = [IsAuthenticated, CanBulkManageUsers]
    serializer_class = BulkUserActionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data["user_ids"]
            action = serializer.validated_data["action"]

            users = User.objects.filter(id__in=user_ids)

            if action == "activate":
                users.update(is_active=True)
            elif action == "deactivate":
                users.update(is_active=False)
                for user in users:
                    UserSession.objects.deactivate_user_sessions(user)
            elif action == "verify":
                users.update(is_verified=True)
            elif action == "unverify":
                users.update(is_verified=False)
            elif action == "lock":
                users.update(is_active=False)
                for user in users:
                    UserSession.objects.deactivate_user_sessions(user)
                    send_account_locked_email(user, "Account locked by administrator")

            return Response(
                {"message": f"Successfully {action}d {users.count()} users"},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SocialProfileListView(generics.ListAPIView):
    serializer_class = SocialAuthProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialAuthProfile.objects.filter(user=self.request.user, is_active=True)


class SocialProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SocialAuthProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return SocialAuthProfile.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    user = request.user

    dashboard_data = {
        "user": UserProfileSerializer(user).data,
        "recent_activity": [],
        "notifications": [],
        "quick_stats": {},
    }

    if user.is_client:
        dashboard_data["client_profile"] = ClientProfileSerializer(
            user.client_profile if hasattr(user, "client_profile") else None
        ).data
        dashboard_data["addresses"] = AddressSerializer(
            user.addresses.all(), many=True
        ).data

    dashboard_data["social_profiles"] = SocialAuthProfileSerializer(
        user.social_profiles.filter(is_active=True), many=True
    ).data

    return Response(dashboard_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def cleanup_expired_tokens(request):
    email_count = EmailVerification.objects.cleanup_expired()
    password_count = PasswordReset.objects.cleanup_expired()
    session_count = UserSession.objects.cleanup_inactive_sessions()

    return Response(
        {
            "message": "Cleanup completed successfully",
            "cleaned_up": {
                "email_verifications": email_count,
                "password_resets": password_count,
                "user_sessions": session_count,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def refresh_social_tokens(request):
    try:
        expired_profiles = SocialAuthProfile.objects.filter(
            token_expires_at__lt=timezone.now(), is_active=True
        )

        refreshed_count = 0
        for profile in expired_profiles:
            social_backend = SocialAuthBackend()
            if social_backend.refresh_token(profile):
                refreshed_count += 1

        return Response(
            {
                "message": f"Refreshed {refreshed_count} social tokens",
                "total_expired": expired_profiles.count(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Token refresh failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def lock_user_account(request):
    user_id = request.data.get("user_id")
    reason = request.data.get("reason", "Account locked by administrator")

    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()

        UserSession.objects.deactivate_user_sessions(user)
        send_account_locked_email(user, reason)

        return Response(
            {"message": f"User account {user.email} has been locked"},
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def send_profile_reminder(request):
    user_id = request.data.get("user_id")
    missing_field = request.data.get("missing_field", "profile information")

    try:
        user = User.objects.get(id=user_id)
        send_profile_completion_reminder(user, missing_field)

        return Response(
            {"message": f"Profile completion reminder sent to {user.email}"},
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response(
        {
            "status": "healthy",
            "timestamp": timezone.now(),
            "service": "accounts",
            "features": {
                "google_auth": True,
                "social_login": True,
                "account_linking": True,
                "email_notifications": True,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, CanAccessAdminDashboard])
def social_auth_stats(request):
    stats = {
        "total_social_profiles": SocialAuthProfile.objects.count(),
        "active_social_profiles": SocialAuthProfile.objects.filter(
            is_active=True
        ).count(),
        "google_profiles": SocialAuthProfile.objects.filter(
            provider="google", is_active=True
        ).count(),
        "expired_tokens": SocialAuthProfile.objects.filter(
            token_expires_at__lt=timezone.now(), is_active=True
        ).count(),
        "users_with_social_auth": User.objects.filter(social_profiles__is_active=True)
        .distinct()
        .count(),
    }

    return Response(stats, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStaffOrAdmin])
def test_email_templates(request):
    template_type = request.data.get("template_type")
    user_email = request.data.get("user_email")

    try:
        user = User.objects.get(email=user_email)

        if template_type == "welcome":
            send_welcome_email(user)
        elif template_type == "verification":
            verification = EmailVerification.objects.create_verification(user)
            send_verification_email(user, verification.token)
        elif template_type == "password_reset":
            reset = PasswordReset.objects.create_reset(user, "127.0.0.1")
            send_password_reset_email(user, reset.token)
        elif template_type == "password_changed":
            send_password_changed_email(user)
        elif template_type == "social_linked":
            send_social_account_linked_email(user, "google")
        elif template_type == "social_unlinked":
            send_social_account_unlinked_email(user, "google")
        elif template_type == "login_notification":
            send_login_notification_email(user, "127.0.0.1", "Test Browser", "email")
        elif template_type == "profile_reminder":
            send_profile_completion_reminder(user, "phone number")
        elif template_type == "account_locked":
            send_account_locked_email(user, "Testing email template")
        else:
            return Response(
                {"error": "Invalid template type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": f"{template_type} email sent successfully to {user.email}"},
            status=status.HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
