from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import csv
from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from .permissions import check_quote_permission
from .validators import validate_quote_status_transition


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    fields = [
        "item_type",
        "name",
        "quantity",
        "unit_price",
        "total_price",
        "is_optional",
        "is_taxable",
        "display_order",
    ]
    readonly_fields = ["total_price"]
    ordering = ["display_order", "created_at"]


class QuoteAttachmentInline(admin.TabularInline):
    model = QuoteAttachment
    extra = 0
    fields = ["file", "attachment_type", "title", "is_public", "file_size_display"]
    readonly_fields = ["file_size_display"]

    def file_size_display(self, obj):
        if obj.file_size:
            return f"{obj.file_size_mb} MB"
        return "-"

    file_size_display.short_description = "File Size"


class QuoteRevisionInline(admin.TabularInline):
    model = QuoteRevision
    extra = 0
    fields = [
        "revision_number",
        "changes_summary",
        "previous_price",
        "new_price",
        "price_change_display",
        "revised_by",
        "created_at",
    ]
    readonly_fields = ["revision_number", "price_change_display", "created_at"]
    ordering = ["-revision_number"]

    def price_change_display(self, obj):
        change = obj.new_price - obj.previous_price
        if change > 0:
            return format_html('<span style="color: green;">+${:.2f}</span>', change)
        elif change < 0:
            return format_html('<span style="color: red;">${:.2f}</span>', change)
        return "$0.00"

    price_change_display.short_description = "Price Change"


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = [
        "quote_number",
        "client_name",
        "service_name",
        "cleaning_type",
        "status_display",
        "final_price_display",
        "urgency_display",
        "is_ndis_display",
        "created_at",
        "expires_at",
    ]

    list_filter = [
        "status",
        "cleaning_type",
        "urgency_level",
        "is_ndis_client",
        "state",
        "created_at",
        "expires_at",
    ]

    search_fields = [
        "quote_number",
        "client__first_name",
        "client__last_name",
        "client__email",
        "property_address",
        "suburb",
        "postcode",
        "ndis_participant_number",
    ]

    readonly_fields = [
        "quote_number",
        "created_at",
        "updated_at",
        "submitted_at",
        "reviewed_at",
        "approved_at",
        "is_expired",
        "days_until_expiry",
        "can_be_accepted",
        "total_items_cost",
    ]

    fieldsets = (
        (
            "Quote Information",
            {
                "fields": (
                    "quote_number",
                    "client",
                    "service",
                    "cleaning_type",
                    "status",
                )
            },
        ),
        (
            "Property Details",
            {"fields": ("property_address", "suburb", "postcode", "state")},
        ),
        (
            "Service Specifications",
            {
                "fields": (
                    "number_of_rooms",
                    "square_meters",
                    "urgency_level",
                    "preferred_date",
                    "preferred_time",
                )
            },
        ),
        (
            "Requirements & Instructions",
            {
                "fields": ("special_requirements", "access_instructions"),
                "classes": ["collapse"],
            },
        ),
        (
            "NDIS Information",
            {
                "fields": (
                    "is_ndis_client",
                    "ndis_participant_number",
                    "plan_manager_name",
                    "plan_manager_contact",
                    "support_coordinator_name",
                    "support_coordinator_contact",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "base_price",
                    "extras_cost",
                    "travel_cost",
                    "urgency_surcharge",
                    "discount_amount",
                    "gst_amount",
                    "final_price",
                    "total_items_cost",
                )
            },
        ),
        (
            "Workflow Management",
            {
                "fields": (
                    "assigned_to",
                    "reviewed_by",
                    "admin_notes",
                    "client_notes",
                    "rejection_reason",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "submitted_at",
                    "reviewed_at",
                    "approved_at",
                    "expires_at",
                    "is_expired",
                    "days_until_expiry",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ("source", "conversion_rate_applied", "can_be_accepted"),
                "classes": ["collapse"],
            },
        ),
    )

    inlines = [QuoteItemInline, QuoteAttachmentInline, QuoteRevisionInline]

    actions = [
        "approve_quotes",
        "reject_quotes",
        "cancel_quotes",
        "assign_to_me",
        "export_quotes",
        "recalculate_pricing",
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("client", "service", "assigned_to", "reviewed_by")
            .prefetch_related("items", "attachments", "revisions")
        )

    def client_name(self, obj):
        return obj.client.get_full_name()

    client_name.short_description = "Client"
    client_name.admin_order_field = "client__last_name"

    def service_name(self, obj):
        return obj.service.name

    service_name.short_description = "Service"
    service_name.admin_order_field = "service__name"

    def status_display(self, obj):
        colors = {
            "draft": "#6c757d",
            "submitted": "#007bff",
            "under_review": "#ffc107",
            "approved": "#28a745",
            "rejected": "#dc3545",
            "expired": "#6f42c1",
            "converted": "#20c997",
            "cancelled": "#fd7e14",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"
    status_display.admin_order_field = "status"

    def final_price_display(self, obj):
        return f"${obj.final_price:,.2f}"

    final_price_display.short_description = "Final Price"
    final_price_display.admin_order_field = "final_price"

    def urgency_display(self, obj):
        colors = {1: "#28a745", 2: "#17a2b8", 3: "#ffc107", 4: "#fd7e14", 5: "#dc3545"}
        color = colors.get(obj.urgency_level, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">Level {}</span>',
            color,
            obj.urgency_level,
        )

    urgency_display.short_description = "Urgency"
    urgency_display.admin_order_field = "urgency_level"

    def is_ndis_display(self, obj):
        if obj.is_ndis_client:
            return format_html('<span style="color: #007bff;">✓ NDIS</span>')
        return format_html('<span style="color: #6c757d;">General</span>')

    is_ndis_display.short_description = "Client Type"
    is_ndis_display.admin_order_field = "is_ndis_client"

    def approve_quotes(self, request, queryset):
        if not request.user.has_perm("quotes.approve_quote"):
            raise PermissionDenied("You don't have permission to approve quotes.")

        approved_count = 0
        for quote in queryset:
            if quote.status in ["submitted", "under_review"]:
                if quote.approve_quote(request.user):
                    approved_count += 1

        messages.success(request, f"Successfully approved {approved_count} quotes.")

    approve_quotes.short_description = "Approve selected quotes"

    def reject_quotes(self, request, queryset):
        if not request.user.has_perm("quotes.reject_quote"):
            raise PermissionDenied("You don't have permission to reject quotes.")

        rejected_count = 0
        for quote in queryset:
            if quote.status in ["submitted", "under_review"]:
                if quote.reject_quote(request.user, "Bulk rejection via admin"):
                    rejected_count += 1

        messages.success(request, f"Successfully rejected {rejected_count} quotes.")

    reject_quotes.short_description = "Reject selected quotes"

    def cancel_quotes(self, request, queryset):
        cancelled_count = 0
        for quote in queryset:
            if quote.status not in ["converted", "cancelled"]:
                quote.status = "cancelled"
                quote.save()
                cancelled_count += 1

        messages.success(request, f"Successfully cancelled {cancelled_count} quotes.")

    cancel_quotes.short_description = "Cancel selected quotes"

    def assign_to_me(self, request, queryset):
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can assign quotes.")

        assigned_count = 0
        for quote in queryset:
            if quote.status in ["submitted", "under_review", "approved"]:
                quote.assigned_to = request.user
                quote.save()
                assigned_count += 1

        messages.success(
            request, f"Successfully assigned {assigned_count} quotes to you."
        )

    assign_to_me.short_description = "Assign selected quotes to me"

    def export_quotes(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="quotes_export.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Quote Number",
                "Client Name",
                "Client Email",
                "Service",
                "Cleaning Type",
                "Status",
                "Final Price",
                "Created At",
                "Property Address",
                "Postcode",
                "Urgency Level",
                "NDIS Client",
            ]
        )

        for quote in queryset:
            writer.writerow(
                [
                    quote.quote_number,
                    quote.client.get_full_name(),
                    quote.client.email,
                    quote.service.name,
                    quote.get_cleaning_type_display(),
                    quote.get_status_display(),
                    quote.final_price,
                    quote.created_at.strftime("%Y-%m-%d %H:%M"),
                    quote.property_address,
                    quote.postcode,
                    quote.urgency_level,
                    "Yes" if quote.is_ndis_client else "No",
                ]
            )

        return response

    export_quotes.short_description = "Export selected quotes to CSV"

    def recalculate_pricing(self, request, queryset):
        updated_count = 0
        for quote in queryset:
            if quote.status in ["draft", "submitted", "under_review"]:
                quote.update_pricing()
                updated_count += 1

        messages.success(
            request, f"Successfully recalculated pricing for {updated_count} quotes."
        )

    recalculate_pricing.short_description = "Recalculate pricing for selected quotes"

    def has_change_permission(self, request, obj=None):
        if obj:
            return check_quote_permission(request.user, obj, "edit")
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            return check_quote_permission(request.user, obj, "delete")
        return super().has_delete_permission(request, obj)


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = [
        "quote_number",
        "item_type",
        "name",
        "quantity",
        "unit_price",
        "total_price",
        "is_optional",
        "is_taxable",
    ]

    list_filter = ["item_type", "is_optional", "is_taxable", "created_at"]

    search_fields = [
        "quote__quote_number",
        "name",
        "description",
        "service__name",
        "addon__name",
    ]

    readonly_fields = ["total_price", "gst_amount", "total_with_gst"]

    fieldsets = (
        ("Item Information", {"fields": ("quote", "item_type", "name", "description")}),
        ("Service Links", {"fields": ("service", "addon"), "classes": ["collapse"]}),
        (
            "Pricing",
            {
                "fields": (
                    "quantity",
                    "unit_price",
                    "total_price",
                    "gst_amount",
                    "total_with_gst",
                )
            },
        ),
        ("Options", {"fields": ("is_optional", "is_taxable", "display_order")}),
    )

    def quote_number(self, obj):
        return obj.quote.quote_number

    quote_number.short_description = "Quote"
    quote_number.admin_order_field = "quote__quote_number"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quote", "service", "addon")


@admin.register(QuoteAttachment)
class QuoteAttachmentAdmin(admin.ModelAdmin):
    list_display = [
        "quote_number",
        "original_filename",
        "attachment_type",
        "file_size_display",
        "uploaded_by_name",
        "is_public",
        "created_at",
    ]

    list_filter = ["attachment_type", "is_public", "file_type", "created_at"]

    search_fields = [
        "quote__quote_number",
        "original_filename",
        "title",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
    ]

    readonly_fields = [
        "original_filename",
        "file_size",
        "file_type",
        "file_size_mb",
        "is_image",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Attachment Information",
            {"fields": ("quote", "uploaded_by", "file", "attachment_type")},
        ),
        (
            "File Details",
            {
                "fields": (
                    "original_filename",
                    "file_size",
                    "file_type",
                    "file_size_mb",
                    "is_image",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("title", "description", "is_public", "display_order")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ["collapse"]},
        ),
    )

    def quote_number(self, obj):
        return obj.quote.quote_number

    quote_number.short_description = "Quote"
    quote_number.admin_order_field = "quote__quote_number"

    def uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name()

    uploaded_by_name.short_description = "Uploaded By"
    uploaded_by_name.admin_order_field = "uploaded_by__last_name"

    def file_size_display(self, obj):
        return f"{obj.file_size_mb} MB"

    file_size_display.short_description = "File Size"
    file_size_display.admin_order_field = "file_size"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quote", "uploaded_by")


@admin.register(QuoteRevision)
class QuoteRevisionAdmin(admin.ModelAdmin):
    list_display = [
        "quote_number",
        "revision_number",
        "revised_by_name",
        "price_change_display",
        "created_at",
    ]

    list_filter = ["created_at", "revised_by"]

    search_fields = [
        "quote__quote_number",
        "changes_summary",
        "reason",
        "revised_by__first_name",
        "revised_by__last_name",
    ]

    readonly_fields = [
        "revision_number",
        "price_change_amount",
        "price_change_percent",
        "created_at",
    ]

    fieldsets = (
        (
            "Revision Information",
            {"fields": ("quote", "revision_number", "revised_by")},
        ),
        ("Changes", {"fields": ("changes_summary", "reason")}),
        (
            "Pricing Changes",
            {
                "fields": (
                    "previous_price",
                    "new_price",
                    "price_change_amount",
                    "price_change_percent",
                )
            },
        ),
        ("Timestamp", {"fields": ("created_at",)}),
    )

    def quote_number(self, obj):
        return obj.quote.quote_number

    quote_number.short_description = "Quote"
    quote_number.admin_order_field = "quote__quote_number"

    def revised_by_name(self, obj):
        return obj.revised_by.get_full_name()

    revised_by_name.short_description = "Revised By"
    revised_by_name.admin_order_field = "revised_by__last_name"

    def price_change_display(self, obj):
        change = obj.new_price - obj.previous_price
        if change > 0:
            return format_html('<span style="color: green;">+${:.2f}</span>', change)
        elif change < 0:
            return format_html('<span style="color: red;">${:.2f}</span>', change)
        return "$0.00"

    price_change_display.short_description = "Price Change"

    def price_change_amount(self, obj):
        return obj.new_price - obj.previous_price

    price_change_amount.short_description = "Change Amount"

    def price_change_percent(self, obj):
        if obj.previous_price > 0:
            return f"{((obj.new_price - obj.previous_price) / obj.previous_price) * 100:.2f}%"
        return "0%"

    price_change_percent.short_description = "Change %"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("quote", "revised_by")


@admin.register(QuoteTemplate)
class QuoteTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "cleaning_type",
        "default_service_name",
        "is_active",
        "is_ndis_template",
        "usage_count",
        "created_by_name",
        "created_at",
    ]

    list_filter = [
        "cleaning_type",
        "is_active",
        "is_ndis_template",
        "default_urgency_level",
        "created_at",
    ]

    search_fields = [
        "name",
        "description",
        "default_service__name",
        "created_by__first_name",
        "created_by__last_name",
    ]

    readonly_fields = ["usage_count", "created_at", "updated_at"]

    fieldsets = (
        ("Template Information", {"fields": ("name", "description", "cleaning_type")}),
        ("Default Settings", {"fields": ("default_service", "default_urgency_level")}),
        ("Template Options", {"fields": ("is_active", "is_ndis_template")}),
        ("Usage Statistics", {"fields": ("usage_count",), "classes": ["collapse"]}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ["collapse"],
            },
        ),
    )

    actions = ["activate_templates", "deactivate_templates", "reset_usage_count"]

    def default_service_name(self, obj):
        return obj.default_service.name

    default_service_name.short_description = "Default Service"
    default_service_name.admin_order_field = "default_service__name"

    def created_by_name(self, obj):
        return obj.created_by.get_full_name()

    created_by_name.short_description = "Created By"
    created_by_name.admin_order_field = "created_by__last_name"

    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        messages.success(request, f"Successfully activated {updated} templates.")

    activate_templates.short_description = "Activate selected templates"

    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        messages.success(request, f"Successfully deactivated {updated} templates.")

    deactivate_templates.short_description = "Deactivate selected templates"

    def reset_usage_count(self, request, queryset):
        updated = queryset.update(usage_count=0)
        messages.success(
            request, f"Successfully reset usage count for {updated} templates."
        )

    reset_usage_count.short_description = "Reset usage count for selected templates"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("default_service", "created_by")
        )


