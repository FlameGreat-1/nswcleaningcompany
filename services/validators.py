from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from decimal import Decimal, InvalidOperation
import re
from typing import Any


def validate_postcode(value: str) -> None:
    if not value:
        return

    if not re.match(r"^\d{4}$", value):
        raise ValidationError(
            _("Enter a valid Australian postcode (4 digits)"), code="invalid_postcode"
        )

    postcode_int = int(value)
    valid_ranges = [
        (1000, 2599),
        (2600, 2618),
        (2620, 2899),
        (2900, 2920),
        (3000, 3999),
        (4000, 4999),
        (5000, 5999),
        (6000, 6797),
        (6800, 6999),
        (7000, 7999),
        (800, 999),
    ]

    if not any(start <= postcode_int <= end for start, end in valid_ranges):
        raise ValidationError(
            _("Enter a valid Australian postcode"), code="invalid_postcode_range"
        )


def validate_service_duration(value: int) -> None:
    if value is None:
        return

    if value <= 0:
        raise ValidationError(
            _("Service duration must be greater than 0"), code="invalid_duration"
        )

    if value > 480:
        raise ValidationError(
            _("Service duration cannot exceed 480 minutes (8 hours)"),
            code="duration_too_long",
        )


def validate_ndis_service_code(value: str) -> None:
    if not value:
        return

    if not re.match(r"^[0-9]{2}_[0-9]{3}_[0-9]{4}_[0-9]_[0-9]$", value):
        raise ValidationError(
            _("NDIS service code must follow format: XX_XXX_XXXX_X_X"),
            code="invalid_ndis_code_format",
        )

    parts = value.split("_")
    if len(parts) != 5:
        raise ValidationError(
            _("NDIS service code must have 5 parts separated by underscores"),
            code="invalid_ndis_code_structure",
        )

    try:
        support_category = int(parts[0])
        if not (1 <= support_category <= 15):
            raise ValidationError(
                _("NDIS support category must be between 01 and 15"),
                code="invalid_support_category",
            )
    except ValueError:
        raise ValidationError(
            _("Invalid NDIS support category format"),
            code="invalid_support_category_format",
        )


def validate_pricing(value: Decimal) -> None:
    if value is None:
        return

    if value < Decimal("0.01"):
        raise ValidationError(_("Price must be at least $0.01"), code="price_too_low")

    if value > Decimal("10000.00"):
        raise ValidationError(
            _("Price cannot exceed $10,000.00"), code="price_too_high"
        )

    if value.as_tuple().exponent < -2:
        raise ValidationError(
            _("Price cannot have more than 2 decimal places"),
            code="too_many_decimal_places",
        )


