from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Invoice, InvoiceItem
from .signals import generate_and_send_invoice, send_invoice_email
import json


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ["total_price", "gst_amount", "total_with_gst"]
    fields = [
        "description",
        "quantity",
        "unit_price",
        "total_price",
        "is_taxable",
        "gst_amount",
        "total_with_gst",
    ]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "client_name",
        "status_badge",
        "total_amount",
        "deposit_status_badge",
        "invoice_date",
        "due_date",
        "is_ndis_invoice",
        "email_sent_status",
        "action_buttons",
    ]

    list_filter = [
        "status",
        "is_ndis_invoice",
        "deposit_required",
        "deposit_paid",
        "email_sent",
        "invoice_date",
        "created_at",
    ]

    search_fields = [
        "invoice_number",
        "client__first_name",
        "client__last_name",
        "client__email",
        "participant_name",
        "ndis_number",
    ]

    readonly_fields = [
        "id",
        "invoice_number",
        "subtotal",
        "gst_amount",
        "total_amount",
        "deposit_required",
        "deposit_amount",
        "deposit_percentage",
        "remaining_balance",
        "pdf_file",
        "email_sent",
        "email_sent_at",
        "created_at",
        "updated_at",
        "invoice_preview",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "invoice_number",
                    "client",
                    "quote",
                    "status",
                    "created_by",
                )
            },
        ),
        ("Dates", {"fields": ("invoice_date", "due_date", "payment_terms")}),
        ("Addresses", {"fields": ("billing_address", "service_address")}),
        (
            "NDIS Information",
            {
                "fields": (
                    "is_ndis_invoice",
                    "participant_name",
                    "ndis_number",
                    "service_start_date",
                    "service_end_date",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Financial Details", {"fields": ("subtotal", "gst_amount", "total_amount")}),
        (
            "Deposit Information",
            {
                "fields": (
                    "deposit_required",
                    "deposit_amount",
                    "deposit_percentage",
                    "remaining_balance",
                    "deposit_paid",
                    "deposit_paid_date",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Files & Communication",
            {"fields": ("pdf_file", "email_sent", "email_sent_at", "notes")},
        ),
        ("Preview", {"fields": ("invoice_preview",), "classes": ("wide",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [InvoiceItemInline]

    actions = [
        "generate_invoices",
        "send_invoice_emails",
        "mark_as_sent",
        "recalculate_totals",
        "mark_deposits_paid",
        "mark_deposits_unpaid",
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<uuid:invoice_id>/preview/",
                self.admin_site.admin_view(self.preview_invoice),
                name="invoices_invoice_preview",
            ),
            path(
                "<uuid:invoice_id>/generate/",
                self.admin_site.admin_view(self.generate_invoice),
                name="invoices_invoice_generate",
            ),
            path(
                "<uuid:invoice_id>/send/",
                self.admin_site.admin_view(self.send_invoice),
                name="invoices_invoice_send",
            ),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user

        if obj.quote and not change:
            obj.client = obj.quote.client
            obj.billing_address = obj.quote.property_address
            obj.service_address = obj.quote.property_address
            obj.is_ndis_invoice = obj.quote.is_ndis_client
            obj.deposit_required = obj.quote.deposit_required
            obj.deposit_amount = obj.quote.deposit_amount
            obj.deposit_percentage = obj.quote.deposit_percentage
            obj.remaining_balance = obj.quote.remaining_balance
            if obj.quote.is_ndis_client:
                client_name = ""
                if hasattr(obj.quote.client, "full_name"):
                    client_name = obj.quote.client.full_name
                else:
                    client_name = f"{obj.quote.client.first_name} {obj.quote.client.last_name}".strip()
                obj.participant_name = client_name
                obj.ndis_number = obj.quote.ndis_participant_number or ""
            if obj.quote.preferred_date:
                obj.service_start_date = obj.quote.preferred_date
                obj.service_end_date = obj.quote.preferred_date

        super().save_model(request, obj, form, change)

        if obj.quote and not change and not obj.items.exists():
            self.populate_invoice_from_quote(obj)

    def populate_invoice_from_quote(self, invoice):
        quote = invoice.quote
        from decimal import Decimal

        if quote.base_price > 0:
            service_description = f"{quote.service.name}"
            if hasattr(quote, "cleaning_type") and quote.cleaning_type:
                service_description += f" - {quote.get_cleaning_type_display()}"

            InvoiceItem.objects.create(
                invoice=invoice,
                description=service_description,
                quantity=Decimal("1.00"),
                unit_price=quote.base_price,
                is_taxable=True,
            )

        if quote.travel_cost > 0:
            InvoiceItem.objects.create(
                invoice=invoice,
                description="Travel Cost",
                quantity=Decimal("1.00"),
                unit_price=quote.travel_cost,
                is_taxable=False,
            )

        if quote.urgency_surcharge > 0:
            InvoiceItem.objects.create(
                invoice=invoice,
                description="Urgency Surcharge",
                quantity=Decimal("1.00"),
                unit_price=quote.urgency_surcharge,
                is_taxable=True,
            )

        if quote.extras_cost > 0:
            InvoiceItem.objects.create(
                invoice=invoice,
                description="Extra Services",
                quantity=Decimal("1.00"),
                unit_price=quote.extras_cost,
                is_taxable=True,
            )

        if quote.discount_amount > 0:
            InvoiceItem.objects.create(
                invoice=invoice,
                description="Discount Applied",
                quantity=Decimal("1.00"),
                unit_price=-quote.discount_amount,
                is_taxable=False,
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

    def client_name(self, obj):
        return obj.client.full_name

    client_name.short_description = "Client"

    def status_badge(self, obj):
        colors = {"draft": "#6c757d", "sent": "#007bff", "cancelled": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def deposit_status_badge(self, obj):
        if not obj.requires_deposit:
            return format_html('<span style="color: #6c757d;">No Deposit</span>')

        if obj.deposit_paid:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Paid</span><br><small>${:.2f}</small>',
                obj.deposit_amount,
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Pending</span><br><small>${:.2f}</small>',
                obj.deposit_amount,
            )

    deposit_status_badge.short_description = "Deposit Status"

    def email_sent_status(self, obj):
        if obj.email_sent:
            return format_html(
                '<span style="color: green;">✓ Sent</span><br><small>{}</small>',
                (
                    obj.email_sent_at.strftime("%d/%m/%Y %H:%M")
                    if obj.email_sent_at
                    else ""
                ),
            )
        return format_html('<span style="color: red;">✗ Not Sent</span>')

    email_sent_status.short_description = "Email Status"

    def action_buttons(self, obj):
        buttons = []

        preview_url = reverse("admin:invoices_invoice_preview", args=[obj.id])
        buttons.append(
            f'<a href="{preview_url}" class="button" target="_blank">Preview</a>'
        )

        if not obj.pdf_file:
            generate_url = reverse("admin:invoices_invoice_generate", args=[obj.id])
            buttons.append(f'<a href="{generate_url}" class="button">Generate PDF</a>')

        if obj.pdf_file and not obj.email_sent:
            send_url = reverse("admin:invoices_invoice_send", args=[obj.id])
            buttons.append(f'<a href="{send_url}" class="button">Send Email</a>')

        return format_html(" ".join(buttons))

    action_buttons.short_description = "Actions"

    def invoice_preview(self, obj):
        if obj.pk:
            preview_data = {
                "invoice_number": obj.invoice_number,
                "client_name": obj.client.full_name,
                "client_email": obj.client.email,
                "billing_address": obj.billing_address,
                "invoice_date": obj.invoice_date.strftime("%d/%m/%Y"),
                "due_date": obj.due_date.strftime("%d/%m/%Y"),
                "subtotal": f"${obj.subtotal:.2f}",
                "gst_amount": f"${obj.gst_amount:.2f}",
                "total_amount": f"${obj.total_amount:.2f}",
                "deposit_required": obj.deposit_required,
                "deposit_amount": f"${obj.deposit_amount:.2f}",
                "deposit_percentage": f"{obj.deposit_percentage:.0f}%",
                "remaining_balance": f"${obj.remaining_balance:.2f}",
                "deposit_paid": obj.deposit_paid,
                "items": [],
            }

            for item in obj.items.all():
                preview_data["items"].append(
                    {
                        "description": item.description,
                        "quantity": str(item.quantity),
                        "unit_price": f"${item.unit_price:.2f}",
                        "total_price": f"${item.total_price:.2f}",
                        "is_taxable": "Yes" if item.is_taxable else "No",
                    }
                )

            if obj.is_ndis_invoice:
                preview_data.update(
                    {
                        "participant_name": obj.participant_name,
                        "ndis_number": obj.ndis_number,
                        "service_start_date": (
                            obj.service_start_date.strftime("%d/%m/%Y")
                            if obj.service_start_date
                            else ""
                        ),
                        "service_end_date": (
                            obj.service_end_date.strftime("%d/%m/%Y")
                            if obj.service_end_date
                            else ""
                        ),
                    }
                )

            preview_html = self.render_invoice_preview(preview_data)
            return mark_safe(preview_html)

        return "Save invoice to see preview"

    invoice_preview.short_description = "Invoice Preview"

    def render_invoice_preview(self, data):
        html = f"""
        <div style="border: 1px solid #ddd; padding: 20px; background: white; font-family: Arial, sans-serif;">
            <h2 style="text-align: center; color: #2c3e50;">INVOICE</h2>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div>
                    <strong>Invoice Number:</strong> {data['invoice_number']}<br>
                    <strong>Invoice Date:</strong> {data['invoice_date']}<br>
                    <strong>Due Date:</strong> {data['due_date']}
                </div>
                <div>
                    <strong>Bill To:</strong><br>
                    {data['client_name']}<br>
                    {data['client_email']}<br>
                    {data['billing_address']}
                </div>
            </div>
        """

        if "participant_name" in data:
            html += f"""
            <div style="background: #f8f9fa; padding: 10px; margin-bottom: 20px; border-left: 4px solid #007bff;">
                <strong>NDIS Information:</strong><br>
                Participant: {data['participant_name']}<br>
                NDIS Number: {data['ndis_number']}<br>
                Service Period: {data['service_start_date']} - {data['service_end_date']}
            </div>
            """

        if data['deposit_required']:
            deposit_status = "PAID" if data['deposit_paid'] else "PENDING"
            status_color = "#28a745" if data['deposit_paid'] else "#ffc107"
            html += f"""
            <div style="background: #e9ecef; padding: 15px; margin-bottom: 20px; border-left: 4px solid {status_color};">
                <strong>Deposit Information:</strong><br>
                Deposit Required: {data['deposit_amount']} ({data['deposit_percentage']})<br>
                Deposit Status: <span style="color: {status_color}; font-weight: bold;">{deposit_status}</span><br>
                Remaining Balance: {data['remaining_balance']}
            </div>
            """

        html += """
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <thead>
                    <tr style="background: #34495e; color: white;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Description</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Qty</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Unit Price</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">GST</th>
                        <th style="padding: 10px; text-align: right; border: 1px solid #ddd;">Total</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in data["items"]:
            html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item['description']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{item['unit_price']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['is_taxable']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">{item['total_price']}</td>
                </tr>
            """

        html += f"""
                </tbody>
            </table>
            
            <div style="text-align: right; margin-top: 20px;">
                <div style="display: inline-block; text-align: right;">
                    <div style="margin-bottom: 5px;"><strong>Subtotal: {data['subtotal']}</strong></div>
                    <div style="margin-bottom: 5px;"><strong>GST: {data['gst_amount']}</strong></div>
                    <div style="font-size: 18px; border-top: 2px solid #34495e; padding-top: 10px;">
                        <strong>Total: {data['total_amount']}</strong>
                    </div>
        """

        if data['deposit_required']:
            html += f"""
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                        <div style="margin-bottom: 5px;"><strong>Deposit: {data['deposit_amount']}</strong></div>
                        <div style="font-size: 16px;"><strong>Balance Due: {data['remaining_balance']}</strong></div>
                    </div>
            """

        html += """
                </div>
            </div>
        </div>
        """

        return html

    def preview_invoice(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        context = {
            "invoice": invoice,
            "title": f"Preview Invoice {invoice.invoice_number}",
            "opts": self.model._meta,
        }

        return render(request, "admin/invoices/invoice_preview.html", context)

    def generate_invoice(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        try:
            success = invoice.generate_pdf()
            if success:
                messages.success(
                    request,
                    f"PDF generated successfully for invoice {invoice.invoice_number}",
                )
            else:
                messages.error(
                    request,
                    f"Failed to generate PDF for invoice {invoice.invoice_number}",
                )
        except Exception as e:
            messages.error(request, f"Error generating PDF: {str(e)}")

        return redirect("admin:invoices_invoice_change", invoice.id)

    def send_invoice(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)

        try:
            success = invoice.send_email()
            if success:
                messages.success(
                    request,
                    f"Invoice {invoice.invoice_number} sent successfully to {invoice.client.email}",
                )
            else:
                messages.error(
                    request, f"Failed to send invoice {invoice.invoice_number}"
                )
        except Exception as e:
            messages.error(request, f"Error sending invoice: {str(e)}")

        return redirect("admin:invoices_invoice_change", invoice.id)

    def generate_invoices(self, request, queryset):
        success_count = 0
        for invoice in queryset:
            try:
                if invoice.generate_pdf():
                    success_count += 1
            except Exception:
                continue

        messages.success(request, f"Generated PDFs for {success_count} invoices")

    generate_invoices.short_description = "Generate PDFs for selected invoices"

    def send_invoice_emails(self, request, queryset):
        success_count = 0
        for invoice in queryset:
            try:
                if invoice.send_email():
                    success_count += 1
            except Exception:
                continue

        messages.success(request, f"Sent {success_count} invoice emails")

    send_invoice_emails.short_description = "Send emails for selected invoices"

    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status="draft").update(status="sent")
        messages.success(request, f"Marked {updated} invoices as sent")

    mark_as_sent.short_description = "Mark selected invoices as sent"

    def recalculate_totals(self, request, queryset):
        for invoice in queryset:
            invoice.calculate_totals()
        messages.success(
            request, f"Recalculated totals for {queryset.count()} invoices"
        )

    recalculate_totals.short_description = "Recalculate totals for selected invoices"

    def mark_deposits_paid(self, request, queryset):
        invoices_with_deposits = queryset.filter(deposit_required=True, deposit_paid=False)
        updated_count = 0
        
        for invoice in invoices_with_deposits:
            invoice.deposit_paid = True
            invoice.deposit_paid_date = timezone.now().date()
            invoice.save(update_fields=["deposit_paid", "deposit_paid_date"])
            updated_count += 1

        messages.success(request, f"Marked deposits as paid for {updated_count} invoices")

    mark_deposits_paid.short_description = "Mark deposits as paid for selected invoices"

    def mark_deposits_unpaid(self, request, queryset):
        invoices_with_deposits = queryset.filter(deposit_required=True, deposit_paid=True)
        updated_count = 0
        
        for invoice in invoices_with_deposits:
            invoice.deposit_paid = False
            invoice.deposit_paid_date = None
            invoice.save(update_fields=["deposit_paid", "deposit_paid_date"])
            updated_count += 1

        messages.success(request, f"Marked deposits as unpaid for {updated_count} invoices")

    mark_deposits_unpaid.short_description = "Mark deposits as unpaid for selected invoices"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = [
        "invoice",
        "description",
        "quantity",
        "unit_price",
        "total_price",
        "is_taxable",
    ]
    list_filter = ["is_taxable", "created_at"]
    search_fields = ["invoice__invoice_number", "description"]
    readonly_fields = ["total_price", "gst_amount", "total_with_gst"]

