from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter
from .models import (
    Service,
    ServiceCategory,
    ServiceArea,
    NDISServiceCode,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)


class ServiceAreaFilter(SimpleListFilter):
    title = "Service Area"
    parameter_name = "service_area"

    def lookups(self, request, model_admin):
        areas = ServiceArea.objects.active().values_list("state", "state").distinct()
        return [(state, state) for state, _ in areas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_areas__state=self.value()).distinct()
        return queryset


class NDISEligibilityFilter(SimpleListFilter):
    title = "NDIS Eligibility"
    parameter_name = "ndis_eligible"

    def lookups(self, request, model_admin):
        return [
            ("yes", "NDIS Eligible"),
            ("no", "Not NDIS Eligible"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_ndis_eligible=True)
        if self.value() == "no":
            return queryset.filter(is_ndis_eligible=False)
        return queryset


class ServiceTypeFilter(SimpleListFilter):
    title = "Service Type"
    parameter_name = "service_type"

    def lookups(self, request, model_admin):
        return Service.SERVICE_TYPES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_type=self.value())
        return queryset


class ServiceAvailabilityInline(admin.TabularInline):
    model = ServiceAvailability
    extra = 0
    fields = ("day_of_week", "start_time", "end_time", "is_available", "max_bookings")
    ordering = ("day_of_week", "start_time")


class ServicePricingInline(admin.TabularInline):
    model = ServicePricing
    extra = 0
    fields = (
        "tier",
        "price",
        "description",
        "is_active",
        "effective_from",
        "effective_to",
    )
    ordering = ("tier",)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category_type",
        "is_ndis_eligible",
        "is_active",
        "service_count_display",
        "display_order",
        "created_at",
    )
    list_filter = ("category_type", "is_ndis_eligible", "is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "slug", "category_type", "description", "icon")},
        ),
        ("Settings", {"fields": ("is_active", "is_ndis_eligible", "display_order")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def service_count_display(self, obj):
        count = obj.services.filter(is_active=True).count()
        if count > 0:
            url = reverse("admin:services_service_changelist")
            return format_html(
                '<a href="{}?category__id__exact={}">{} services</a>',
                url,
                obj.id,
                count,
            )
        return "0 services"

    service_count_display.short_description = "Active Services"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                service_count=Count("services", filter=Q(services__is_active=True))
            )
        )


@admin.register(NDISServiceCode)
class NDISServiceCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "unit_type",
        "standard_rate",
        "is_active",
        "is_current_display",
        "effective_from",
        "effective_to",
    )
    list_filter = ("is_active", "unit_type", "effective_from", "created_at")
    search_fields = ("code", "name", "description")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "NDIS Code Information",
            {"fields": ("code", "name", "description", "unit_type")},
        ),
        ("Pricing", {"fields": ("standard_rate",)}),
        (
            "Validity Period",
            {"fields": ("effective_from", "effective_to", "is_active")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def is_current_display(self, obj):
        if obj.is_current:
            return format_html('<span style="color: green;">✓ Current</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')

    is_current_display.short_description = "Status"

    actions = ["make_active", "make_inactive"]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} NDIS service codes marked as active.")

    make_active.short_description = "Mark selected codes as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} NDIS service codes marked as inactive.")

    make_inactive.short_description = "Mark selected codes as inactive"


@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = (
        "suburb",
        "postcode",
        "state",
        "is_active",
        "travel_time_minutes",
        "travel_cost",
        "priority_level",
    )
    list_filter = ("state", "is_active", "priority_level")
    search_fields = ("suburb", "postcode")
    ordering = ("state", "suburb")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Location", {"fields": ("suburb", "postcode", "state")}),
        (
            "Service Details",
            {
                "fields": (
                    "travel_time_minutes",
                    "travel_cost",
                    "service_radius_km",
                    "priority_level",
                )
            },
        ),
        ("Settings", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["make_active", "make_inactive", "set_high_priority"]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} service areas activated.")

    make_active.short_description = "Activate selected areas"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} service areas deactivated.")

    make_inactive.short_description = "Deactivate selected areas"

    def set_high_priority(self, request, queryset):
        updated = queryset.update(priority_level=5)
        self.message_user(request, f"{updated} service areas set to high priority.")

    set_high_priority.short_description = "Set high priority"


