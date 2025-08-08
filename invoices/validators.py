from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re
from datetime import datetime, date
from typing import Any


def validate_invoice_number(value: str) -> None:
    pattern = r"^INV-\d{4}-\d{4}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Invoice number must be in format INV-YYYY-NNNN",
            code="invalid_invoice_number",
        )


def validate_ndis_number(value: str) -> None:
    if not value:
        return

    cleaned = "".join(filter(str.isdigit, value))
    if len(cleaned) != 9:
        raise ValidationError(
            "NDIS number must contain exactly 9 digits", code="invalid_ndis_number"
        )


def validate_abn_number(value: str) -> None:
    if not value:
        return

    cleaned = "".join(filter(str.isdigit, value))
    if len(cleaned) != 11:
        raise ValidationError("ABN must contain exactly 11 digits", code="invalid_abn")

    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    digits = [int(d) for d in cleaned]
    digits[0] -= 1

    total = sum(digit * weight for digit, weight in zip(digits, weights))

    if total % 89 != 0:
        raise ValidationError("Invalid ABN number", code="invalid_abn")


def validate_positive_decimal(value: Decimal) -> None:
    if value < 0:
        raise ValidationError("Value must be positive", code="negative_value")


def validate_payment_amount(value: Decimal) -> None:
    if value <= 0:
        raise ValidationError(
            "Payment amount must be greater than zero", code="invalid_payment_amount"
        )

    if value.as_tuple().exponent < -2:
        raise ValidationError(
            "Payment amount cannot have more than 2 decimal places",
            code="too_many_decimals",
        )


def validate_gst_rate(value: Decimal) -> None:
    if not (0 <= value <= 1):
        raise ValidationError(
            "GST rate must be between 0 and 1", code="invalid_gst_rate"
        )


def validate_due_date(value: date) -> None:
    if value < timezone.now().date():
        raise ValidationError("Due date cannot be in the past", code="past_due_date")


def validate_service_date_range(start_date: date, end_date: date) -> None:
    if start_date > end_date:
        raise ValidationError(
            "Service start date must be before end date", code="invalid_date_range"
        )

    if end_date > timezone.now().date():
        raise ValidationError(
            "Service end date cannot be in the future", code="future_service_date"
        )


def validate_payment_terms(value: int) -> None:
    if value < 0:
        raise ValidationError(
            "Payment terms must be non-negative", code="negative_payment_terms"
        )

    if value > 365:
        raise ValidationError(
            "Payment terms cannot exceed 365 days", code="excessive_payment_terms"
        )


def validate_invoice_status_transition(current_status: str, new_status: str) -> None:
    valid_transitions = {
        "draft": ["sent", "cancelled"],
        "sent": ["paid", "overdue", "cancelled"],
        "overdue": ["paid", "cancelled"],
        "paid": [],
        "cancelled": ["draft"],
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise ValidationError(
            f"Cannot change status from {current_status} to {new_status}",
            code="invalid_status_transition",
        )


def validate_quantity(value: Decimal) -> None:
    if value <= 0:
        raise ValidationError(
            "Quantity must be greater than zero", code="invalid_quantity"
        )

    if value > 9999:
        raise ValidationError("Quantity cannot exceed 9999", code="excessive_quantity")


def validate_unit_price(value: Decimal) -> None:
    if value < 0:
        raise ValidationError(
            "Unit price cannot be negative", code="negative_unit_price"
        )

    if value > Decimal("999999.99"):
        raise ValidationError(
            "Unit price cannot exceed $999,999.99", code="excessive_unit_price"
        )


def validate_email_address(value: str) -> None:
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, value):
        raise ValidationError("Enter a valid email address", code="invalid_email")


def validate_phone_number(value: str) -> None:
    if not value:
        return

    phone_pattern = r"^\+?1?\d{9,15}$"
    if not re.match(phone_pattern, value):
        raise ValidationError(
            'Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.',
            code="invalid_phone_number",
        )


def validate_postcode(value: str) -> None:
    if not value:
        return

    if not re.match(r"^\d{4}$", value):
        raise ValidationError(
            "Postcode must be exactly 4 digits", code="invalid_postcode"
        )


def validate_file_size(value: Any) -> None:
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(value, "size") and value.size > max_size:
        raise ValidationError("File size cannot exceed 10MB", code="file_too_large")


def validate_pdf_file(value: Any) -> None:
    if not hasattr(value, "name"):
        return

    if not value.name.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are allowed", code="invalid_file_type")


def validate_invoice_item_description(value: str) -> None:
    if len(value.strip()) < 3:
        raise ValidationError(
            "Description must be at least 3 characters long",
            code="description_too_short",
        )

    if len(value) > 500:
        raise ValidationError(
            "Description cannot exceed 500 characters", code="description_too_long"
        )


def validate_participant_name(value: str) -> None:
    if not value or not value.strip():
        raise ValidationError(
            "Participant name is required for NDIS invoices",
            code="missing_participant_name",
        )

    if len(value.strip()) < 2:
        raise ValidationError(
            "Participant name must be at least 2 characters long",
            code="participant_name_too_short",
        )


def validate_provider_registration(value: str) -> None:
    if not value:
        return

    if not re.match(r"^\d{8}$", value):
        raise ValidationError(
            "Provider registration must be exactly 8 digits",
            code="invalid_provider_registration",
        )


def validate_invoice_total_consistency(
    subtotal: Decimal, gst_amount: Decimal, total_amount: Decimal
) -> None:
    calculated_total = subtotal + gst_amount

    if abs(calculated_total - total_amount) > Decimal("0.01"):
        raise ValidationError(
            "Invoice total does not match subtotal plus GST", code="inconsistent_totals"
        )


def validate_payment_allocation(
    payment_amount: Decimal, invoice_total: Decimal, existing_payments: Decimal
) -> None:
    remaining_balance = invoice_total - existing_payments

    if payment_amount > remaining_balance:
        raise ValidationError(
            "Payment amount exceeds remaining invoice balance", code="excessive_payment"
        )


def validate_business_hours(value: Any) -> None:
    if hasattr(value, "hour"):
        if not (6 <= value.hour <= 22):
            raise ValidationError(
                "Service time must be between 6:00 AM and 10:00 PM",
                code="outside_business_hours",
            )


def validate_future_date(value: date) -> None:
    if value <= timezone.now().date():
        raise ValidationError("Date must be in the future", code="past_date")


def validate_currency_code(value: str) -> None:
    valid_currencies = ["AUD", "USD", "EUR", "GBP"]
    if value not in valid_currencies:
        raise ValidationError(
            f'Currency must be one of: {", ".join(valid_currencies)}',
            code="invalid_currency",
        )