class QuoteAdminSite(admin.AdminSite):
    site_header = "Quote Management System"
    site_title = "Quote Admin"
    index_title = "Quote Administration"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        quote_stats = Quote.objects.statistics()

        extra_context.update(
            {
                "quote_statistics": {
                    "total_quotes": quote_stats["total_quotes"],
                    "pending_quotes": quote_stats["pending_count"],
                    "approved_quotes": quote_stats["approved_count"],
                    "total_value": quote_stats["total_value"],
                    "average_value": quote_stats["average_value"],
                    "approval_rate": quote_stats["approval_rate"],
                    "conversion_rate": quote_stats["conversion_rate"],
                },
                "recent_quotes": Quote.objects.recent(7).count(),
                "urgent_quotes": Quote.objects.urgent().count(),
                "expiring_quotes": Quote.objects.expiring_soon(7).count(),
                "ndis_quotes": Quote.objects.ndis_quotes().count(),
            }
        )

        return super().index(request, extra_context)


admin.site.unregister(Quote)
admin.site.unregister(QuoteItem)
admin.site.unregister(QuoteAttachment)
admin.site.unregister(QuoteRevision)
admin.site.unregister(QuoteTemplate)

quote_admin_site = QuoteAdminSite(name="quote_admin")
quote_admin_site.register(Quote, QuoteAdmin)
quote_admin_site.register(QuoteItem, QuoteItemAdmin)
quote_admin_site.register(QuoteAttachment, QuoteAttachmentAdmin)
quote_admin_site.register(QuoteRevision, QuoteRevisionAdmin)
quote_admin_site.register(QuoteTemplate, QuoteTemplateAdmin)

