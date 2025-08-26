from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from .managers import (
    CustomUserManager,
    ClientProfileManager,
    AddressManager,
    EmailVerificationManager,
    PasswordResetManager,
    UserSessionManager,
)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ("client", "Client"),
        ("admin", "Admin"),
        ("staff", "Staff"),
    )

    CLIENT_TYPES = (
        ("general", "General Client"),
        ("ndis", "NDIS Client"),
    )

    AUTH_PROVIDERS = (
        ("email", "Email"),
        ("google", "Google"),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default="client")
    client_type = models.CharField(
        max_length=10, choices=CLIENT_TYPES, default="general", blank=True, null=True
    )
    auth_provider = models.CharField(
        max_length=10, choices=AUTH_PROVIDERS, default="email"
    )
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_client(self):
        return self.user_type == "client"

    @property
    def is_ndis_client(self):
        return self.user_type == "client" and self.client_type == "ndis"

    @property
    def is_admin_user(self):
        return self.user_type == "admin"

    @property
    def is_google_user(self):
        return self.auth_provider == "google"

    @property
    def has_usable_password(self):
        return self.auth_provider == "email" and super().has_usable_password()


class SocialAuthProfile(models.Model):
    PROVIDER_CHOICES = (
        ("google", "Google"),
        ("facebook", "Facebook"),
        ("apple", "Apple"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_profiles"
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=100)
    provider_email = models.EmailField()
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    profile_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_auth_profiles"
        verbose_name = "Social Auth Profile"
        verbose_name_plural = "Social Auth Profiles"
        unique_together = ["provider", "provider_id"]

    def __str__(self):
        return f"{self.user.email} - {self.provider}"

    @property
    def is_token_expired(self):
        if not self.token_expires_at:
            return False
        return timezone.now() > self.token_expires_at


class ClientProfile(models.Model):
    ACCESSIBILITY_NEEDS = (
        ("none", "No Special Needs"),
        ("mobility", "Mobility Assistance"),
        ("visual", "Visual Impairment"),
        ("hearing", "Hearing Impairment"),
        ("cognitive", "Cognitive Support"),
        ("multiple", "Multiple Needs"),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="client_profile"
    )
    ndis_number = models.CharField(max_length=20, blank=True, null=True)
    plan_manager = models.CharField(max_length=100, blank=True, null=True)
    support_coordinator = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True, null=True)
    accessibility_needs = models.CharField(
        max_length=20, choices=ACCESSIBILITY_NEEDS, default="none"
    )
    special_instructions = models.TextField(blank=True, null=True)
    preferred_communication = models.CharField(
        max_length=20,
        choices=(
            ("email", "Email"),
            ("phone", "Phone"),
            ("sms", "SMS"),
            ("app", "App Notifications"),
        ),
        default="email",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ClientProfileManager()

    class Meta:
        db_table = "client_profiles"
        verbose_name = "Client Profile"
        verbose_name_plural = "Client Profiles"

    def __str__(self):
        return f"{self.user.full_name} - Profile"

    @property
    def is_ndis_eligible(self):
        return bool(self.ndis_number)


class Address(models.Model):
    ADDRESS_TYPES = (
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(
        max_length=10, choices=ADDRESS_TYPES, default="home"
    )
    street_address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="Australia")
    is_primary = models.BooleanField(default=False)
    access_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AddressManager()

    class Meta:
        db_table = "addresses"
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        unique_together = ["user", "address_type"]

    def __str__(self):
        return f"{self.street_address}, {self.suburb}, {self.state} {self.postcode}"

    @property
    def full_address(self):
        return f"{self.street_address}, {self.suburb}, {self.state} {self.postcode}, {self.country}"


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

class EmailVerification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verifications"
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    objects = EmailVerificationManager()

    class Meta:
        db_table = "email_verifications"
        verbose_name = "Email Verification"
        verbose_name_plural = "Email Verifications"

    def __str__(self):
        return f"{self.user.email} - Verification"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class PasswordReset(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_resets"
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()

    objects = PasswordResetManager()

    class Meta:
        db_table = "password_resets"
        verbose_name = "Password Reset"
        verbose_name_plural = "Password Resets"

    def __str__(self):
        return f"{self.user.email} - Password Reset"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
