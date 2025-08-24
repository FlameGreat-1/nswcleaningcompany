from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from datetime import timedelta
import secrets
import string
import hashlib
import re
import logging
import requests
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "127.0.0.1")
    return ip


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def validate_google_access_token(access_token: str) -> Optional[Dict[str, Any]]:
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers, timeout=10
        )

        if response.status_code == 200:
            user_data = response.json()
            if "email" in user_data and "id" in user_data:
                return user_data

        logger.error(
            f"Google API returned status {response.status_code}: {response.text if hasattr(response, 'text') else 'No response text'}"
        )
        return None

    except Exception as e:
        logger.error(f"Error validating Google access token: {str(e)}")
        return None


def get_google_user_info(token: str) -> Optional[Dict[str, Any]]:
    try:
        id_token_info = verify_google_id_token(token)
        if id_token_info:
            return {
                "id": id_token_info.get("sub"),
                "email": id_token_info.get("email"),
                "given_name": id_token_info.get("given_name", ""),
                "family_name": id_token_info.get("family_name", ""),
                "name": id_token_info.get("name", ""),
                "picture": id_token_info.get("picture", ""),
                "verified_email": id_token_info.get("email_verified", False),
            }

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers, timeout=10
        )

        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "given_name": user_data.get("given_name", ""),
                "family_name": user_data.get("family_name", ""),
                "name": user_data.get("name", ""),
                "picture": user_data.get("picture", ""),
                "verified_email": user_data.get("verified_email", False),
            }

        logger.error(f"Failed to get Google user info: {response.status_code}")
        return None

    except Exception as e:
        logger.error(f"Error getting Google user info: {str(e)}")
        return None


def verify_google_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    try:
        google_client_id = getattr(settings, "GOOGLE_OAUTH2_CLIENT_ID", "")
        if not google_client_id:
            logger.error("Google OAuth2 client ID not configured")
            return None

        response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}", timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            if token_data.get("aud") == google_client_id:
                return token_data

        return None

    except Exception as e:
        logger.error(f"Error verifying Google ID token: {str(e)}")
        return None