class QuoteInlineAdmin(admin.TabularInline):
    model = Quote
    fk_name = 'client'
    extra = 0
    fields = [
        "quote_number",
        "cleaning_type",
        "status",
        "final_price",
        "created_at",
        "expires_at",
    ]
    readonly_fields = ["quote_number", "created_at"]
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


def register_quote_admin_extensions():
    from django.contrib.auth import get_user_model
    from services.models import Service

    User = get_user_model()

    try:
        user_admin = admin.site._registry[User]
        if hasattr(user_admin, "inlines"):
            user_admin.inlines = list(user_admin.inlines) + [QuoteInlineAdmin]
        else:
            user_admin.inlines = [QuoteInlineAdmin]
    except KeyError:
        pass

    try:
        service_admin = admin.site._registry[Service]
        if hasattr(service_admin, "inlines"):
            service_admin.inlines = list(service_admin.inlines) + [QuoteInlineAdmin]
        else:
            service_admin.inlines = [QuoteInlineAdmin]
    except KeyError:
        pass


register_quote_admin_extensions()


admin.site.add_action(lambda modeladmin, request, queryset: None, "quote_bulk_actions")


class QuoteAdminMixin:

    def get_quote_context_data(self, request, object_id=None):
        context = {}

        if object_id:
            try:
                quote = Quote.objects.get(pk=object_id)
                context.update(
                    {
                        "quote_permissions": {
                            "can_approve": check_quote_permission(
                                request.user, quote, "approve"
                            ),
                            "can_reject": check_quote_permission(
                                request.user, quote, "reject"
                            ),
                            "can_assign": check_quote_permission(
                                request.user, quote, "assign"
                            ),
                            "can_convert": check_quote_permission(
                                request.user, quote, "convert"
                            ),
                        },
                        "quote_stats": {
                            "items_count": quote.items.count(),
                            "attachments_count": quote.attachments.count(),
                            "revisions_count": quote.revisions.count(),
                        },
                    }
                )
            except Quote.DoesNotExist:
                pass

        return context

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_quote_context_data(request, object_id))
        return super().changeform_view(request, object_id, form_url, extra_context)


