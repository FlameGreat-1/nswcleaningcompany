from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Max
from decimal import Decimal
from io import StringIO
import uuid
import re
from .managers import QuoteManager, QuoteItemManager
from .validators import (
    validate_quote_number,
    validate_urgency_level,
    validate_file_size,
    validate_image_file,
    validate_room_count,
    validate_square_meters,
    validate_template_name,
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
        ("airbnb", "Airbnb Turnover"),
        ("post_renovation", "Post Renovation"),
        ("after_builders", "After Builders Clean"),
        ("custom_one_off", "Custom One Off"),
    )

    URGENCY_LEVEL_CHOICES = (
        (1, "Flexible (7+ days)"),
        (2, "Standard (3-7 days)"),
        (3, "Priority (1-3 days)"),
        (4, "Urgent (Same day)"),
        (5, "Emergency (ASAP)"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_quote_number],
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quotes",
    )

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="quotes",
    )

    cleaning_type = models.CharField(
        max_length=20,
        choices=CLEANING_TYPE_CHOICES,
    )

    property_address = models.TextField()

    postcode = models.CharField(max_length=4)

    suburb = models.CharField(max_length=100)

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
    )

    number_of_rooms = models.PositiveIntegerField(validators=[validate_room_count])

    square_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_square_meters],
    )

    urgency_level = models.PositiveIntegerField(
        choices=URGENCY_LEVEL_CHOICES,
        default=2,
        validators=[validate_urgency_level],
    )

    preferred_date = models.DateField(null=True, blank=True)

    preferred_time = models.TimeField(null=True, blank=True)

    special_requirements = models.TextField(blank=True)

    access_instructions = models.TextField(blank=True)

    is_ndis_client = models.BooleanField(default=False)

    ndis_participant_number = models.CharField(max_length=9, blank=True)

    plan_manager_name = models.CharField(max_length=200, blank=True)

    plan_manager_contact = models.CharField(max_length=100, blank=True)

    support_coordinator_name = models.CharField(max_length=200, blank=True)

    support_coordinator_contact = models.CharField(max_length=100, blank=True)

    estimated_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    extras_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    travel_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    urgency_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    deposit_required = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    deposit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )

    remaining_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    status = models.CharField(
        max_length=20,
        choices=QUOTE_STATUS_CHOICES,
        default="draft",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_quotes",
        limit_choices_to={"is_staff": True},
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_quotes",
        limit_choices_to={"is_staff": True},
    )

    admin_notes = models.TextField(blank=True)

    client_notes = models.TextField(blank=True)

    rejection_reason = models.TextField(blank=True)

    source = models.CharField(max_length=50, default="website")

    conversion_rate_applied = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

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

        constraints = [
            models.CheckConstraint(
                check=models.Q(final_price__gte=0),
                name="quotes_quote_positive_final_price",
            ),
            models.CheckConstraint(
                check=models.Q(number_of_rooms__gt=0),
                name="quotes_quote_positive_room_count",
            ),
            models.CheckConstraint(
                check=models.Q(base_price__gte=0),
                name="quotes_quote_positive_base_price",
            ),
            models.CheckConstraint(
                check=models.Q(estimated_total__gte=0),
                name="quotes_quote_positive_estimated_total",
            ),
            models.CheckConstraint(
                check=models.Q(deposit_amount__gte=0),
                name="quotes_quote_positive_deposit_amount",
            ),
            models.CheckConstraint(
                check=models.Q(deposit_percentage__gte=0, deposit_percentage__lte=100),
                name="quotes_quote_valid_deposit_percentage",
            ),
            models.CheckConstraint(
                check=models.Q(remaining_balance__gte=0),
                name="quotes_quote_positive_remaining_balance",
            ),
        ]

    def __str__(self):
        return f"Quote {self.quote_number} - {self.client.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            self.quote_number = self.generate_quote_number()

        if not self.expires_at and self.status in ["approved"]:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)

        super().save(*args, **kwargs)

    @transaction.atomic
    def generate_quote_number(self):
        current_year = timezone.now().year
        prefix = f"QT-{current_year}-"

        latest_quote = (
            Quote.objects.select_for_update()
            .filter(quote_number__startswith=prefix)
            .aggregate(Max("quote_number"))["quote_number__max"]
        )

        if latest_quote:
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
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def days_until_expiry(self):
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return max(0, delta.days)
        return None

    @property
    def can_be_accepted(self):
        return (
            self.status == "approved" and not self.is_expired and self.final_price > 0
        )

    @property
    def total_items_cost(self):
        return self.items.aggregate(
            total=models.Sum(models.F("quantity") * models.F("unit_price"))
        )["total"] or Decimal("0.00")

    @property
    def requires_deposit(self):
        """Check if quote requires deposit based on urgency level"""
        return self.deposit_required  

    def calculate_pricing(self):
        from .utils import calculate_quote_pricing

        return calculate_quote_pricing(self)

    def update_pricing(self):
        pricing_data = self.calculate_pricing()

        self.base_price = pricing_data["base_price"]
        self.extras_cost = pricing_data["extras_cost"]
        self.travel_cost = pricing_data["travel_cost"]
        self.urgency_surcharge = pricing_data["urgency_surcharge"]
        self.discount_amount = pricing_data["discount_amount"]
        self.gst_amount = pricing_data["gst_amount"]
        self.final_price = pricing_data["final_price"]
        self.estimated_total = pricing_data["final_price"]
        self.deposit_required = pricing_data.get("deposit_required", False)
        self.deposit_amount = pricing_data.get("deposit_amount", Decimal("0.00"))
        self.deposit_percentage = pricing_data.get("deposit_percentage", Decimal("0.00"))
        self.remaining_balance = pricing_data.get("remaining_balance", Decimal("0.00"))

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
                "deposit_required",
                "deposit_amount",
                "deposit_percentage",
                "remaining_balance",
            ]
        )

    def submit_quote(self):
        if self.status == "draft":
            self.status = "submitted"
            self.submitted_at = timezone.now()
            self.save(update_fields=["status", "submitted_at"])
            return True
        return False

    def approve_quote(self, approved_by_user):
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

    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPE_CHOICES, help_text="Type of quote item"
    )

    name = models.CharField(max_length=200, help_text="Item name/description")

    description = models.TextField(blank=True, help_text="Detailed item description")

    quantity = models.DecimalField(
        max_digits=10,
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

    is_optional = models.BooleanField(
        default=False, help_text="Whether this item is optional"
    )

    is_taxable = models.BooleanField(
        default=True, help_text="Whether GST applies to this item"
    )

    display_order = models.PositiveIntegerField(
        default=0, help_text="Order for displaying items"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name="quotes_quoteitem_positive_quantity",
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gte=0),
                name="quotes_quoteitem_positive_unit_price",
            ),
            models.CheckConstraint(
                check=models.Q(total_price__gte=0),
                name="quotes_quoteitem_positive_total_price",
            ),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - {self.name}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def gst_amount(self):
        if self.is_taxable:
            return (self.total_price * Decimal("0.10")).quantize(Decimal("0.01"))
        return Decimal("0.00")

    @property
    def total_with_gst(self):
        return self.total_price + self.gst_amount


class QuoteAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = (
        ("image", "Image"),
        ("document", "Document"),
        ("floor_plan", "Floor Plan"),
        ("reference", "Reference Photo"),
    )

    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text="Quote this attachment belongs to",
    )

    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who uploaded this file"
    )

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
        constraints = [
            models.CheckConstraint(
                check=models.Q(file_size__gt=0),
                name="quotes_quoteattachment_positive_file_size",
            ),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - {self.original_filename}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            if not self.original_filename:
                self.original_filename = getattr(self.file, "name", "unknown")
            if hasattr(self.file.file, "content_type"):
                self.file_type = self.file.file.content_type
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.file_type.startswith("image/") if self.file_type else False

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class QuoteRevision(models.Model):
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="revisions",
        help_text="Quote this revision belongs to",
    )

    revised_by = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who made the revision"
    )

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

    previous_deposit_required = models.BooleanField(default=False)
    new_deposit_required = models.BooleanField(default=False)
    previous_deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    new_deposit_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    reason = models.TextField(help_text="Reason for the revision")

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
        constraints = [
            models.CheckConstraint(
                check=models.Q(previous_price__gte=0),
                name="quotes_quoterevision_positive_previous_price",
            ),
            models.CheckConstraint(
                check=models.Q(new_price__gte=0),
                name="quotes_quoterevision_positive_new_price",
            ),
            models.CheckConstraint(
                check=models.Q(revision_number__gt=0),
                name="quotes_quoterevision_positive_revision_number",
            ),
        ]

    def __str__(self):
        return f"{self.quote.quote_number} - Revision {self.revision_number}"


class QuoteTemplate(models.Model):
    name = models.CharField(
        max_length=200, validators=[validate_template_name], help_text="Template name"
    )
    description = models.TextField(help_text="Template description")
    cleaning_type = models.CharField(
        max_length=20,
        choices=Quote.CLEANING_TYPE_CHOICES,
        help_text="Default cleaning type",
    )
    default_service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Default service for this template",
    )
    default_urgency_level = models.PositiveIntegerField(
        choices=Quote.URGENCY_LEVEL_CHOICES,
        default=2,
        help_text="Default urgency level",
    )
    number_of_rooms = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[validate_room_count],
        help_text="Default number of rooms",
    )
    square_meters = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_square_meters],
        help_text="Default property size",
    )
    special_requirements = models.TextField(
        blank=True, help_text="Default special requirements"
    )
    access_instructions = models.TextField(
        blank=True, help_text="Default access instructions"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether template is active"
    )
    is_ndis_template = models.BooleanField(
        default=False, help_text="Whether this is an NDIS-specific template"
    )
    usage_count = models.PositiveIntegerField(
        default=0, help_text="Number of times template has been used"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created the template",
    )

    class Meta:
        db_table = "quotes_quote_template"
        verbose_name = "Quote Template"
        verbose_name_plural = "Quote Templates"
        ordering = ["-updated_at"]
        unique_together = ["created_by", "name"]
        indexes = [
            models.Index(fields=["created_by", "is_active"]),
            models.Index(fields=["cleaning_type", "is_active"]),
            models.Index(fields=["is_ndis_template"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(usage_count__gte=0),
                name="quotes_quotetemplate_positive_usage_count",
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.created_by.get_full_name()}"

    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=["usage_count"])