def validate_service_name(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 3:
        raise ValidationError(
            _("Service name must be at least 3 characters long"), code="name_too_short"
        )

    if len(value) > 200:
        raise ValidationError(
            _("Service name cannot exceed 200 characters"), code="name_too_long"
        )

    if not re.match(r"^[a-zA-Z0-9\s\-\&\(\)\.\/]+$", value):
        raise ValidationError(
            _("Service name contains invalid characters"),
            code="invalid_name_characters",
        )


def validate_service_description(value: str) -> None:
    if not value:
        return

    if len(value.strip()) < 10:
        raise ValidationError(
            _("Service description must be at least 10 characters long"),
            code="description_too_short",
        )

    if len(value) > 2000:
        raise ValidationError(
            _("Service description cannot exceed 2000 characters"),
            code="description_too_long",
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
                _("Service description contains forbidden content"),
                code="forbidden_content",
            )


def validate_hourly_rate(value: Decimal) -> None:
    if value is None:
        return

    if value < Decimal("15.00"):
        raise ValidationError(
            _("Hourly rate must be at least $15.00 (minimum wage compliance)"),
            code="rate_below_minimum",
        )

    if value > Decimal("500.00"):
        raise ValidationError(
            _("Hourly rate cannot exceed $500.00"), code="rate_too_high"
        )


def validate_room_count(value: int) -> None:
    if value is None:
        return

    if value < 1:
        raise ValidationError(
            _("Room count must be at least 1"), code="invalid_room_count"
        )

    if value > 50:
        raise ValidationError(_("Room count cannot exceed 50"), code="too_many_rooms")


def validate_square_meters(value: Decimal) -> None:
    if value is None:
        return

    if value <= Decimal("0"):
        raise ValidationError(
            _("Square meters must be greater than 0"), code="invalid_square_meters"
        )

    if value > Decimal("10000"):
        raise ValidationError(
            _("Square meters cannot exceed 10,000"), code="area_too_large"
        )


def validate_travel_time(value: int) -> None:
    if value is None:
        return

    if value < 0:
        raise ValidationError(
            _("Travel time cannot be negative"), code="negative_travel_time"
        )

    if value > 300:
        raise ValidationError(
            _("Travel time cannot exceed 300 minutes (5 hours)"),
            code="travel_time_too_long",
        )


def validate_service_radius(value: int) -> None:
    if value is None:
        return

    if value < 1:
        raise ValidationError(
            _("Service radius must be at least 1 km"), code="radius_too_small"
        )

    if value > 200:
        raise ValidationError(
            _("Service radius cannot exceed 200 km"), code="radius_too_large"
        )


def validate_priority_level(value: int) -> None:
    if value is None:
        return

    if not (1 <= value <= 5):
        raise ValidationError(
            _("Priority level must be between 1 and 5"), code="invalid_priority_level"
        )


def validate_display_order(value: int) -> None:
    if value is None:
        return

    if value < 0:
        raise ValidationError(
            _("Display order cannot be negative"), code="negative_display_order"
        )

    if value > 9999:
        raise ValidationError(
            _("Display order cannot exceed 9999"), code="display_order_too_high"
        )


def validate_max_bookings(value: int) -> None:
    if value is None:
        return

    if value < 1:
        raise ValidationError(
            _("Maximum bookings must be at least 1"), code="invalid_max_bookings"
        )

    if value > 100:
        raise ValidationError(
            _("Maximum bookings cannot exceed 100 per time slot"),
            code="too_many_bookings",
        )


def validate_service_time_slot(start_time, end_time) -> None:
    if not start_time or not end_time:
        return

    if start_time >= end_time:
        raise ValidationError(
            _("End time must be after start time"), code="invalid_time_range"
        )

    duration_minutes = (end_time.hour * 60 + end_time.minute) - (
        start_time.hour * 60 + start_time.minute
    )

    if duration_minutes < 30:
        raise ValidationError(
            _("Service time slot must be at least 30 minutes"),
            code="time_slot_too_short",
        )

    if duration_minutes > 480:
        raise ValidationError(
            _("Service time slot cannot exceed 8 hours"), code="time_slot_too_long"
        )


def validate_effective_date_range(effective_from, effective_to) -> None:
    if not effective_from:
        return

    if effective_to and effective_from >= effective_to:
        raise ValidationError(
            _("Effective end date must be after start date"), code="invalid_date_range"
        )


def validate_addon_price(value: Decimal) -> None:
    if value is None:
        return

    if value < Decimal("0.01"):
        raise ValidationError(
            _("Add-on price must be at least $0.01"), code="addon_price_too_low"
        )

    if value > Decimal("1000.00"):
        raise ValidationError(
            _("Add-on price cannot exceed $1,000.00"), code="addon_price_too_high"
        )


def validate_equipment_list(value: str) -> None:
    if not value:
        return

    if len(value) > 1000:
        raise ValidationError(
            _("Equipment list cannot exceed 1000 characters"),
            code="equipment_list_too_long",
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
                _("Equipment list contains forbidden content"), code="forbidden_content"
            )


def validate_special_requirements(value: str) -> None:
    if not value:
        return

    if len(value) > 2000:
        raise ValidationError(
            _("Special requirements cannot exceed 2000 characters"),
            code="requirements_too_long",
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
                _("Special requirements contain forbidden content"),
                code="forbidden_content",
            )


def validate_service_slug(value: str) -> None:
    if not value:
        return

    if not re.match(r"^[a-z0-9\-]+$", value):
        raise ValidationError(
            _("Slug can only contain lowercase letters, numbers, and hyphens"),
            code="invalid_slug_format",
        )

    if len(value) < 3:
        raise ValidationError(
            _("Slug must be at least 3 characters long"), code="slug_too_short"
        )

    if len(value) > 200:
        raise ValidationError(
            _("Slug cannot exceed 200 characters"), code="slug_too_long"
        )

    if value.startswith("-") or value.endswith("-"):
        raise ValidationError(
            _("Slug cannot start or end with a hyphen"), code="invalid_slug_hyphens"
        )

    if "--" in value:
        raise ValidationError(
            _("Slug cannot contain consecutive hyphens"), code="consecutive_hyphens"
        )


class PostcodeValidator(RegexValidator):
    regex = r"^\d{4}$"
    message = _("Enter a valid Australian postcode (4 digits)")
    code = "invalid_postcode"


class NDISServiceCodeValidator(RegexValidator):
    regex = r"^[0-9]{2}_[0-9]{3}_[0-9]{4}_[0-9]_[0-9]$"
    message = _("Enter a valid NDIS service code (format: XX_XXX_XXXX_X_X)")
    code = "invalid_ndis_service_code"


class ServiceNameValidator(RegexValidator):
    regex = r"^[a-zA-Z0-9\s\-\&\(\)\.\/]{3,200}$"
    message = _(
        "Service name must be 3-200 characters and contain only valid characters"
    )
    code = "invalid_service_name"


class ServiceSlugValidator(RegexValidator):
    regex = r"^[a-z0-9\-]{3,200}$"
    message = _(
        "Slug must be 3-200 characters and contain only lowercase letters, numbers, and hyphens"
    )
    code = "invalid_service_slug"
