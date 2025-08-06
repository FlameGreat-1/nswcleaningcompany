import logging
import requests
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import User, SocialAuthProfile, ClientProfile
from .utils import (
    get_google_user_info,
    validate_google_access_token,
    verify_google_id_token,
    refresh_google_access_token,
    validate_google_auth_callback,
    get_google_login_url,
    log_user_activity,
    send_welcome_email,
    send_social_account_linked_email,
)

logger = logging.getLogger(__name__)


class GoogleOAuthHandler:
    def __init__(self):
        self.client_id = getattr(settings, "GOOGLE_OAUTH2_CLIENT_ID", "")
        self.client_secret = getattr(settings, "GOOGLE_OAUTH2_CLIENT_SECRET", "")
        self.redirect_uri = getattr(settings, "GOOGLE_OAUTH2_REDIRECT_URI", "")

        if not all([self.client_id, self.client_secret]):
            logger.error("Google OAuth2 credentials not properly configured")

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        try:
            user_data = get_google_user_info(access_token)
            if not user_data:
                logger.error("Failed to retrieve Google user info")
                return None

            if not user_data.get("email") or not user_data.get("id"):
                logger.error("Google user data missing required fields")
                return None

            return user_data

        except Exception as e:
            logger.error(f"Error getting Google user info: {str(e)}")
            return None

    def verify_token(self, access_token: str) -> bool:
        try:
            user_data = validate_google_access_token(access_token)
            return user_data is not None

        except Exception as e:
            logger.error(f"Error verifying Google token: {str(e)}")
            return False

    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        try:
            return verify_google_id_token(id_token)

        except Exception as e:
            logger.error(f"Error verifying Google ID token: {str(e)}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        try:
            return refresh_google_access_token(refresh_token)

        except Exception as e:
            logger.error(f"Error refreshing Google access token: {str(e)}")
            return None

    def authenticate_user(self, access_token: str) -> Optional[User]:
        try:
            user_data = self.get_user_info(access_token)
            if not user_data:
                return None

            email = user_data.get("email")
            google_id = user_data.get("id")

            if not email or not google_id:
                logger.error("Missing email or Google ID in user data")
                return None

            try:
                user = User.objects.get(email=email)

                if user.auth_provider != "google":
                    logger.error(f"User {email} exists but not a Google user")
                    return None

                if user.google_id != google_id:
                    logger.error(f"Google ID mismatch for user {email}")
                    return None

                if not user.is_active:
                    logger.error(f"User {email} is not active")
                    return None

                self._update_social_profile(user, access_token, user_data)

                log_user_activity(
                    user, "google_login", {"google_id": google_id, "email": email}
                )

                return user

            except User.DoesNotExist:
                logger.error(f"Google user {email} not found")
                return None

        except Exception as e:
            logger.error(f"Error authenticating Google user: {str(e)}")
            return None

    def register_user(
        self,
        access_token: str,
        user_type: str = "client",
        client_type: str = "general",
        phone_number: str = "",
    ) -> Optional[User]:
        try:
            user_data = self.get_user_info(access_token)
            if not user_data:
                return None

            email = user_data.get("email")
            google_id = user_data.get("id")

            if not email or not google_id:
                logger.error("Missing email or Google ID in user data")
                return None

            if User.objects.filter(email=email).exists():
                logger.error(f"User with email {email} already exists")
                return None

            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    first_name=user_data.get("given_name", ""),
                    last_name=user_data.get("family_name", ""),
                    phone_number=phone_number,
                    user_type=user_type,
                    client_type=client_type if user_type == "client" else None,
                    auth_provider="google",
                    google_id=google_id,
                    avatar_url=user_data.get("picture", ""),
                    is_verified=True,
                )

                user.set_unusable_password()
                user.save()

                if user.is_client:
                    ClientProfile.objects.create(user=user)

                self._create_social_profile(user, access_token, user_data)

                send_welcome_email(user)

                log_user_activity(
                    user,
                    "google_registration",
                    {
                        "google_id": google_id,
                        "email": email,
                        "user_type": user_type,
                        "client_type": client_type,
                    },
                )

                return user

        except Exception as e:
            logger.error(f"Error registering Google user: {str(e)}")
            return None

    def link_account(self, user: User, access_token: str) -> bool:
        try:
            user_data = self.get_user_info(access_token)
            if not user_data:
                return False

            google_email = user_data.get("email")
            google_id = user_data.get("id")

            if not google_email or not google_id:
                logger.error("Missing email or Google ID in user data")
                return False

            if google_email != user.email:
                logger.error(f"Email mismatch: {google_email} vs {user.email}")
                return False

            if User.objects.filter(google_id=google_id).exclude(id=user.id).exists():
                logger.error(f"Google ID {google_id} already linked to another user")
                return False

            existing_profile = SocialAuthProfile.objects.filter(
                user=user, provider="google"
            ).first()

            if existing_profile and existing_profile.is_active:
                logger.error(f"Google account already linked for user {user.email}")
                return False

            with transaction.atomic():
                user.google_id = google_id
                if not user.avatar_url:
                    user.avatar_url = user_data.get("picture", "")
                user.save()

                if existing_profile:
                    existing_profile.provider_id = google_id
                    existing_profile.provider_email = google_email
                    existing_profile.access_token = access_token
                    existing_profile.profile_data = user_data
                    existing_profile.is_active = True
                    existing_profile.save()
                else:
                    self._create_social_profile(user, access_token, user_data)

                send_social_account_linked_email(user, "google")

                log_user_activity(
                    user,
                    "google_account_linked",
                    {"google_id": google_id, "email": google_email},
                )

                return True

        except Exception as e:
            logger.error(f"Error linking Google account: {str(e)}")
            return False

    def unlink_account(self, user: User) -> bool:
        try:
            if user.auth_provider == "google" and not user.has_usable_password:
                logger.error(
                    f"Cannot unlink primary Google account without password for {user.email}"
                )
                return False

            social_profile = SocialAuthProfile.objects.filter(
                user=user, provider="google", is_active=True
            ).first()

            if not social_profile:
                logger.error(f"No active Google profile found for user {user.email}")
                return False

            with transaction.atomic():
                social_profile.is_active = False
                social_profile.save()

                if user.auth_provider == "google":
                    user.auth_provider = "email"

                user.google_id = None
                user.save()

                log_user_activity(
                    user, "google_account_unlinked", {"email": user.email}
                )

                return True

        except Exception as e:
            logger.error(f"Error unlinking Google account: {str(e)}")
            return False

    def handle_callback(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        try:
            return validate_google_auth_callback(code, state)

        except Exception as e:
            logger.error(f"Error handling Google callback: {str(e)}")
            return None

    def get_authorization_url(
        self, redirect_uri: str = None, state: str = None
    ) -> Optional[str]:
        try:
            return get_google_login_url(redirect_uri)

        except Exception as e:
            logger.error(f"Error generating Google authorization URL: {str(e)}")
            return None

    def refresh_user_token(self, user: User) -> bool:
        try:
            social_profile = SocialAuthProfile.objects.filter(
                user=user, provider="google", is_active=True
            ).first()

            if not social_profile or not social_profile.refresh_token:
                logger.error(f"No refresh token found for user {user.email}")
                return False

            token_data = self.refresh_access_token(social_profile.refresh_token)
            if not token_data:
                return False

            social_profile.access_token = token_data.get("access_token")
            if "expires_in" in token_data:
                social_profile.token_expires_at = timezone.now() + timezone.timedelta(
                    seconds=int(token_data["expires_in"])
                )
            social_profile.save()

            return True

        except Exception as e:
            logger.error(f"Error refreshing user token: {str(e)}")
            return False

    def _create_social_profile(
        self, user: User, access_token: str, user_data: Dict[str, Any]
    ) -> SocialAuthProfile:
        return SocialAuthProfile.objects.create(
            user=user,
            provider="google",
            provider_id=user_data.get("id"),
            provider_email=user_data.get("email"),
            access_token=access_token,
            profile_data=user_data,
            is_active=True,
        )

    def _update_social_profile(
        self, user: User, access_token: str, user_data: Dict[str, Any]
    ) -> None:
        social_profile = SocialAuthProfile.objects.filter(
            user=user, provider="google"
        ).first()

        if social_profile:
            social_profile.access_token = access_token
            social_profile.profile_data = user_data
            social_profile.provider_email = user_data.get("email")
            social_profile.is_active = True
            social_profile.save()
        else:
            self._create_social_profile(user, access_token, user_data)

    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        try:
            return User.objects.get(google_id=google_id, is_active=True)
        except User.DoesNotExist:
            return None

    def is_token_expired(self, user: User) -> bool:
        try:
            social_profile = SocialAuthProfile.objects.filter(
                user=user, provider="google", is_active=True
            ).first()

            if not social_profile:
                return True

            return social_profile.is_token_expired

        except Exception as e:
            logger.error(f"Error checking token expiration: {str(e)}")
            return True

    def validate_configuration(self) -> bool:
        return all([self.client_id, self.client_secret, self.redirect_uri])
