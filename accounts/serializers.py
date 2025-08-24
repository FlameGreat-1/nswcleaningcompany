from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    User,
    ClientProfile,
    Address,
    EmailVerification,
    PasswordReset,
    SocialAuthProfile,
)
from .validators import validate_australian_phone, validate_postcode

class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(
        required=True, help_text="Google ID token or access token"
    )
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, default="client")
    client_type = serializers.ChoiceField(
        choices=User.CLIENT_TYPES, default="general", required=False
    )

    def validate(self, attrs):
        if attrs.get("user_type") == "client" and not attrs.get("client_type"):
            attrs["client_type"] = "general"
        return attrs

class GoogleRegistrationSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPES, default="client")
    client_type = serializers.ChoiceField(
        choices=User.CLIENT_TYPES, default="general", required=False
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        ## validators=[validate_australian_phone]  
    )

    def validate(self, attrs):
        if attrs.get("user_type") == "client" and not attrs.get("client_type"):
            attrs["client_type"] = "general"
        return attrs


class SocialAuthProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    is_token_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = SocialAuthProfile
        fields = (
            "id",
            "user_email",
            "provider",
            "provider_id",
            "provider_email",
            "token_expires_at",
            "is_active",
            "is_token_expired",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user_email",
            "provider_id",
            "provider_email",
            "token_expires_at",
            "is_token_expired",
            "created_at",
            "updated_at",
        )

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True, required=False
    )  
    confirm_password = serializers.CharField(
        write_only=True, required=False
    )  
    phone_number = serializers.CharField(
        required=False
        ## required=False, validators=[validate_australian_phone]
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "confirm_password", 
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "client_type",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        password = attrs.get("password")


        password_confirm = attrs.get("password_confirm") or attrs.get(
            "confirm_password"
        )

        if not password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation is required."}
            )

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        if attrs.get("user_type") == "client" and not attrs.get("client_type"):
            attrs["client_type"] = "general"

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Must include email and password.")

        attrs["user"] = user
        return attrs


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=SocialAuthProfile.PROVIDER_CHOICES)
    access_token = serializers.CharField(required=True)

    def validate(self, attrs):
        provider = attrs.get("provider")
        access_token = attrs.get("access_token")

        if not provider or not access_token:
            raise serializers.ValidationError("Provider and access token are required.")

        attrs["provider"] = provider
        attrs["access_token"] = access_token
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if user.auth_provider == "google":
            raise serializers.ValidationError("Google users cannot change password.")
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password": "New password fields didn't match."}
            )
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)
            if user.auth_provider == "google":
                raise serializers.ValidationError("Google users cannot reset password.")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No active user found with this email address."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_token(self, value):
        try:
            reset = PasswordReset.objects.get(token=value, is_used=False)
            if not reset.is_valid:
                raise serializers.ValidationError("Token is expired or invalid.")
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
            "client_type",
            "is_active",
        )
        read_only_fields = ("id", "full_name", "user_type", "client_type")
class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            verification = EmailVerification.objects.get(token=value, is_used=False)
            if not verification.is_valid:
                raise serializers.ValidationError("Token is expired or invalid.")
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
        return value


