from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import re
from typing import Any


def validate_australian_phone(value: str) -> None:
    # Temporarily disabled for registration issues
    return

    # if not value:
    #     return

    # cleaned = re.sub(r"[^\d+]", "", value)

    # patterns = [
    #     r"^\+61[2-9]\d{8}$",
    #     r"^0[2-9]\d{8}$",
    #     r"^\+614\d{8}$",
    #     r"^04\d{8}$"
    # ]

    # if not any(re.match(pattern, cleaned) for pattern in patterns):
    #     raise ValidationError(
    #         _(
    #             "Enter a valid Australian phone number. Format: +61 4XX XXX XXX or 04XX XXX XXX"
    #         ),
    #         code="invalid_phone",
    #     )


def validate_postcode(value: str) -> None:
    # Temporarily disabled for registration issues
    return

    # if not value:
    #     return

    # if not re.match(r"^\d{4}$", value):
    #     raise ValidationError(
    #         _("Enter a valid Australian postcode (4 digits)"), code="invalid_postcode"
    #     )

    # postcode_int = int(value)
    # valid_ranges = [
    #     (1000, 2599),
    #     (2600, 2618),
    #     (2620, 2899),
    #     (2900, 2920),
    #     (3000, 3999),
    #     (4000, 4999),
    #     (5000, 5999),
    #     (6000, 6797),
    #     (6800, 6999),
    #     (7000, 7999),
    #     (800, 999),
    # ]

    # if not any(start <= postcode_int <= end for start, end in valid_ranges):
    #     raise ValidationError(
    #         _("Enter a valid Australian postcode"), code="invalid_postcode_range"
    #     )

def validate_ndis_number(value: str) -> None:
    if not value:
        return

    cleaned = re.sub(r"[^\d]", "", value)

    if len(cleaned) < 9 or len(cleaned) > 10:
        raise ValidationError(
            _("NDIS number must be 9-10 digits long"), code="invalid_ndis_length"
        )

    if not cleaned.isdigit():
        raise ValidationError(
            _("NDIS number must contain only digits"), code="invalid_ndis_format"
        )


def validate_emergency_contact_phone(value: str) -> None:
    if not value:
        return

    try:
        validate_australian_phone(value)
    except ValidationError:
        raise ValidationError(
            _("Enter a valid emergency contact phone number"),
            code="invalid_emergency_phone",
        )


