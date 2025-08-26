from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from datetime import timedelta
import secrets


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email address is required")

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Invalid email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("user_type", "client")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)

    def create_client(self, email, password, client_type="general", **extra_fields):
        extra_fields.setdefault("user_type", "client")
        extra_fields.setdefault("client_type", client_type)
        return self._create_user(email, password, **extra_fields)

    def create_ndis_client(self, email, password, **extra_fields):
        extra_fields.setdefault("user_type", "client")
        extra_fields.setdefault("client_type", "ndis")
        return self._create_user(email, password, **extra_fields)

    def create_staff_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("user_type", "staff")
        extra_fields.setdefault("is_verified", True)
        return self._create_user(email, password, **extra_fields)

    def get_active_users(self):
        return self.filter(is_active=True)

    def get_verified_users(self):
        return self.filter(is_verified=True, is_active=True)

    def get_clients(self):
        return self.filter(user_type="client", is_active=True)

    def get_ndis_clients(self):
        return self.filter(user_type="client", client_type="ndis", is_active=True)

    def get_general_clients(self):
        return self.filter(user_type="client", client_type="general", is_active=True)

    def get_staff_users(self):
        return self.filter(user_type="staff", is_active=True)

    def get_admin_users(self):
        return self.filter(user_type="admin", is_active=True)


class ClientProfileManager(BaseUserManager):

    def create_profile(self, user, **extra_fields):
        if not user:
            raise ValueError("User is required")

        profile = self.model(user=user, **extra_fields)
        profile.save(using=self._db)
        return profile

    def get_ndis_profiles(self):
        return self.filter(user__client_type="ndis", user__is_active=True)

    def get_profiles_with_accessibility_needs(self):
        return self.exclude(accessibility_needs="none").filter(user__is_active=True)

    def get_profiles_by_communication_preference(self, preference):
        return self.filter(preferred_communication=preference, user__is_active=True)


class AddressManager(BaseUserManager):

    def create_address(self, user, **extra_fields):
        if not user:
            raise ValueError("User is required")

        address = self.model(user=user, **extra_fields)

        if extra_fields.get("is_primary", False):
            self.filter(user=user).update(is_primary=False)

        address.save(using=self._db)
        return address

    def get_primary_address(self, user):
        try:
            return self.get(user=user, is_primary=True)
        except self.model.DoesNotExist:
            return None

    def get_user_addresses(self, user):
        return self.filter(user=user).order_by("-is_primary", "address_type")

    def get_addresses_by_suburb(self, suburb):
        return self.filter(suburb__icontains=suburb)


class EmailVerificationManager(BaseUserManager):

    def create_verification(self, user):
        if not user:
            raise ValueError("User is required")

        existing = self.filter(user=user, is_used=False)
        existing.delete()

        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)

        verification = self.model(user=user, token=token, expires_at=expires_at)
        verification.save(using=self._db)
        return verification

    def verify_token(self, token):
        try:
            verification = self.get(token=token, is_used=False)
            if verification.is_valid:
                verification.is_used = True
                verification.used_at = timezone.now()
                verification.save()
                verification.user.is_verified = True
                verification.user.save()
                return verification.user
            return None
        except self.model.DoesNotExist:
            return None

    def cleanup_expired(self):
        expired = self.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count


class PasswordResetManager(BaseUserManager):

    def create_reset(self, user, ip_address):
        if not user:
            raise ValueError("User is required")
        if not ip_address:
            raise ValueError("IP address is required")

        existing = self.filter(user=user, is_used=False)
        existing.delete()

        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        reset = self.model(
            user=user, token=token, expires_at=expires_at, ip_address=ip_address
        )
        reset.save(using=self._db)
        return reset

    def verify_token(self, token):
        try:
            reset = self.get(token=token, is_used=False)
            if reset.is_valid:
                return reset
            return None
        except self.model.DoesNotExist:
            return None

    def use_token(self, token, new_password):
        reset = self.verify_token(token)
        if reset:
            reset.user.set_password(new_password)
            reset.user.save()
            reset.is_used = True
            reset.used_at = timezone.now()
            reset.save()
            return reset.user
        return None

    def cleanup_expired(self):
        expired = self.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count

class UserSessionManager(BaseUserManager):

    def create_session(self, user, session_key=None, ip_address=None, user_agent=None):
        import uuid

        new_session_key = str(uuid.uuid4()).replace("-", "")[:32]

        session = self.model(
            user=user,
            session_key=new_session_key,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        try:
            session.save(using=self._db)
        except:
            session.session_key = str(uuid.uuid4()).replace("-", "")[:32]
            session.save(using=self._db)

        return session

    def get_active_sessions(self, user):
        return self.filter(user=user, is_active=True)

    def deactivate_session(self, session_key):
        return self.filter(session_key=session_key).update(
            is_active=False, ended_at=timezone.now()
        )

    def deactivate_user_sessions(self, user):
        return self.filter(user=user).update(is_active=False, ended_at=timezone.now())

    def cleanup_inactive_sessions(self, days=30):
        cutoff_date = timezone.now() - timedelta(days=days)
        inactive = self.filter(last_activity__lt=cutoff_date)
        count = inactive.count()
        inactive.delete()
        return count