def refresh_google_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    try:
        google_client_id = getattr(settings, "GOOGLE_OAUTH2_CLIENT_ID", "")
        google_client_secret = getattr(settings, "GOOGLE_OAUTH2_CLIENT_SECRET", "")

        if not google_client_id or not google_client_secret:
            logger.error("Google OAuth2 credentials not configured")
            return None

        data = {
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(
            "https://oauth2.googleapis.com/token", data=data, timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception as e:
        logger.error(f"Error refreshing Google access token: {str(e)}")
        return None


def validate_social_provider_token(
    provider: str, access_token: str
) -> Optional[Dict[str, Any]]:
    if provider == "google":
        return validate_google_access_token(access_token)

    logger.error(f"Unsupported social provider: {provider}")
    return None


def get_social_user_info(provider: str, access_token: str) -> Optional[Dict[str, Any]]:
    if provider == "google":
        return get_google_user_info(access_token)

    logger.error(f"Unsupported social provider: {provider}")
    return None


def generate_social_auth_state() -> str:
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> Dict[str, Any]:
    errors = []
    score = 0

    if len(password) >= 8:
        score += 1
    else:
        errors.append("Password must be at least 8 characters long")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        errors.append("Password must contain at least one uppercase letter")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        errors.append("Password must contain at least one lowercase letter")

    if re.search(r"\d", password):
        score += 1
    else:
        errors.append("Password must contain at least one digit")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        errors.append("Password must contain at least one special character")

    strength_levels = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong",
        5: "Very Strong",
    }

    return {
        "score": score,
        "strength": strength_levels.get(score, "Unknown"),
        "errors": errors,
        "is_valid": len(errors) == 0,
    }


def send_email_template(
    template_name: str,
    context: Dict[str, Any],
    subject: str,
    recipient_list: list,
    from_email: Optional[str] = None,
) -> bool:
    try:
        from_email = from_email or settings.DEFAULT_FROM_EMAIL

        html_content = render_to_string(f"emails/{template_name}.html", context)
        text_content = render_to_string(f"emails/{template_name}.txt", context)

        msg = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(f"Email sent successfully to {recipient_list}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        return False


def send_welcome_email(user, verification_token: str = None) -> bool:
    try:
        context = {
            "user": user,
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
            "is_google_user": (
                user.auth_provider == "google"
                if hasattr(user, "auth_provider")
                else False
            ),
        }

        if verification_token and not (
            hasattr(user, "auth_provider") and user.auth_provider == "google"
        ):
            context["verification_url"] = (
                f"{settings.FRONTEND_URL}/accounts/email-verification?token={verification_token}"
            )

        subject = f"Welcome to {context['site_name']}"
        if verification_token and not (
            hasattr(user, "auth_provider") and user.auth_provider == "google"
        ):
            subject += " - Please verify your email"

        return send_email_template(
            template_name="welcome",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_verification_email(user, verification_token: str) -> bool:
    try:
        if hasattr(user, "auth_provider") and user.auth_provider == "google":
            logger.info(f"Skipping verification email for Google user: {user.email}")
            return True

        verification_url = f"{settings.FRONTEND_URL}/accounts/email-verification?token={verification_token}"

        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "expiry_hours": 24,
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
        }

        subject = "Please verify your email address"

        return send_email_template(
            template_name="email_verification",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, reset_token: str) -> bool:
    try:
        if hasattr(user, "auth_provider") and user.auth_provider == "google":
            logger.info(f"Skipping password reset email for Google user: {user.email}")
            return False

        reset_url = (
            f"{settings.FRONTEND_URL}/accounts/password-reset?token={reset_token}"
        )

        context = {
            "user": user,
            "reset_url": reset_url,
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "expiry_hours": 1,
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
        }

        subject = "Password Reset Request"

        return send_email_template(
            template_name="password_reset",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False


def send_social_account_linked_email(user, provider: str) -> bool:
    try:
        context = {
            "user": user,
            "provider": provider.title(),
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
            "timestamp": timezone.now(),
        }

        subject = f"{provider.title()} Account Linked Successfully"

        return send_email_template(
            template_name="social_account_linked",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(
            f"Failed to send social account linked email to {user.email}: {str(e)}"
        )
        return False


def send_social_account_unlinked_email(user, provider: str) -> bool:
    try:
        context = {
            "user": user,
            "provider": provider.title(),
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
            "timestamp": timezone.now(),
        }

        subject = f"{provider.title()} Account Unlinked"

        return send_email_template(
            template_name="social_account_unlinked",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(
            f"Failed to send social account unlinked email to {user.email}: {str(e)}"
        )
        return False


def send_password_changed_email(user) -> bool:
    try:
        if hasattr(user, "auth_provider") and user.auth_provider == "google":
            logger.info(
                f"Skipping password changed email for Google user: {user.email}"
            )
            return True

        context = {
            "user": user,
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
            "timestamp": timezone.now(),
        }

        subject = "Password Changed Successfully"

        return send_email_template(
            template_name="password_changed",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send password changed email to {user.email}: {str(e)}")
        return False


def send_profile_completion_reminder(user, missing_field: str) -> bool:
    try:
        context = {
            "user": user,
            "missing_field": missing_field,
            "profile_url": f"{settings.FRONTEND_URL}/profile",
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "is_google_user": (
                user.auth_provider == "google"
                if hasattr(user, "auth_provider")
                else False
            ),
        }

        subject = "Complete Your Profile"

        return send_email_template(
            template_name="profile_completion_reminder",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(
            f"Failed to send profile completion reminder to {user.email}: {str(e)}"
        )
        return False


def send_account_locked_email(
    user, reason: str = "Multiple failed login attempts"
) -> bool:
    try:
        context = {
            "user": user,
            "reason": reason,
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "timestamp": timezone.now(),
            "is_google_user": (
                user.auth_provider == "google"
                if hasattr(user, "auth_provider")
                else False
            ),
        }

        subject = "Account Security Alert - Account Locked"

        return send_email_template(
            template_name="account_locked",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send account locked email to {user.email}: {str(e)}")
        return False


def send_login_notification_email(
    user, ip_address: str, user_agent: str, login_method: str = "email"
) -> bool:
    try:
        context = {
            "user": user,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "login_method": login_method,
            "timestamp": timezone.now(),
            "site_name": getattr(settings, "SITE_NAME", "Cleaning Service"),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
        }

        subject = "New Login to Your Account"

        return send_email_template(
            template_name="login_notification",
            context=context,
            subject=subject,
            recipient_list=[user.email],
        )

    except Exception as e:
        logger.error(f"Failed to send login notification to {user.email}: {str(e)}")
        return False


def format_phone_number(phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", phone)

    if cleaned.startswith("0"):
        cleaned = "+61" + cleaned[1:]
    elif cleaned.startswith("61") and not cleaned.startswith("+61"):
        cleaned = "+" + cleaned
    elif not cleaned.startswith("+"):
        cleaned = "+61" + cleaned

    return cleaned


def validate_australian_postcode(postcode: str) -> bool:
    return bool(re.match(r"^\d{4}$", postcode))


def get_suburb_from_postcode(postcode: str) -> Optional[str]:
    postcode_mapping = {
        "2000": "Sydney",
        "3000": "Melbourne",
        "4000": "Brisbane",
        "5000": "Adelaide",
        "6000": "Perth",
        "7000": "Hobart",
        "0800": "Darwin",
        "2600": "Canberra",
    }
    return postcode_mapping.get(postcode)


def calculate_service_area_distance(postcode1: str, postcode2: str) -> Optional[float]:
    try:
        return 0.0
    except Exception as e:
        logger.error(
            f"Error calculating distance between {postcode1} and {postcode2}: {str(e)}"
        )
        return None


def generate_user_avatar_url(user) -> str:
    if hasattr(user, "avatar_url") and user.avatar_url:
        return user.avatar_url

    email_hash = hashlib.md5(user.email.lower().encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"


def sanitize_user_input(input_string: str) -> str:
    if not input_string:
        return ""

    sanitized = re.sub(r'[<>"\']', "", input_string)
    sanitized = sanitized.strip()
    return sanitized


def log_user_activity(user, action: str, details: Optional[Dict] = None) -> None:
    try:
        activity_data = {
            "user_id": user.id,
            "user_email": user.email,
            "action": action,
            "timestamp": timezone.now(),
            "auth_provider": getattr(user, "auth_provider", "email"),
            "details": details or {},
        }

        logger.info(f"User activity: {activity_data}")

    except Exception as e:
        logger.error(f"Failed to log user activity: {str(e)}")


def check_rate_limit(
    user, action: str, limit: int = 5, window_minutes: int = 15
) -> bool:
    try:
        cache_key = f"rate_limit_{user.id}_{action}"

        return True

    except Exception as e:
        logger.error(f"Error checking rate limit for user {user.email}: {str(e)}")
        return True


def generate_api_key(user) -> str:
    timestamp = str(int(timezone.now().timestamp()))
    user_data = f"{user.id}_{user.email}_{timestamp}"
    return hashlib.sha256(user_data.encode()).hexdigest()


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    if not data or len(data) <= visible_chars:
        return data

    visible_start = data[: visible_chars // 2]
    visible_end = data[-(visible_chars // 2) :] if visible_chars > 1 else ""
    masked_middle = mask_char * (len(data) - visible_chars)

    return f"{visible_start}{masked_middle}{visible_end}"


def format_user_display_name(user) -> str:
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    else:
        return user.email.split("@")[0]


def get_user_timezone(user) -> str:
    if hasattr(user, "client_profile") and user.client_profile:
        return getattr(user.client_profile, "timezone", "Australia/Sydney")
    return "Australia/Sydney"


def convert_to_user_timezone(dt, user):
    import pytz

    try:
        user_tz = pytz.timezone(get_user_timezone(user))
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(user_tz)
    except Exception:
        return dt


def cleanup_user_data(user) -> Dict[str, int]:
    try:
        from .models import (
            UserSession,
            EmailVerification,
            PasswordReset,
            SocialAuthProfile,
        )

        sessions_deleted = UserSession.objects.filter(user=user).count()
        UserSession.objects.filter(user=user).delete()

        verifications_deleted = EmailVerification.objects.filter(user=user).count()
        EmailVerification.objects.filter(user=user).delete()

        resets_deleted = PasswordReset.objects.filter(user=user).count()
        PasswordReset.objects.filter(user=user).delete()

        social_profiles_deleted = SocialAuthProfile.objects.filter(user=user).count()
        SocialAuthProfile.objects.filter(user=user).delete()

        return {
            "sessions": sessions_deleted,
            "verifications": verifications_deleted,
            "password_resets": resets_deleted,
            "social_profiles": social_profiles_deleted,
        }

    except Exception as e:
        logger.error(f"Error cleaning up user data for {user.email}: {str(e)}")
        return {
            "sessions": 0,
            "verifications": 0,
            "password_resets": 0,
            "social_profiles": 0,
        }


def export_user_data(user) -> Dict[str, Any]:
    try:
        user_data = {
            "personal_info": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "auth_provider": getattr(user, "auth_provider", "email"),
                "avatar_url": getattr(user, "avatar_url", ""),
            },
            "account_info": {
                "user_type": user.user_type,
                "client_type": user.client_type,
                "is_verified": user.is_verified,
                "is_active": user.is_active,
                "is_google_user": (
                    user.auth_provider == "google"
                    if hasattr(user, "auth_provider")
                    else False
                ),
            },
            "addresses": [],
            "client_profile": None,
            "social_profiles": [],
        }

        if hasattr(user, "addresses"):
            user_data["addresses"] = [
                {
                    "type": addr.address_type,
                    "street": addr.street_address,
                    "suburb": addr.suburb,
                    "state": addr.state,
                    "postcode": addr.postcode,
                    "is_primary": addr.is_primary,
                }
                for addr in user.addresses.all()
            ]

        if hasattr(user, "client_profile") and user.client_profile:
            profile = user.client_profile
            user_data["client_profile"] = {
                "ndis_number": mask_sensitive_data(profile.ndis_number or ""),
                "accessibility_needs": profile.accessibility_needs,
                "preferred_communication": profile.preferred_communication,
                "emergency_contact": mask_sensitive_data(
                    profile.emergency_contact_phone or ""
                ),
            }

        if hasattr(user, "social_profiles"):
            user_data["social_profiles"] = [
                {
                    "provider": profile.provider,
                    "provider_email": profile.provider_email,
                    "is_active": profile.is_active,
                    "created_at": profile.created_at.isoformat(),
                }
                for profile in user.social_profiles.all()
            ]

        return user_data

    except Exception as e:
        logger.error(f"Error exporting user data for {user.email}: {str(e)}")
        return {}


def validate_social_auth_callback(
    provider: str, code: str, state: str
) -> Optional[Dict[str, Any]]:
    try:
        if provider == "google":
            return validate_google_auth_callback(code, state)

        logger.error(f"Unsupported social provider for callback: {provider}")
        return None

    except Exception as e:
        logger.error(f"Error validating social auth callback: {str(e)}")
        return None


def validate_google_auth_callback(code: str, state: str) -> Optional[Dict[str, Any]]:
    try:
        google_client_id = getattr(settings, "GOOGLE_OAUTH2_CLIENT_ID", "")
        google_client_secret = getattr(settings, "GOOGLE_OAUTH2_CLIENT_SECRET", "")
        redirect_uri = getattr(settings, "GOOGLE_OAUTH2_REDIRECT_URI", "")

        if not all([google_client_id, google_client_secret, redirect_uri]):
            logger.error("Google OAuth2 configuration incomplete")
            return None

        token_data = {
            "client_id": google_client_id,
            "client_secret": google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        response = requests.post(
            "https://oauth2.googleapis.com/token", data=token_data, timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except Exception as e:
        logger.error(f"Error validating Google auth callback: {str(e)}")
        return None


def cleanup_expired_social_tokens() -> int:
    try:
        from .models import SocialAuthProfile

        expired_profiles = SocialAuthProfile.objects.filter(
            token_expires_at__lt=timezone.now(), is_active=True
        )

        count = expired_profiles.count()
        expired_profiles.update(is_active=False)

        logger.info(f"Cleaned up {count} expired social tokens")
        return count

    except Exception as e:
        logger.error(f"Error cleaning up expired social tokens: {str(e)}")
        return 0


def get_social_login_url(provider: str, redirect_uri: str = None) -> Optional[str]:
    try:
        if provider == "google":
            return get_google_login_url(redirect_uri)

        logger.error(f"Unsupported social provider for login URL: {provider}")
        return None

    except Exception as e:
        logger.error(f"Error generating social login URL: {str(e)}")
        return None


def get_google_login_url(redirect_uri: str = None) -> Optional[str]:
    try:
        google_client_id = getattr(settings, "GOOGLE_OAUTH2_CLIENT_ID", "")
        default_redirect_uri = getattr(settings, "GOOGLE_OAUTH2_REDIRECT_URI", "")

        if not google_client_id:
            logger.error("Google OAuth2 client ID not configured")
            return None

        redirect_uri = redirect_uri or default_redirect_uri
        state = generate_social_auth_state()

        params = {
            "client_id": google_client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"

    except Exception as e:
        logger.error(f"Error generating Google login URL: {str(e)}")
        return None