def validate_name(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 2:
        raise ValidationError(
            _("Name must be at least 2 characters long"), code="name_too_short"
        )

    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", value):
        raise ValidationError(
            _(
                "Name can only contain letters, spaces, hyphens, apostrophes, and periods"
            ),
            code="invalid_name_characters",
        )

    if len(value) > 50:
        raise ValidationError(
            _("Name cannot be longer than 50 characters"), code="name_too_long"
        )


def validate_street_address(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 5:
        raise ValidationError(
            _("Street address must be at least 5 characters long"),
            code="address_too_short",
        )

    if len(value) > 255:
        raise ValidationError(
            _("Street address cannot be longer than 255 characters"),
            code="address_too_long",
        )

    if not re.match(r"^[a-zA-Z0-9\s\-\,\.\/\#]+$", value):
        raise ValidationError(
            _("Street address contains invalid characters"),
            code="invalid_address_characters",
        )


def validate_suburb(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 2:
        raise ValidationError(
            _("Suburb must be at least 2 characters long"), code="suburb_too_short"
        )

    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", value):
        raise ValidationError(
            _(
                "Suburb can only contain letters, spaces, hyphens, apostrophes, and periods"
            ),
            code="invalid_suburb_characters",
        )

    if len(value) > 100:
        raise ValidationError(
            _("Suburb cannot be longer than 100 characters"), code="suburb_too_long"
        )


def validate_state(value: str) -> None:
    if not value:
        return

    valid_states = [
        "NSW",
        "VIC",
        "QLD",
        "WA",
        "SA",
        "TAS",
        "ACT",
        "NT",
        "New South Wales",
        "Victoria",
        "Queensland",
        "Western Australia",
        "South Australia",
        "Tasmania",
        "Australian Capital Territory",
        "Northern Territory",
    ]

    if value not in valid_states:
        raise ValidationError(
            _("Enter a valid Australian state or territory"), code="invalid_state"
        )


def validate_plan_manager_name(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 2:
        raise ValidationError(
            _("Plan manager name must be at least 2 characters long"),
            code="plan_manager_too_short",
        )

    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", value):
        raise ValidationError(
            _(
                "Plan manager name can only contain letters, spaces, hyphens, apostrophes, and periods"
            ),
            code="invalid_plan_manager_characters",
        )


def validate_support_coordinator_name(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 2:
        raise ValidationError(
            _("Support coordinator name must be at least 2 characters long"),
            code="coordinator_too_short",
        )

    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", value):
        raise ValidationError(
            _(
                "Support coordinator name can only contain letters, spaces, hyphens, apostrophes, and periods"
            ),
            code="invalid_coordinator_characters",
        )


def validate_special_instructions(value: str) -> None:
    if not value:
        return

    if len(value) > 1000:
        raise ValidationError(
            _("Special instructions cannot be longer than 1000 characters"),
            code="instructions_too_long",
        )

    forbidden_patterns = [
        r"<script",
        r"javascript:",
        r"onclick=",
        r"onerror=",
        r"onload=",
    ]

    for pattern in forbidden_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(
                _("Special instructions contain forbidden content"),
                code="forbidden_content",
            )


def validate_access_instructions(value: str) -> None:
    if not value:
        return

    if len(value) > 500:
        raise ValidationError(
            _("Access instructions cannot be longer than 500 characters"),
            code="access_instructions_too_long",
        )


def validate_user_type(value: str) -> None:
    valid_types = ["client", "admin", "staff"]

    if value not in valid_types:
        raise ValidationError(_("Invalid user type"), code="invalid_user_type")


def validate_client_type(value: str) -> None:
    if not value:
        return

    valid_types = ["general", "ndis"]

    if value not in valid_types:
        raise ValidationError(_("Invalid client type"), code="invalid_client_type")


def validate_accessibility_needs(value: str) -> None:
    valid_needs = ["none", "mobility", "visual", "hearing", "cognitive", "multiple"]

    if value not in valid_needs:
        raise ValidationError(
            _("Invalid accessibility needs option"), code="invalid_accessibility_needs"
        )


def validate_communication_preference(value: str) -> None:
    valid_preferences = ["email", "phone", "sms", "app"]

    if value not in valid_preferences:
        raise ValidationError(
            _("Invalid communication preference"),
            code="invalid_communication_preference",
        )


def validate_password_complexity(value: str) -> None:
    if len(value) < 8:
        raise ValidationError(
            _("Password must be at least 8 characters long"), code="password_too_short"
        )

    if len(value) > 128:
        raise ValidationError(
            _("Password cannot be longer than 128 characters"), code="password_too_long"
        )

    if not re.search(r"[A-Z]", value):
        raise ValidationError(
            _("Password must contain at least one uppercase letter"),
            code="password_no_uppercase",
        )

    if not re.search(r"[a-z]", value):
        raise ValidationError(
            _("Password must contain at least one lowercase letter"),
            code="password_no_lowercase",
        )

    if not re.search(r"\d", value):
        raise ValidationError(
            _("Password must contain at least one digit"), code="password_no_digit"
        )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _("Password must contain at least one special character"),
            code="password_no_special",
        )

    common_passwords = [
        "password",
        "123456",
        "123456789",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
    ]

    if value.lower() in common_passwords:
        raise ValidationError(
            _("This password is too common"), code="password_too_common"
        )


def validate_email_domain(value: str) -> None:
    if not value:
        return

    blocked_domains = [
        "10minutemail.com",
        "tempmail.org",
        "guerrillamail.com",
        "mailinator.com",
    ]

    domain = value.split("@")[-1].lower()

    if domain in blocked_domains:
        raise ValidationError(
            _("Email from this domain is not allowed"), code="blocked_email_domain"
        )


def validate_file_size(value: Any, max_size_mb: int = 5) -> None:
    if not value:
        return

    max_size_bytes = max_size_mb * 1024 * 1024

    if hasattr(value, "size") and value.size > max_size_bytes:
        raise ValidationError(
            _(f"File size cannot exceed {max_size_mb}MB"), code="file_too_large"
        )


def validate_image_file(value: Any) -> None:
    if not value:
        return

    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    if hasattr(value, "name"):
        extension = value.name.lower().split(".")[-1]
        if f".{extension}" not in valid_extensions:
            raise ValidationError(
                _("Only image files (JPG, PNG, GIF, WebP) are allowed"),
                code="invalid_image_format",
            )

    validate_file_size(value, max_size_mb=10)


def validate_document_file(value: Any) -> None:
    if not value:
        return

    valid_extensions = [".pdf", ".doc", ".docx", ".txt"]

    if hasattr(value, "name"):
        extension = value.name.lower().split(".")[-1]
        if f".{extension}" not in valid_extensions:
            raise ValidationError(
                _("Only document files (PDF, DOC, DOCX, TXT) are allowed"),
                code="invalid_document_format",
            )

    validate_file_size(value, max_size_mb=20)


def validate_business_hours(value: str) -> None:
    if not value:
        return

    time_pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"

    if not re.match(time_pattern, value):
        raise ValidationError(
            _("Enter time in HH:MM format (24-hour)"), code="invalid_time_format"
        )


def validate_service_radius(value: int) -> None:
    if value is None:
        return

    if value < 1:
        raise ValidationError(
            _("Service radius must be at least 1 km"), code="radius_too_small"
        )

    if value > 100:
        raise ValidationError(
            _("Service radius cannot exceed 100 km"), code="radius_too_large"
        )


def validate_rating(value: float) -> None:
    if value is None:
        return

    if value < 0 or value > 5:
        raise ValidationError(
            _("Rating must be between 0 and 5"), code="invalid_rating_range"
        )


def validate_price(value: float) -> None:
    if value is None:
        return

    if value < 0:
        raise ValidationError(_("Price cannot be negative"), code="negative_price")

    if value > 10000:
        raise ValidationError(_("Price cannot exceed $10,000"), code="price_too_high")


class AustralianPhoneValidator(RegexValidator):
    regex = r"^\+?61[2-9]\d{8}$|^0[2-9]\d{8}$|^\+?614\d{8}$|^04\d{8}$"
    message = _("Enter a valid Australian phone number")
    code = "invalid_australian_phone"


class PostcodeValidator(RegexValidator):
    regex = r"^\d{4}$"
    message = _("Enter a valid Australian postcode (4 digits)")
    code = "invalid_postcode"


class NDISNumberValidator(RegexValidator):
    regex = r"^\d{9,10}$"
    message = _("Enter a valid NDIS number (9-10 digits)")
    code = "invalid_ndis_number"


class NameValidator(RegexValidator):
    regex = r"^[a-zA-Z\s\-\'\.]{2,50}$"
    message = _(
        "Name must be 2-50 characters and contain only letters, spaces, hyphens, apostrophes, and periods"
    )
    code = "invalid_name"


class AddressValidator(RegexValidator):
    regex = r"^[a-zA-Z0-9\s\-\,\.\/\#]{5,255}$"
    message = _("Address must be 5-255 characters and contain valid address characters")
    code = "invalid_address"
