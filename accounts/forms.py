from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, ClientProfile, Address
from .validators import validate_australian_phone, validate_postcode


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First Name",
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last Name",
                "autocomplete": "family-name",
            }
        ),
    )
    phone_number = forms.CharField(
        required=False,
        validators=[validate_australian_phone],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+61 4XX XXX XXX",
                "autocomplete": "tel",
            }
        ),
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        initial="client",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    client_type = forms.ChoiceField(
        choices=User.CLIENT_TYPES,
        initial="general",
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "user_type",
            "client_type",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with this email already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        client_type = cleaned_data.get("client_type")

        if user_type == "client" and not client_type:
            cleaned_data["client_type"] = "general"
        elif user_type != "client":
            cleaned_data["client_type"] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data.get("phone_number", "")
        user.user_type = self.cleaned_data["user_type"]
        user.client_type = self.cleaned_data.get("client_type")

        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email Address",
                "autocomplete": "email",
                "autofocus": True,
            }
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, email=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    phone_number = forms.CharField(
        required=False,
        validators=[validate_australian_phone],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+61 4XX XXX XXX"}
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class ClientProfileForm(forms.ModelForm):
    ndis_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "NDIS Number (if applicable)",
            }
        ),
    )
    plan_manager = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Plan Manager Name"}
        ),
    )
    support_coordinator = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Support Coordinator Name"}
        ),
    )
    emergency_contact_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Emergency Contact Name"}
        ),
    )
    emergency_contact_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Emergency Contact Phone"}
        ),
    )
    accessibility_needs = forms.ChoiceField(
        choices=ClientProfile.ACCESSIBILITY_NEEDS,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    preferred_communication = forms.ChoiceField(
        choices=(
            ("email", "Email"),
            ("phone", "Phone"),
            ("sms", "SMS"),
            ("app", "App Notifications"),
        ),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Any special instructions or requirements",
            }
        ),
    )

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

    def clean_ndis_number(self):
        ndis_number = self.cleaned_data.get("ndis_number")
        if ndis_number and len(ndis_number) < 9:
            raise ValidationError(_("NDIS number must be at least 9 characters long."))
        return ndis_number


class AddressForm(forms.ModelForm):
    street_address = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Street Address"}
        )
    )
    suburb = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Suburb"})
    )
    state = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "State"})
    )
    postcode = forms.CharField(
        validators=[validate_postcode],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Postcode"}
        ),
    )
    country = forms.CharField(
        initial="Australia",
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": True}),
    )
    address_type = forms.ChoiceField(
        choices=Address.ADDRESS_TYPES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_primary = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    access_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Access instructions (e.g., gate code, parking)",
            }
        ),
    )

    class Meta:
        model = Address
        fields = (
            "address_type",
            "street_address",
            "suburb",
            "state",
            "postcode",
            "country",
            "is_primary",
            "access_instructions",
        )


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Current Password",
                "autocomplete": "current-password",
                "autofocus": True,
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm New Password",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                _("Your old password was entered incorrectly. Please enter it again.")
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email Address",
                "autocomplete": "email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_("No active user found with this email address."))
        return email


class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
                "autocomplete": "new-password",
            }
        ),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm New Password",
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class UserDeactivationForm(forms.Form):
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Reason for deactivation (optional)",
            }
        ),
    )
    confirm = forms.BooleanField(
        required=True, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    def clean_confirm(self):
        confirm = self.cleaned_data.get("confirm")
        if not confirm:
            raise ValidationError(_("You must confirm account deactivation."))
        return confirm


class BulkUserActionForm(forms.Form):
    ACTION_CHOICES = [
        ("activate", "Activate"),
        ("deactivate", "Deactivate"),
        ("verify", "Verify"),
        ("unverify", "Unverify"),
    ]

    user_ids = forms.CharField(widget=forms.HiddenInput())
    action = forms.ChoiceField(
        choices=ACTION_CHOICES, widget=forms.Select(attrs={"class": "form-control"})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Reason for this action (optional)",
            }
        ),
    )

    def clean_user_ids(self):
        user_ids_str = self.cleaned_data["user_ids"]
        try:
            user_ids = [int(id.strip()) for id in user_ids_str.split(",") if id.strip()]
            if not user_ids:
                raise ValidationError(_("No users selected."))
            return user_ids
        except ValueError:
            raise ValidationError(_("Invalid user IDs."))


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        )
    )
    phone = forms.CharField(
        required=False,
        validators=[validate_australian_phone],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Phone (optional)"}
        ),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "placeholder": "Your Message"}
        )
    )
    user_type = forms.ChoiceField(
        choices=[
            ("general", "General Inquiry"),
            ("ndis", "NDIS Client"),
            ("existing", "Existing Client"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