class AddressSerializer(serializers.ModelSerializer):
    ## postcode = serializers.CharField(validators=[validate_postcode])

    class Meta:
        model = Address
        fields = (
            "id",
            "address_type",
            "street_address",
            "suburb",
            "state",
            "postcode",
            "country",
            "is_primary",
            "access_instructions",
            "full_address",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "full_address", "created_at", "updated_at")

    def validate(self, attrs):
        user = self.context["request"].user
        address_type = attrs.get("address_type")

        if self.instance is None:
            if Address.objects.filter(user=user, address_type=address_type).exists():
                raise serializers.ValidationError(
                    f"You already have a {address_type} address. Please update the existing one."
                )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ClientProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    is_ndis_eligible = serializers.BooleanField(read_only=True)

    class Meta:
        model = ClientProfile
        fields = (
            "id",
            "user_email",
            "user_full_name",
            "ndis_number",
            "plan_manager",
            "support_coordinator",
            "emergency_contact_name",
            "emergency_contact_phone",
            "accessibility_needs",
            "special_instructions",
            "preferred_communication",
            "is_ndis_eligible",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user_email",
            "user_full_name",
            "is_ndis_eligible",
            "created_at",
            "updated_at",
        )

    def validate_ndis_number(self, value):
        if value and len(value) < 9:
            raise serializers.ValidationError(
                "NDIS number must be at least 9 characters long."
            )
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    client_profile = ClientProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)
    social_profiles = SocialAuthProfileSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(
        ## validators=[validate_australian_phone], required=False
    )
    is_google_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "user_type",
            "client_type",
            "auth_provider",
            "avatar_url",
            "is_verified",
            "date_joined",
            "last_login",
            "is_google_user",
            "client_profile",
            "addresses",
            "social_profiles",
        )
        read_only_fields = (
            "id",
            "email",
            "user_type",
            "client_type",
            "auth_provider",
            "is_verified",
            "date_joined",
            "last_login",
            "full_name",
            "is_google_user",
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    client_type_display = serializers.CharField(
        source="get_client_type_display", read_only=True
    )
    user_type_display = serializers.CharField(
        source="get_user_type_display", read_only=True
    )
    auth_provider_display = serializers.CharField(
        source="get_auth_provider_display", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "user_type",
            "user_type_display",
            "client_type",
            "client_type_display",
            "auth_provider",
            "auth_provider_display",
            "is_active",
            "is_verified",
            "date_joined",
            "last_login",
        )


class ClientProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = (
            "ndis_number",
            "plan_manager",
            "support_coordinator",
            "emergency_contact_name",
            "emergency_contact_phone",
            "accessibility_needs",
            "special_instructions",
            "preferred_communication",
        )

    def validate_ndis_number(self, value):
        if value and len(value) < 9:
            raise serializers.ValidationError(
                "NDIS number must be at least 9 characters long."
            )
        return value


class UserDeactivationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, max_length=500)
    confirm = serializers.BooleanField(required=True)

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("You must confirm account deactivation.")
        return value


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)
            if user.is_verified:
                raise serializers.ValidationError("This email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No active user found with this email address."
            )
        return value


class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    client_users = serializers.IntegerField()
    ndis_clients = serializers.IntegerField()
    general_clients = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    admin_users = serializers.IntegerField()
    google_users = serializers.IntegerField()
    recent_registrations = serializers.IntegerField()


class BulkUserActionSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=100
    )
    action = serializers.ChoiceField(
        choices=[
            ("activate", "Activate"),
            ("deactivate", "Deactivate"),
            ("verify", "Verify"),
            ("unverify", "Unverify"),
        ]
    )
    reason = serializers.CharField(required=False, max_length=500)

    def validate_user_ids(self, value):
        existing_ids = User.objects.filter(id__in=value).values_list("id", flat=True)
        if len(existing_ids) != len(value):
            missing_ids = set(value) - set(existing_ids)
            raise serializers.ValidationError(
                f"Users with IDs {list(missing_ids)} do not exist."
            )
        return value


class SocialProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAuthProfile
        fields = ("is_active",)


class AccountLinkingSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=SocialAuthProfile.PROVIDER_CHOICES)
    access_token = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context["request"].user
        provider = attrs.get("provider")

        if SocialAuthProfile.objects.filter(
            user=user, provider=provider, is_active=True
        ).exists():
            raise serializers.ValidationError(
                f"{provider.title()} account is already linked."
            )

        return attrs


class AccountUnlinkingSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=SocialAuthProfile.PROVIDER_CHOICES)

    def validate_provider(self, value):
        user = self.context["request"].user

        if not SocialAuthProfile.objects.filter(
            user=user, provider=value, is_active=True
        ).exists():
            raise serializers.ValidationError(
                f"No active {value.title()} account found."
            )

        if user.auth_provider == value and not user.has_usable_password:
            raise serializers.ValidationError(
                f"Cannot unlink {value.title()} account. Set a password first."
            )

        return value
