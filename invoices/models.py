from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
import uuid
import os
from django.conf import settings
from .utils import (
    InvoiceNumberGenerator,
    PricingCalculator,
    PDFInvoiceGenerator,
    InvoiceEmailService,
    DateTimeUtils,
    FilePathGenerator,
)
from .validators import (
    validate_invoice_number,
    validate_ndis_number,
    validate_positive_decimal,
    validate_due_date,
    validate_payment_terms,
    validate_quantity,
    validate_unit_price,
    validate_participant_name,
)

User = get_user_model()


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("cancelled", "Cancelled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(
        max_length=20, unique=True, validators=[validate_invoice_number]
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")

    quote = models.OneToOneField(
        "quotes.Quote",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="invoice",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(validators=[validate_due_date])

    billing_address = models.TextField()
    service_address = models.TextField()

    is_ndis_invoice = models.BooleanField(default=False)
    participant_name = models.CharField(
        max_length=200, blank=True, validators=[validate_participant_name]
    )
    ndis_number = models.CharField(
        max_length=20, blank=True, validators=[validate_ndis_number]
    )
    service_start_date = models.DateField(null=True, blank=True)
    service_end_date = models.DateField(null=True, blank=True)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
    )

    payment_terms = models.PositiveIntegerField(
        default=30, validators=[validate_payment_terms]
    )

    notes = models.TextField(blank=True)

    pdf_file = models.FileField(upload_to="invoices/pdfs/%Y/%m/", blank=True, null=True)

    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )

    class Meta:
        db_table = "invoices_invoice"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["is_ndis_invoice"]),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client_full_name}"

    @property
    def client_full_name(self):
        if hasattr(self.client, "full_name"):
            return self.client.full_name
        return f"{self.client.first_name} {self.client.last_name}".strip()

    @property
    def is_client_ndis(self):
        return getattr(self.client, "is_ndis_client", False)

    @property
    def client_profile_data(self):
        if hasattr(self.client, "client_profile"):
            try:
                return self.client.client_profile
            except ObjectDoesNotExist:
                return None
        return None

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = InvoiceNumberGenerator.generate_invoice_number()

        if not self.due_date:
            self.due_date = DateTimeUtils.calculate_due_date(
                self.invoice_date, self.payment_terms
            )

        if self.is_client_ndis:
            self.is_ndis_invoice = True
            self.participant_name = self.client_full_name

            profile = self.client_profile_data
            if profile:
                self.ndis_number = getattr(profile, "ndis_number", "") or ""

        if self.quote:
            self.billing_address = self.quote.property_address
            self.service_address = self.quote.property_address
            if self.quote.preferred_date:
                self.service_start_date = self.quote.preferred_date
                self.service_end_date = self.quote.preferred_date

        super().save(*args, **kwargs)

    def calculate_totals(self):
        items_data = []
        for item in self.items.all():
            items_data.append(
                {
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "is_taxable": item.is_taxable,
                }
            )

        totals = PricingCalculator.calculate_invoice_totals(items_data)

        self.subtotal = totals["subtotal"]
        self.gst_amount = totals["gst_amount"]
        self.total_amount = totals["total_amount"]

        self.save(update_fields=["subtotal", "gst_amount", "total_amount"])

    def generate_pdf(self):
        pdf_path = FilePathGenerator.generate_invoice_pdf_path(self)
        FilePathGenerator.ensure_directory_exists(pdf_path)

        generator = PDFInvoiceGenerator()
        success = generator.generate_pdf(self, pdf_path)

        if success:
            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            self.pdf_file.name = relative_path
            self.save(update_fields=["pdf_file"])

        return success

    def send_email(self):
        if not self.pdf_file:
            if not self.generate_pdf():
                return False

        pdf_path = self.pdf_file.path if self.pdf_file else None
        success = InvoiceEmailService.send_invoice_email(self, pdf_path)

        if success:
            self.email_sent = True
            self.email_sent_at = timezone.now()
            self.save(update_fields=["email_sent", "email_sent_at"])

        return success

    def mark_as_sent(self):
        if self.status == "draft":
            self.status = "sent"
            self.save(update_fields=["status"])

    @classmethod
    def create_from_quote(cls, quote, created_by=None):
        client_name = ""
        if hasattr(quote.client, "full_name"):
            client_name = quote.client.full_name
        else:
            client_name = f"{quote.client.first_name} {quote.client.last_name}".strip()

        invoice = cls.objects.create(
            client=quote.client,
            quote=quote,
            billing_address=quote.property_address,
            service_address=quote.property_address,
            is_ndis_invoice=quote.is_ndis_client,
            participant_name=client_name if quote.is_ndis_client else "",
            ndis_number=quote.ndis_participant_number or "",
            service_start_date=quote.preferred_date,
            service_end_date=quote.preferred_date,
            created_by=created_by,
        )

        for quote_item in quote.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                description=quote_item.name,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                is_taxable=quote_item.is_taxable,
            )

        invoice.calculate_totals()

        quote.status = "converted"
        quote.save(update_fields=["status"])

        return invoice


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")

    description = models.CharField(max_length=500)
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[validate_quantity],
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_unit_price]
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    is_taxable = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices_invoice_item"
        verbose_name = "Invoice Item"
        verbose_name_plural = "Invoice Items"
        ordering = ["id"]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.description}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def gst_amount(self):
        if self.is_taxable:
            return PricingCalculator.calculate_gst(self.total_price)
        return Decimal("0.00")

    @property
    def total_with_gst(self):
        return self.total_price + self.gst_amount
