from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator
from decimal import Decimal, InvalidOperation
import re
from datetime import datetime, timedelta
import mimetypes
import os


def validate_quote_number(value):
    if not value:
        raise ValidationError("Quote number is required.")
    
    pattern = r'^QT-\d{4}-\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            "Quote number must be in format QT-YYYY-NNNN (e.g., QT-2024-0001)"
        )
    
    year_part = value.split('-')[1]
    current_year = timezone.now().year
    if int(year_part) > current_year + 1:
        raise ValidationError("Quote number year cannot be more than one year in the future.")


def validate_urgency_level(value):
    if not isinstance(value, int):
        raise ValidationError("Urgency level must be an integer.")
    
    if value < 1 or value > 5:
        raise ValidationError("Urgency level must be between 1 and 5.")


def validate_room_count(value):
    if not isinstance(value, int):
        raise ValidationError("Room count must be an integer.")
    
    if value < 1:
        raise ValidationError("Room count must be at least 1.")
    
    if value > 50:
        raise ValidationError("Room count cannot exceed 50.")


def validate_square_meters(value):
    if value is None:
        return
    
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError("Square meters must be a valid decimal number.")
    
    if decimal_value <= 0:
        raise ValidationError("Square meters must be greater than 0.")
    
    if decimal_value > Decimal('10000'):
        raise ValidationError("Square meters cannot exceed 10,000.")


def validate_postcode(value):
    if not value:
        raise ValidationError("Postcode is required.")
    
    if not value.isdigit():
        raise ValidationError("Postcode must contain only digits.")
    
    if len(value) != 4:
        raise ValidationError("Postcode must be exactly 4 digits.")
    
    postcode_int = int(value)
    if postcode_int < 1000 or postcode_int > 9999:
        raise ValidationError("Postcode must be between 1000 and 9999.")


def validate_ndis_participant_number(value):
    if not value:
        return
    
    if not value.isdigit():
        raise ValidationError("NDIS participant number must contain only digits.")
    
    if len(value) != 9:
        raise ValidationError("NDIS participant number must be exactly 9 digits.")


def validate_phone_number(value):
    if not value:
        return
    
    phone_pattern = r'^(\+61|0)[2-9]\d{8}$'
    if not re.match(phone_pattern, value):
        raise ValidationError(
            "Phone number must be a valid Australian number (e.g., 0412345678 or +61412345678)"
        )


def validate_file_size(file):
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(f"File size cannot exceed 10MB. Current size: {file.size / (1024*1024):.1f}MB")


def validate_image_file(file):
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
    
    file_type = mimetypes.guess_type(file.name)[0]
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_type not in allowed_types:
        raise ValidationError(
            f"File type '{file_type}' not allowed. Allowed types: JPG, PNG, GIF, PDF"
        )
    
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f"File extension '{file_extension}' not allowed. Allowed extensions: .jpg, .jpeg, .png, .gif, .pdf"
        )


def validate_preferred_date(value):
    if not value:
        return
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Date must be in YYYY-MM-DD format.")
    
    today = timezone.now().date()
    if value < today:
        raise ValidationError("Preferred date cannot be in the past.")
    
    max_future_date = today + timedelta(days=365)
    if value > max_future_date:
        raise ValidationError("Preferred date cannot be more than one year in the future.")


def validate_preferred_time(value):
    if not value:
        return
    
    if isinstance(value, str):
        try:
            datetime.strptime(value, '%H:%M')
        except ValueError:
            raise ValidationError("Time must be in HH:MM format.")


def validate_price_amount(value):
    if value is None:
        return
    
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError("Price must be a valid decimal number.")
    
    if decimal_value < 0:
        raise ValidationError("Price cannot be negative.")
    
    if decimal_value > Decimal('100000'):
        raise ValidationError("Price cannot exceed $100,000.")
    
    if decimal_value.as_tuple().exponent < -2:
        raise ValidationError("Price cannot have more than 2 decimal places.")