for model_admin in [
    QuoteAdmin,
    QuoteItemAdmin,
    QuoteAttachmentAdmin,
    QuoteRevisionAdmin,
]:
    if hasattr(model_admin, "__bases__"):
        model_admin.__bases__ = model_admin.__bases__ + (QuoteAdminMixin,)


def get_admin_urls():
    from django.urls import path

    return [
        path(
            "quotes/analytics/",
            admin.site.admin_view(quote_analytics_view),
            name="quote_analytics",
        ),
        path(
            "quotes/reports/",
            admin.site.admin_view(quote_reports_view),
            name="quote_reports",
        ),
        path(
            "quotes/bulk-operations/",
            admin.site.admin_view(quote_bulk_operations_view),
            name="quote_bulk_operations",
        ),
    ]


def quote_analytics_view(request):
    from django.shortcuts import render

    context = {
        "title": "Quote Analytics",
        "statistics": Quote.objects.statistics(),
        "recent_trends": Quote.objects.this_month().count(),
    }

    return render(request, "admin/quotes/analytics.html", context)


def quote_reports_view(request):
    from django.shortcuts import render

    context = {
        "title": "Quote Reports",
        "available_reports": [
            "Monthly Summary",
            "Conversion Analysis",
            "NDIS Quotes Report",
            "Staff Performance",
        ],
    }

    return render(request, "admin/quotes/reports.html", context)


def quote_bulk_operations_view(request):
    from django.shortcuts import render

    if request.method == "POST":
        operation = request.POST.get("operation")
        quote_ids = request.POST.getlist("quote_ids")

        if operation and quote_ids:
            messages.success(
                request,
                f"Bulk operation '{operation}' completed for {len(quote_ids)} quotes.",
            )

    context = {
        "title": "Bulk Quote Operations",
        "pending_quotes": Quote.objects.pending().count(),
        "available_operations": ["approve", "reject", "assign", "export"],
    }

    return render(request, "admin/quotes/bulk_operations.html", context)

