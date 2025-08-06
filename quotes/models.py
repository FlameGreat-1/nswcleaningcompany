from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from .managers import QuoteManager, QuoteItemManager
from .validators import (
    validate_quote_number,
    validate_urgency_level,
    validate_file_size,
    validate_image_file,
    validate_room_count,
    validate_square_meters,
)

User = get_user_model()


class Quote(models.Model):
    QUOTE_STATUS_CHOICES = (
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
        ("converted", "Converted to Job"),
        ("cancelled", "Cancelled"),
    )

    CLEANING_TYPE_CHOICES = (
        ("general", "General Cleaning"),
        ("deep", "Deep Cleaning"),
        ("end_of_lease", "End of Lease Cleaning"),
        ("ndis", "NDIS Cleaning"),
        ("commercial", "Commercial Cleaning"),
        ("carpet", "Carpet Cleaning"),
        ("window", "Window Cleaning"),
        ("pressure_washing", "Pressure Washing"),
    )

    URGENCY_LEVEL_CHOICES = (
        (1, "Flexible (7+ days)"),
        (2, "Standard (3-7 days)"),
        (3, "Priority (1-3 days)"),
        (4, "Urgent (Same day)"),
        (5, "Emergency (ASAP)"),
    )

    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_quote_number],
        help_text="Auto-generated quote number (QT-YYYY-NNNN)",
    )

    # Client information
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quotes",
        help_text="Client who requested the quote",
    )

    # Service details
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="quotes",
        help_text="Primary service being quoted",
    )

    cleaning_type = models.CharField(
        max_length=20,
        choices=CLEANING_TYPE_CHOICES,
        help_text="Type of cleaning service",
    )

    # Property details
    property_address = models.TextField(
        help_text="Full property address for the cleaning service"
    )

    postcode = models.CharField(
        max_length=4, help_text="Property postcode for service area validation"
    )

    suburb = models.CharField(max_length=100, help_text="Property suburb")

    state = models.CharField(
        max_length=3,
        choices=(
            ("NSW", "New South Wales"),
            ("VIC", "Victoria"),
            ("QLD", "Queensland"),
            ("WA", "Western Australia"),
            ("SA", "South Australia"),
            ("TAS", "Tasmania"),
            ("ACT", "Australian Capital Territory"),
            ("NT", "Northern Territory"),
        ),
        help_text="Property state",
    )

    # Service specifications
    number_of_rooms = models.PositiveIntegerField(
        validators=[validate_room_count], help_text="Number of rooms to be cleaned"
    )

    square_meters = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_square_meters],
        help_text="Property size in square meters (optional)",
    )

    urgency_level = models.PositiveIntegerField(
        choices=URGENCY_LEVEL_CHOICES,
        default=2,
        validators=[validate_urgency_level],
        help_text="Service urgency level (affects pricing)",
    )

    # Scheduling
    preferred_date = models.DateField(
        null=True, blank=True, help_text="Client's preferred service date"
    )

    preferred_time = models.TimeField(
        null=True, blank=True, help_text="Client's preferred service time"
    )

    # Special requirements
    special_requirements = models.TextField(
        blank=True, help_text="Any special cleaning requirements or instructions"
    )

    access_instructions = models.TextField(
        blank=True, help_text="Property access instructions (keys, codes, etc.)"
    )

    # NDIS specific fields
    is_ndis_client = models.BooleanField(
        default=False, help_text="Whether this is an NDIS client quote"
    )

    ndis_participant_number = models.CharField(
        max_length=9, blank=True, help_text="NDIS participant number (if applicable)"
    )

    plan_manager_name = models.CharField(
        max_length=200, blank=True, help_text="NDIS plan manager name (if applicable)"
    )

    plan_manager_contact = models.CharField(
        max_length=100, blank=True, help_text="NDIS plan manager contact details"
    )

    support_coordinator_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="NDIS support coordinator name (if applicable)",
    )

    support_coordinator_contact = models.CharField(
        max_length=100, blank=True, help_text="NDIS support coordinator contact details"
    )

    # Pricing details
    estimated_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Auto-calculated estimated total price",
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Base service price",
    )

    extras_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Cost of additional services/extras",
    )

    travel_cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Travel cost based on location",
    )

    urgency_surcharge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Additional cost for urgent service",
    )

    discount_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount applied to the quote",
    )

    gst_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="GST amount (10% in Australia)",
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final price including all adjustments",
    )

    # Quote status and workflow
    status = models.CharField(
        max_length=20,
        choices=QUOTE_STATUS_CHOICES,
        default="draft",
        help_text="Current quote status",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(
        null=True, blank=True, help_text="When the quote was submitted by client"
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True, help_text="When the quote was reviewed by staff"
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, help_text="When the quote was approved"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Quote expiration date"
    )

    # Staff handling
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_quotes",
        limit_choices_to={"is_staff": True},
        help_text="Staff member assigned to handle this quote",
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_quotes",
        limit_choices_to={"is_staff": True},
        help_text="Staff member who reviewed the quote",
    )

    # Notes and communication
    admin_notes = models.TextField(
        blank=True, help_text="Internal notes for staff (not visible to client)"
    )

    client_notes = models.TextField(blank=True, help_text="Notes visible to client")

    rejection_reason = models.TextField(
        blank=True, help_text="Reason for quote rejection (if applicable)"
    )

    # Tracking and analytics
    source = models.CharField(
        max_length=50,
        default="website",
        help_text="How the quote was generated (website, phone, etc.)",
    )

    conversion_rate_applied = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("1.0000"),
        help_text="Conversion rate applied for pricing calculations",
    )

    # Custom manager
    objects = QuoteManager()

    class Meta:
        db_table = "quotes_quote"
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["quote_number"]),
            models.Index(fields=["postcode", "cleaning_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_ndis_client"]),
        ]

    def __str__(self):
        return f"Quote {self.quote_number} - {self.client.get_full_name()}"

    def save(self, *args, **kwargs):
        # Generate quote number if not exists
        if not self.quote_number:
            self.quote_number = self.generate_quote_number()

        # Set NDIS fields based on client
        if hasattr(self.client, "client_profile") and self.client.client_profile:
            profile = self.client.client_profile
            if profile.client_type == "ndis":
                self.is_ndis_client = True
                self.ndis_participant_number = profile.ndis_number or ""
                self.plan_manager_name = profile.plan_manager_name or ""
                self.plan_manager_contact = profile.plan_manager_contact or ""
                self.support_coordinator_name = profile.support_coordinator_name or ""
                self.support_coordinator_contact = (
                    profile.support_coordinator_contact or ""
                )

        # Set expiration date
        if not self.expires_at and self.status in ["approved"]:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)

        super().save(*args, **kwargs)

    def generate_quote_number(self):
        """Generate unique quote number in format QT-YYYY-NNNN"""
        from django.db.models import Max
        import re

        current_year = timezone.now().year
        prefix = f"QT-{current_year}-"

        # Get the highest number for current year
        latest_quote = Quote.objects.filter(quote_number__startswith=prefix).aggregate(
            Max("quote_number")
        )["quote_number__max"]

        if latest_quote:
            # Extract number from QT-YYYY-NNNN format
            match = re.search(r"-(\d{4})$", latest_quote)
            if match:
                next_number = int(match.group(1)) + 1
            else:
                next_number = 1
        else:
            next_number = 1

        return f"{prefix}{next_number:04d}"

    @property
    def is_expired(self):
        """Check if quote has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def days_until_expiry(self):
        """Get days until quote expires"""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
        return None

    @property
    def can_be_accepted(self):
        """Check if quote can be accepted by client"""
        return (
            self.status == "approved" and not self.is_expired and self.final_price > 0
        )

    @property
    def total_items_cost(self):
        """Calculate total cost of all quote items"""
        return self.items.aggregate(
            total=models.Sum(models.F("quantity") * models.F("unit_price"))
        )["total"] or Decimal("0.00")

    def calculate_pricing(self):
        """Calculate all pricing components"""
        from .utils import calculate_quote_pricing

        return calculate_quote_pricing(self)

    def update_pricing(self):
        """Update all pricing fields based on current data"""
        pricing_data = self.calculate_pricing()

        self.base_price = pricing_data["base_price"]
        self.extras_cost = pricing_data["extras_cost"]
        self.travel_cost = pricing_data["travel_cost"]
        self.urgency_surcharge = pricing_data["urgency_surcharge"]
        self.discount_amount = pricing_data["discount_amount"]
        self.gst_amount = pricing_data["gst_amount"]
        self.final_price = pricing_data["final_price"]
        self.estimated_total = pricing_data["final_price"]

        self.save(
            update_fields=[
                "base_price",
                "extras_cost",
                "travel_cost",
                "urgency_surcharge",
                "discount_amount",
                "gst_amount",
                "final_price",
                "estimated_total",
            ]
        )

    def submit_quote(self):
        """Submit quote for review"""
        if self.status == "draft":
            self.status = "submitted"
            self.submitted_at = timezone.now()
            self.save(update_fields=["status", "submitted_at"])
            return True
        return False

    def approve_quote(self, approved_by_user):
        """Approve the quote"""
        if self.status in ["submitted", "under_review"]:
            self.status = "approved"
            self.approved_at = timezone.now()
            self.reviewed_by = approved_by_user
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
            self.save(
                update_fields=["status", "approved_at", "reviewed_by", "expires_at"]
            )
            return True
        return False

    def reject_quote(self, rejected_by_user, reason=""):
        """Reject the quote"""
        if self.status in ["submitted", "under_review"]:
            self.status = "rejected"
            self.reviewed_at = timezone.now()
            self.reviewed_by = rejected_by_user
            self.rejection_reason = reason
            self.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                    "reviewed_by",
                    "rejection_reason",
                ]
            )
            return True
        return False


class QuoteItem(models.Model):
    """Individual items/services within a quote"""

    ITEM_TYPE_CHOICES = (
        ("service", "Main Service"),
        ("addon", "Add-on Service"),
        ("extra", "Extra Service"),
        ("material", "Materials"),
        ("equipment", "Equipment"),
        ("travel", "Travel Cost"),
        ("surcharge", "Surcharge"),
        ("discount", "Discount"),
    )

    # Relationships
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Quote this item belongs to",
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Related service (if applicable)",
    )

    addon = models.ForeignKey(
        "services.ServiceAddOn",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Related add-on service (if applicable)",
    )

    # Item details
    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPE_CHOICES, help_text="Type of quote item"
    )

    name = models.CharField(max_length=200, help_text="Item name/description")

    description = models.TextField(blank=True, help_text="Detailed item description")

    # Pricing
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Item quantity",
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Price per unit",
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total price (quantity × unit_price)",
    )

    # Metadata
    is_optional = models.BooleanField(
        default=False, help_text="Whether this item is optional"
    )

    is_taxable = models.BooleanField(
        default=True, help_text="Whether GST applies to this item"
    )

    display_order = models.PositiveIntegerField(
        default=0, help_text="Order for displaying items"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = QuoteItemManager()

    class Meta:
        db_table = "quotes_quote_item"
        verbose_name = "Quote Item"
        verbose_name_plural = "Quote Items"
        ordering = ["display_order", "created_at"]
        indexes = [
            models.Index(fields=["quote", "item_type"]),
            models.Index(fields=["display_order"]),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - {self.name}"

    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def gst_amount(self):
        """Calculate GST amount for this item"""
        if self.is_taxable:
            return (self.total_price * Decimal("0.10")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def total_with_gst(self):
        """Get total price including GST"""
        return self.total_price + self.gst_amount


class QuoteAttachment(models.Model):
    """File attachments for quotes (images, documents)"""

    ATTACHMENT_TYPE_CHOICES = (
        ("image", "Image"),
        ("document", "Document"),
        ("floor_plan", "Floor Plan"),
        ("reference", "Reference Photo"),
    )

    # Relationships
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text="Quote this attachment belongs to",
    )

    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who uploaded this file"
    )

    # File details
    file = models.FileField(
        upload_to="quotes/attachments/%Y/%m/",
        validators=[validate_file_size, validate_image_file],
        help_text="Uploaded file (JPG, PNG, PDF)",
    )

    original_filename = models.CharField(max_length=255, help_text="Original filename")

    file_size = models.PositiveIntegerField(help_text="File size in bytes")

    file_type = models.CharField(max_length=50, help_text="MIME type of the file")

    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        default="image",
        help_text="Type of attachment",
    )

    # Metadata
    title = models.CharField(
        max_length=200, blank=True, help_text="Attachment title/caption"
    )

    description = models.TextField(blank=True, help_text="Attachment description")

    is_public = models.BooleanField(
        default=False, help_text="Whether attachment is visible to client"
    )

    display_order = models.PositiveIntegerField(
        default=0, help_text="Order for displaying attachments"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes_quote_attachment"
        verbose_name = "Quote Attachment"
        verbose_name_plural = "Quote Attachments"
        ordering = ["display_order", "created_at"]
        indexes = [
            models.Index(fields=["quote", "attachment_type"]),
            models.Index(fields=["uploaded_by"]),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - {self.original_filename}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.original_filename = self.file.name
            # Set file_type based on file extension or content
            if hasattr(self.file.file, "content_type"):
                self.file_type = self.file.file.content_type
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        """Check if attachment is an image"""
        return self.file_type.startswith("image/") if self.file_type else False

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)


class QuoteRevision(models.Model):
    """Track quote revisions and changes"""

    # Relationships
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="revisions",
        help_text="Quote this revision belongs to",
    )

    revised_by = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who made the revision"
    )

    # Revision details
    revision_number = models.PositiveIntegerField(
        help_text="Sequential revision number"
    )

    changes_summary = models.TextField(help_text="Summary of changes made")

    previous_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price before revision"
    )

    new_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price after revision"
    )

    reason = models.TextField(help_text="Reason for the revision")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "quotes_quote_revision"
        verbose_name = "Quote Revision"
        verbose_name_plural = "Quote Revisions"
        ordering = ["-revision_number"]
        unique_together = ["quote", "revision_number"]
        indexes = [
            models.Index(fields=["quote", "revision_number"]),
            models.Index(fields=["revised_by"]),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - Revision {self.revision_number}"


class QuoteTemplate(models.Model):
    """Reusable quote templates for common services"""

    # Template details
    name = models.CharField(max_length=200, unique=True, help_text="Template name")

    description = models.TextField(help_text="Template description")

    cleaning_type = models.CharField(
        max_length=20,
        choices=Quote.CLEANING_TYPE_CHOICES,
        help_text="Default cleaning type",
    )

    # Default values
    default_service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        help_text="Default service for this template",
    )

    default_urgency_level = models.PositiveIntegerField(
        choices=Quote.URGENCY_LEVEL_CHOICES,
        default=2,
        help_text="Default urgency level",
    )

    # Template settings
    is_active = models.BooleanField(
        default=True, help_text="Whether template is active"
    )

    is_ndis_template = models.BooleanField(
        default=False, help_text="Whether this is an NDIS-specific template"
    )

    # Usage tracking
    usage_count = models.PositiveIntegerField(
        default=0, help_text="Number of times template has been used"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": True},
        help_text="Staff member who created the template",
    )

    class Meta:
        db_table = "quotes_quote_template"
        verbose_name = "Quote Template"
        verbose_name_plural = "Quote Templates"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["cleaning_type", "is_active"]),
            models.Index(fields=["is_ndis_template"]),
        ]

    def __str__(self):
        return self.name

    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])