def validate_gst_amount(base_amount, gst_amount):
    if base_amount is None or gst_amount is None:
        return
    
    try:
        base_decimal = Decimal(str(base_amount))
        gst_decimal = Decimal(str(gst_amount))
    except (InvalidOperation, ValueError):
        raise ValidationError("GST calculation values must be valid decimal numbers.")
    
    expected_gst = (base_decimal * Decimal('0.10')).quantize(Decimal('0.01'))
    
    if abs(gst_decimal - expected_gst) > Decimal('0.01'):
        raise ValidationError(
            f"GST amount {gst_decimal} does not match expected GST {expected_gst} for base amount {base_decimal}"
        )


def validate_quote_status_transition(current_status, new_status):
    valid_transitions = {
        'draft': ['submitted', 'cancelled'],
        'submitted': ['under_review', 'approved', 'rejected', 'cancelled'],
        'under_review': ['approved', 'rejected', 'submitted'],
        'approved': ['converted', 'expired', 'cancelled'],
        'rejected': ['submitted', 'cancelled'],
        'expired': ['cancelled'],
        'converted': [],
        'cancelled': []
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise ValidationError(
            f"Cannot change status from '{current_status}' to '{new_status}'. "
            f"Valid transitions: {', '.join(valid_transitions.get(current_status, []))}"
        )


def validate_cleaning_type_service_compatibility(cleaning_type, service):
    if not service:
        return
    
    compatible_types = {
        'general': ['general', 'deep', 'commercial'],
        'deep': ['deep', 'general'],
        'end_of_lease': ['end_of_lease', 'deep'],
        'ndis': ['ndis', 'general'],
        'commercial': ['commercial', 'general'],
        'carpet': ['carpet'],
        'window': ['window'],
        'pressure_washing': ['pressure_washing']
    }
    
    service_types = compatible_types.get(cleaning_type, [])
    if service.service_type not in service_types:
        raise ValidationError(
            f"Service type '{service.service_type}' is not compatible with cleaning type '{cleaning_type}'"
        )


def validate_ndis_quote_requirements(is_ndis_client, ndis_participant_number, service):
    if is_ndis_client:
        if not ndis_participant_number:
            raise ValidationError("NDIS participant number is required for NDIS clients.")
        
        if service and not service.is_ndis_eligible:
            raise ValidationError("Selected service is not NDIS eligible.")


def validate_service_area_coverage(service, postcode):
    if not service or not postcode:
        return
    
    if not service.service_areas.filter(postcode=postcode, is_active=True).exists():
        raise ValidationError(
            f"Service '{service.name}' is not available in postcode {postcode}"
        )

def validate_quote_expiry_date(expires_at, status):
    if not expires_at:
        return
    
    if status != 'approved':
        raise ValidationError("Expiry date can only be set for approved quotes.")
    
    now = timezone.now()
    if expires_at <= now:
        raise ValidationError("Expiry date must be in the future.")
    
    max_expiry = now + timedelta(days=90)
    if expires_at > max_expiry:
        raise ValidationError("Quote cannot be valid for more than 90 days.")


def validate_quote_item_quantity(quantity):
    if quantity is None:
        raise ValidationError("Quantity is required.")
    
    try:
        decimal_quantity = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise ValidationError("Quantity must be a valid decimal number.")
    
    if decimal_quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    
    if decimal_quantity > Decimal('1000'):
        raise ValidationError("Quantity cannot exceed 1000.")


def validate_quote_item_unit_price(unit_price):
    if unit_price is None:
        raise ValidationError("Unit price is required.")
    
    validate_price_amount(unit_price)


def validate_attachment_filename(filename):
    if not filename:
        raise ValidationError("Filename is required.")
    
    if len(filename) > 255:
        raise ValidationError("Filename cannot exceed 255 characters.")
    
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        if char in filename:
            raise ValidationError(f"Filename cannot contain '{char}' character.")


def validate_revision_reason(reason):
    if not reason or not reason.strip():
        raise ValidationError("Revision reason is required.")
    
    if len(reason.strip()) < 10:
        raise ValidationError("Revision reason must be at least 10 characters long.")
    
    if len(reason) > 1000:
        raise ValidationError("Revision reason cannot exceed 1000 characters.")


def validate_template_name(name):
    if not name or not name.strip():
        raise ValidationError("Template name is required.")
    
    if len(name.strip()) < 3:
        raise ValidationError("Template name must be at least 3 characters long.")
    
    if len(name) > 200:
        raise ValidationError("Template name cannot exceed 200 characters.")


def validate_special_requirements(requirements):
    if not requirements:
        return
    
    if len(requirements) > 2000:
        raise ValidationError("Special requirements cannot exceed 2000 characters.")
    
    forbidden_words = ['illegal', 'dangerous', 'hazardous', 'toxic']
    requirements_lower = requirements.lower()
    for word in forbidden_words:
        if word in requirements_lower:
            raise ValidationError(f"Special requirements cannot contain '{word}'.")


def validate_access_instructions(instructions):
    if not instructions:
        return
    
    if len(instructions) > 1000:
        raise ValidationError("Access instructions cannot exceed 1000 characters.")


def validate_admin_notes(notes):
    if not notes:
        return
    
    if len(notes) > 2000:
        raise ValidationError("Admin notes cannot exceed 2000 characters.")


def validate_client_notes(notes):
    if not notes:
        return
    
    if len(notes) > 1000:
        raise ValidationError("Client notes cannot exceed 1000 characters.")


def validate_rejection_reason(reason):
    if not reason or not reason.strip():
        raise ValidationError("Rejection reason is required.")
    
    if len(reason.strip()) < 10:
        raise ValidationError("Rejection reason must be at least 10 characters long.")
    
    if len(reason) > 1000:
        raise ValidationError("Rejection reason cannot exceed 1000 characters.")


def validate_property_address(address):
    if not address or not address.strip():
        raise ValidationError("Property address is required.")
    
    if len(address.strip()) < 10:
        raise ValidationError("Property address must be at least 10 characters long.")
    
    if len(address) > 500:
        raise ValidationError("Property address cannot exceed 500 characters.")


def validate_suburb_name(suburb):
    if not suburb or not suburb.strip():
        raise ValidationError("Suburb is required.")
    
    if len(suburb.strip()) < 2:
        raise ValidationError("Suburb must be at least 2 characters long.")
    
    if len(suburb) > 100:
        raise ValidationError("Suburb cannot exceed 100 characters.")
    
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', suburb):
        raise ValidationError("Suburb can only contain letters, spaces, hyphens, apostrophes, and periods.")


def validate_state_code(state):
    valid_states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
    if state not in valid_states:
        raise ValidationError(f"State must be one of: {', '.join(valid_states)}")


def validate_contact_name(name):
    if not name:
        return
    
    if len(name.strip()) < 2:
        raise ValidationError("Contact name must be at least 2 characters long.")
    
    if len(name) > 200:
        raise ValidationError("Contact name cannot exceed 200 characters.")
    
    if not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
        raise ValidationError("Contact name can only contain letters, spaces, hyphens, apostrophes, and periods.")


def validate_contact_details(contact):
    if not contact:
        return
    
    if len(contact) > 100:
        raise ValidationError("Contact details cannot exceed 100 characters.")


def validate_quote_source(source):
    valid_sources = ['website', 'phone', 'email', 'referral', 'social_media', 'advertisement', 'walk_in']
    if source not in valid_sources:
        raise ValidationError(f"Quote source must be one of: {', '.join(valid_sources)}")


def validate_conversion_rate(rate):
    if rate is None:
        return
    
    try:
        decimal_rate = Decimal(str(rate))
    except (InvalidOperation, ValueError):
        raise ValidationError("Conversion rate must be a valid decimal number.")
    
    if decimal_rate <= 0:
        raise ValidationError("Conversion rate must be greater than 0.")
    
    if decimal_rate > Decimal('10'):
        raise ValidationError("Conversion rate cannot exceed 10.")


def validate_discount_percentage(percentage):
    if percentage is None:
        return
    
    try:
        decimal_percentage = Decimal(str(percentage))
    except (InvalidOperation, ValueError):
        raise ValidationError("Discount percentage must be a valid decimal number.")
    
    if decimal_percentage < 0:
        raise ValidationError("Discount percentage cannot be negative.")
    
    if decimal_percentage > 100:
        raise ValidationError("Discount percentage cannot exceed 100%.")


def validate_quote_completeness(quote_data):
    required_fields = ['client', 'service', 'cleaning_type', 'property_address', 'postcode', 'suburb', 'state', 'number_of_rooms']
    
    missing_fields = []
    for field in required_fields:
        if not quote_data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")


def validate_quote_pricing_consistency(quote):
    calculated_total = (
        quote.base_price + 
        quote.extras_cost + 
        quote.travel_cost + 
        quote.urgency_surcharge - 
        quote.discount_amount
    )
    
    if abs(calculated_total - quote.estimated_total) > Decimal('0.01'):
        raise ValidationError("Quote pricing is inconsistent. Please recalculate.")
    
    final_with_gst = calculated_total + quote.gst_amount
    if abs(final_with_gst - quote.final_price) > Decimal('0.01'):
        raise ValidationError("Final price calculation is inconsistent.")


def validate_bulk_quote_operation(quote_ids, operation):
    if not quote_ids:
        raise ValidationError("No quotes selected for bulk operation.")
    
    if len(quote_ids) > 100:
        raise ValidationError("Cannot perform bulk operation on more than 100 quotes at once.")
    
    valid_operations = ['approve', 'reject', 'cancel', 'assign', 'export']
    if operation not in valid_operations:
        raise ValidationError(f"Invalid bulk operation. Valid operations: {', '.join(valid_operations)}")


def validate_quote_assignment(quote, staff_user):
    if not staff_user.is_staff:
        raise ValidationError("Only staff members can be assigned to quotes.")
    
    if not staff_user.is_active:
        raise ValidationError("Cannot assign quote to inactive staff member.")
    
    if quote.status in ['cancelled', 'converted']:
        raise ValidationError(f"Cannot assign quote with status '{quote.status}'.")


def validate_quote_approval_requirements(quote):
    if quote.status not in ['submitted', 'under_review']:
        raise ValidationError(f"Cannot approve quote with status '{quote.status}'.")
    
    if quote.final_price <= 0:
        raise ValidationError("Cannot approve quote with zero or negative price.")
    
    if quote.is_ndis_client and not quote.ndis_participant_number:
        raise ValidationError("NDIS participant number required for NDIS quote approval.")


def validate_file_upload_permissions(user, quote):
    if not user.is_authenticated:
        raise ValidationError("Authentication required for file upload.")
    
    if user != quote.client and not user.is_staff:
        raise ValidationError("You don't have permission to upload files for this quote.")
    
    if quote.status in ['cancelled', 'converted']:
        raise ValidationError(f"Cannot upload files for quote with status '{quote.status}'.")


class QuoteValidator:
    
    @staticmethod
    def validate_quote_creation(data):
        validate_quote_completeness(data)
        
        if data.get('cleaning_type') and data.get('service'):
            validate_cleaning_type_service_compatibility(data['cleaning_type'], data['service'])
        
        if data.get('service') and data.get('postcode'):
            validate_service_area_coverage(data['service'], data['postcode'])
        
        validate_ndis_quote_requirements(
            data.get('is_ndis_client', False),
            data.get('ndis_participant_number'),
            data.get('service')
        )
    
    @staticmethod
    def validate_quote_update(quote, data):
        if 'status' in data:
            validate_quote_status_transition(quote.status, data['status'])
        
        if data.get('expires_at'):
            validate_quote_expiry_date(data['expires_at'], data.get('status', quote.status))
    
    @staticmethod
    def validate_quote_submission(quote):
        if quote.status != 'draft':
            raise ValidationError("Only draft quotes can be submitted.")
        
        if quote.final_price <= 0:
            raise ValidationError("Quote must have a valid price before submission.")
    
    @staticmethod
    def validate_quote_conversion(quote):
        if quote.status != 'approved':
            raise ValidationError("Only approved quotes can be converted.")
        
        if quote.is_expired:
            raise ValidationError("Cannot convert expired quote.")
