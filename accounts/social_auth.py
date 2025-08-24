import logging
from typing import Optional, Dict, Any, Union
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from .models import User, SocialAuthProfile, ClientProfile
from .utils import (
    validate_social_provider_token,
    get_social_user_info,
    validate_google_access_token,
    get_google_user_info,
    refresh_google_access_token,
    log_user_activity,
    send_welcome_email,
    send_social_account_linked_email,
    send_social_account_unlinked_email,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class SocialAuthBackend(BaseBackend):
    def __init__(self):
        self.supported_providers = ["google", "facebook", "apple"]

    def authenticate(self, request, provider=None, access_token=None, **kwargs):
        if not provider or not access_token:
            return None

        if provider not in self.supported_providers:
            logger.error(f"Unsupported provider: {provider}")
            return None

        return self.authenticate_social_user(provider, access_token)

    def authenticate_social_user(
        self, provider: str, access_token: str
    ) -> Optional[User]:
        try:
            user_data = self.get_provider_user_data(provider, access_token)
            if not user_data:
                logger.error(f"Failed to get user data from {provider}")
                return None

            email = user_data.get("email")
            provider_id = user_data.get("id")

            if not email or not provider_id:
                logger.error(f"Missing email or ID in {provider} user data")
                return None

            user = self._find_user_by_social_profile(provider, provider_id, email)
            if not user:
                user = self._find_user_by_email(email, provider)

            if user:
                if not user.is_active:
                    logger.error(f"User {email} is not active")
                    return None

                self._update_or_create_social_profile(
                    user, provider, access_token, user_data
                )

                log_user_activity(
                    user,
                    f"{provider}_login",
                    {"provider_id": provider_id, "email": email},
                )

                return user

            return None

        except Exception as e:
            logger.error(f"Error authenticating {provider} user: {str(e)}")
            return None

    def get_provider_user_data(
        self, provider: str, access_token: str
    ) -> Optional[Dict[str, Any]]:
        try:
            if provider == "google":
                return get_google_user_info(access_token)
            elif provider == "facebook":
                return self._get_facebook_user_info(access_token)
            elif provider == "apple":
                return self._get_apple_user_info(access_token)
            else:
                logger.error(f"Unsupported provider: {provider}")
                return None

        except Exception as e:
            logger.error(f"Error getting {provider} user data: {str(e)}")
            return None

    def register_social_user(
        self,
        provider: str,
        access_token: str,
        user_type: str = "client",
        client_type: str = "general",
        phone_number: str = "",
    ) -> Optional[User]:
        try:
            user_data = self.get_provider_user_data(provider, access_token)
            if not user_data:
                return None

            email = user_data.get("email")
            provider_id = user_data.get("id")

            if not email or not provider_id:
                logger.error(f"Missing email or ID in {provider} user data")
                return None

            if User.objects.filter(email=email).exists():
                logger.error(f"User with email {email} already exists")
                return None

            with transaction.atomic():
                user_data_normalized = self._normalize_user_data(provider, user_data)

                user = User.objects.create_user(
                    email=email,
                    first_name=user_data_normalized.get("first_name", ""),
                    last_name=user_data_normalized.get("last_name", ""),
                    phone_number=phone_number,
                    user_type=user_type,
                    client_type=client_type if user_type == "client" else None,
                    auth_provider=provider,
                    avatar_url=user_data_normalized.get("avatar_url", ""),
                    is_verified=True,
                )

                if provider == "google":
                    user.google_id = provider_id

                user.set_unusable_password()
                user.save()

                self._create_social_profile(user, provider, access_token, user_data)

                send_welcome_email(user)

                log_user_activity(
                    user,
                    f"{provider}_registration",
                    {
                        "provider_id": provider_id,
                        "email": email,
                        "user_type": user_type,
                        "client_type": client_type,
                    },
                )

                return user

        except Exception as e:
            logger.error(f"Error registering {provider} user: {str(e)}")
            return None

    def link_social_account(self, user: User, provider: str, access_token: str) -> bool:
        try:
            user_data = self.get_provider_user_data(provider, access_token)
            if not user_data:
                return False

            provider_email = user_data.get("email")
            provider_id = user_data.get("id")

            if not provider_email or not provider_id:
                logger.error(f"Missing email or ID in {provider} user data")
                return False

            if provider_email != user.email:
                logger.error(f"Email mismatch: {provider_email} vs {user.email}")
                return False

            if self._is_provider_id_taken(provider, provider_id, user.id):
                logger.error(
                    f"{provider} ID {provider_id} already linked to another user"
                )
                return False

            existing_profile = SocialAuthProfile.objects.filter(
                user=user, provider=provider
            ).first()

            if existing_profile and existing_profile.is_active:
                logger.error(f"{provider} account already linked for user {user.email}")
                return False

            with transaction.atomic():
                if provider == "google":
                    user.google_id = provider_id

                if not user.avatar_url:
                    user_data_normalized = self._normalize_user_data(
                        provider, user_data
                    )
                    user.avatar_url = user_data_normalized.get("avatar_url", "")

                user.save()

                if existing_profile:
                    existing_profile.provider_id = provider_id
                    existing_profile.provider_email = provider_email
                    existing_profile.access_token = access_token
                    existing_profile.profile_data = user_data
                    existing_profile.is_active = True
                    existing_profile.save()
                else:
                    self._create_social_profile(user, provider, access_token, user_data)

                send_social_account_linked_email(user, provider)

                log_user_activity(
                    user,
                    f"{provider}_account_linked",
                    {"provider_id": provider_id, "email": provider_email},
                )

                return True

        except Exception as e:
            logger.error(f"Error linking {provider} account: {str(e)}")
            return False

    def unlink_social_account(self, user: User, provider: str) -> bool:
        try:
            if user.auth_provider == provider and not user.has_usable_password:
                logger.error(
                    f"Cannot unlink primary {provider} account without password for {user.email}"
                )
                return False

            social_profile = SocialAuthProfile.objects.filter(
                user=user, provider=provider, is_active=True
            ).first()

            if not social_profile:
                logger.error(
                    f"No active {provider} profile found for user {user.email}"
                )
                return False

            with transaction.atomic():
                social_profile.is_active = False
                social_profile.save()

                if user.auth_provider == provider:
                    user.auth_provider = "email"

                if provider == "google":
                    user.google_id = None

                user.save()

                send_social_account_unlinked_email(user, provider)

                log_user_activity(
                    user, f"{provider}_account_unlinked", {"email": user.email}
                )

                return True

        except Exception as e:
            logger.error(f"Error unlinking {provider} account: {str(e)}")
            return False
        
    def refresh_token(self, profile: SocialAuthProfile) -> bool:
        try:
            if profile.provider == 'google':
                return self._refresh_google_token(profile)
            elif profile.provider == 'facebook':
                return self._refresh_facebook_token(profile)
            elif profile.provider == 'apple':
                return self._refresh_apple_token(profile)
            else:
                logger.error(f"Token refresh not supported for provider: {profile.provider}")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing {profile.provider} token: {str(e)}")
            return False
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _find_user_by_social_profile(self, provider: str, provider_id: str, email: str) -> Optional[User]:
        try:
            social_profile = SocialAuthProfile.objects.filter(
                provider=provider,
                provider_id=provider_id,
                is_active=True
            ).first()
            
            if social_profile and social_profile.user.is_active:
                if social_profile.user.email == email:
                    return social_profile.user
                else:
                    logger.warning(f"Email mismatch for {provider} user: {email} vs {social_profile.user.email}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by social profile: {str(e)}")
            return None
    
    def _find_user_by_email(self, email: str, provider: str) -> Optional[User]:
        try:
            user = User.objects.filter(email=email, is_active=True).first()
            if user and user.auth_provider == provider:
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None
    
    def _is_provider_id_taken(self, provider: str, provider_id: str, exclude_user_id: int = None) -> bool:
        try:
            query = SocialAuthProfile.objects.filter(
                provider=provider,
                provider_id=provider_id,
                is_active=True
            )
            
            if exclude_user_id:
                query = query.exclude(user_id=exclude_user_id)
            
            return query.exists()
            
        except Exception as e:
            logger.error(f"Error checking if provider ID is taken: {str(e)}")
            return True
    
    def _normalize_user_data(self, provider: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        if provider == 'google':
            return {
                'first_name': user_data.get('given_name', ''),
                'last_name': user_data.get('family_name', ''),
                'avatar_url': user_data.get('picture', ''),
                'full_name': user_data.get('name', '')
            }
        elif provider == 'facebook':
            return {
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'avatar_url': user_data.get('picture', {}).get('data', {}).get('url', ''),
                'full_name': user_data.get('name', '')
            }
        elif provider == 'apple':
            name = user_data.get('name', {})
            return {
                'first_name': name.get('firstName', ''),
                'last_name': name.get('lastName', ''),
                'avatar_url': '',
                'full_name': f"{name.get('firstName', '')} {name.get('lastName', '')}".strip()
            }
        else:
            return {
                'first_name': '',
                'last_name': '',
                'avatar_url': '',
                'full_name': ''
            }
    
    def _create_social_profile(self, user: User, provider: str, access_token: str, user_data: Dict[str, Any]) -> SocialAuthProfile:
        return SocialAuthProfile.objects.create(
            user=user,
            provider=provider,
            provider_id=user_data.get('id'),
            provider_email=user_data.get('email'),
            access_token=access_token,
            profile_data=user_data,
            is_active=True
        )
    
    def _update_or_create_social_profile(self, user: User, provider: str, access_token: str, user_data: Dict[str, Any]) -> None:
        social_profile = SocialAuthProfile.objects.filter(
            user=user, 
            provider=provider
        ).first()
        
        if social_profile:
            social_profile.access_token = access_token
            social_profile.profile_data = user_data
            social_profile.provider_email = user_data.get('email')
            social_profile.provider_id = user_data.get('id')
            social_profile.is_active = True
            social_profile.save()
        else:
            self._create_social_profile(user, provider, access_token, user_data)
    
    def _refresh_google_token(self, profile: SocialAuthProfile) -> bool:
        try:
            if not profile.refresh_token:
                logger.error(f"No refresh token for Google profile {profile.id}")
                return False
            
            token_data = refresh_google_access_token(profile.refresh_token)
            if not token_data:
                return False
            
            profile.access_token = token_data.get('access_token')
            if 'expires_in' in token_data:
                profile.token_expires_at = timezone.now() + timezone.timedelta(
                    seconds=int(token_data['expires_in'])
                )
            profile.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing Google token: {str(e)}")
            return False
    
    def _refresh_facebook_token(self, profile: SocialAuthProfile) -> bool:
        try:
            logger.info("Facebook token refresh not implemented yet")
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing Facebook token: {str(e)}")
            return False
    
    def _refresh_apple_token(self, profile: SocialAuthProfile) -> bool:
        try:
            logger.info("Apple token refresh not implemented yet")
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing Apple token: {str(e)}")
            return False
    
    def _get_facebook_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            
            url = f"https://graph.facebook.com/me?fields=id,email,first_name,last_name,name,picture&access_token={access_token}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                if 'email' in user_data and 'id' in user_data:
                    return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Facebook user info: {str(e)}")
            return None
    
    def _get_apple_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        try:
            logger.info("Apple user info retrieval not implemented yet")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Apple user info: {str(e)}")
            return None
    
    def get_user_social_profiles(self, user: User) -> list:
        try:
            return list(SocialAuthProfile.objects.filter(user=user, is_active=True))
            
        except Exception as e:
            logger.error(f"Error getting user social profiles: {str(e)}")
            return []
    
    def is_social_user(self, user: User, provider: str = None) -> bool:
        try:
            if provider:
                return SocialAuthProfile.objects.filter(
                    user=user, 
                    provider=provider, 
                    is_active=True
                ).exists()
            else:
                return SocialAuthProfile.objects.filter(
                    user=user, 
                    is_active=True
                ).exists()
                
        except Exception as e:
            logger.error(f"Error checking if user is social user: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        try:
            expired_profiles = SocialAuthProfile.objects.filter(
                token_expires_at__lt=timezone.now(),
                is_active=True
            )
            
            count = expired_profiles.count()
            expired_profiles.update(is_active=False)
            
            logger.info(f"Cleaned up {count} expired social tokens")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            return 0
    
    def validate_provider_support(self, provider: str) -> bool:
        return provider in self.supported_providers
    
    def get_supported_providers(self) -> list:
        return self.supported_providers.copy()
    
    def get_provider_login_url(self, provider: str, redirect_uri: str = None) -> Optional[str]:
        try:
            if provider == 'google':
                from .utils import get_google_login_url
                return get_google_login_url(redirect_uri)
            else:
                logger.error(f"Login URL generation not supported for provider: {provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating {provider} login URL: {str(e)}")
            return None