@admin.register(ServiceAddOn)
class ServiceAddOnAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "addon_type",
        "price",
        "is_active",
        "is_optional",
        "service_count",
    )
    list_filter = ("addon_type", "is_active", "is_optional")
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("services",)

    fieldsets = (
        (
            "Add-on Information",
            {"fields": ("name", "addon_type", "description", "price")},
        ),
        ("Settings", {"fields": ("is_active", "is_optional")}),
        ("Associated Services", {"fields": ("services",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def service_count(self, obj):
        return obj.services.count()

    service_count.short_description = "Services"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "service_type",
        "pricing_type",
        "price_display",
        "is_active",
        "is_featured",
        "is_ndis_eligible",
        "requires_quote",
        "display_order",
    )
    list_filter = (
        "is_active",
        "is_featured",
        NDISEligibilityFilter,
        "requires_quote",
        "category",
        ServiceTypeFilter,
        "pricing_type",
        ServiceAreaFilter,
        "created_at",
    )
    search_fields = ("name", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")
    readonly_fields = ("created_at", "updated_at", "price_display", "duration_display")
    filter_horizontal = ("service_areas", "addons")
    inlines = [ServiceAvailabilityInline, ServicePricingInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "category",
                    "service_type",
                    "description",
                    "short_description",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "pricing_type",
                    "base_price",
                    "hourly_rate",
                    "minimum_charge",
                    "price_display",
                )
            },
        ),
        (
            "Duration & Capacity",
            {
                "fields": (
                    "estimated_duration",
                    "duration_unit",
                    "duration_display",
                    "minimum_rooms",
                    "maximum_rooms",
                )
            },
        ),
        (
            "NDIS Information",
            {
                "fields": ("is_ndis_eligible", "ndis_service_code"),
                "classes": ("collapse",),
            },
        ),
        ("Service Details", {"fields": ("equipment_required", "special_requirements")}),
        (
            "Settings",
            {"fields": ("is_active", "is_featured", "requires_quote", "display_order")},
        ),
        (
            "Associations",
            {"fields": ("service_areas", "addons"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = [
        "make_active",
        "make_inactive",
        "make_featured",
        "remove_featured",
        "enable_ndis",
        "disable_ndis",
        "require_quote",
        "enable_instant_booking",
    ]

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} services activated.")

    make_active.short_description = "Activate selected services"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} services deactivated.")

    make_inactive.short_description = "Deactivate selected services"

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} services marked as featured.")

    make_featured.short_description = "Mark as featured"

    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} services removed from featured.")

    remove_featured.short_description = "Remove from featured"

    def enable_ndis(self, request, queryset):
        updated = queryset.update(is_ndis_eligible=True)
        self.message_user(request, f"{updated} services enabled for NDIS.")

    enable_ndis.short_description = "Enable NDIS eligibility"

    def disable_ndis(self, request, queryset):
        updated = queryset.update(is_ndis_eligible=False)
        self.message_user(request, f"{updated} services disabled for NDIS.")

    disable_ndis.short_description = "Disable NDIS eligibility"

    def require_quote(self, request, queryset):
        updated = queryset.update(requires_quote=True)
        self.message_user(request, f"{updated} services now require quotes.")

    require_quote.short_description = "Require quote"

    def enable_instant_booking(self, request, queryset):
        updated = queryset.update(requires_quote=False)
        self.message_user(request, f"{updated} services enabled for instant booking.")

    enable_instant_booking.short_description = "Enable instant booking"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category", "ndis_service_code")
            .prefetch_related("service_areas", "addons")
        )


@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "get_day_of_week_display",
        "start_time",
        "end_time",
        "is_available",
        "max_bookings",
    )
    list_filter = ("day_of_week", "is_available", "service__category")
    search_fields = ("service__name",)
    ordering = ("service", "day_of_week", "start_time")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Service & Schedule",
            {"fields": ("service", "day_of_week", "start_time", "end_time")},
        ),
        ("Availability", {"fields": ("is_available", "max_bookings")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ServicePricing)
class ServicePricingAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "tier",
        "price",
        "is_active",
        "is_current_display",
        "effective_from",
        "effective_to",
    )
    list_filter = ("tier", "is_active", "effective_from", "service__category")
    search_fields = ("service__name", "description")
    ordering = ("service", "tier")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Service & Tier", {"fields": ("service", "tier", "description")}),
        ("Pricing", {"fields": ("price",)}),
        ("Validity", {"fields": ("is_active", "effective_from", "effective_to")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def is_current_display(self, obj):
        if obj.is_current:
            return format_html('<span style="color: green;">✓ Current</span>')
        return format_html('<span style="color: red;">✗ Not Current</span>')

    is_current_display.short_description = "Current Status"


admin.site.site_header = "Professional Cleaning Service Administration"
admin.site.site_title = "Cleaning Service Admin"
admin.site.index_title = "Service Management Dashboard"

