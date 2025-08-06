from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from .managers import (
    ServiceManager,
    ServiceCategoryManager,
    ServiceAreaManager,
    NDISServiceCodeManager,
)
from .validators import (
    validate_postcode,
    validate_service_duration,
    validate_ndis_service_code,
    validate_pricing,
)

User = get_user_model()


class ServiceCategory(models.Model):
    CATEGORY_TYPES = (
        ("general", "General Cleaning"),
        ("ndis", "NDIS Services"),
        ("commercial", "Commercial Cleaning"),
        ("specialized", "Specialized Services"),
    )

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category_type = models.CharField(
        max_length=20, choices=CATEGORY_TYPES, default="general"
    )
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_ndis_eligible = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ServiceCategoryManager()

    class Meta:
        db_table = "service_categories"
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    @property
    def service_count(self):
        return self.services.filter(is_active=True).count()


class NDISServiceCode(models.Model):
    code = models.CharField(
        max_length=20, unique=True, validators=[validate_ndis_service_code]
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    unit_type = models.CharField(max_length=50)
    standard_rate = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NDISServiceCodeManager()

    class Meta:
        db_table = "ndis_service_codes"
        verbose_name = "NDIS Service Code"
        verbose_name_plural = "NDIS Service Codes"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.effective_from <= today and (
            self.effective_to is None or self.effective_to >= today
        )


class ServiceArea(models.Model):
    STATE_CHOICES = (
        ("NSW", "New South Wales"),
        ("VIC", "Victoria"),
        ("QLD", "Queensland"),
        ("WA", "Western Australia"),
        ("SA", "South Australia"),
        ("TAS", "Tasmania"),
        ("ACT", "Australian Capital Territory"),
        ("NT", "Northern Territory"),
    )

    suburb = models.CharField(max_length=100)
    postcode = models.CharField(max_length=4, validators=[validate_postcode])
    state = models.CharField(max_length=3, choices=STATE_CHOICES)
    is_active = models.BooleanField(default=True)
    travel_time_minutes = models.PositiveIntegerField(default=0)
    travel_cost = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    service_radius_km = models.PositiveIntegerField(default=50)
    priority_level = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ServiceAreaManager()

    class Meta:
        db_table = "service_areas"
        verbose_name = "Service Area"
        verbose_name_plural = "Service Areas"
        unique_together = ["suburb", "postcode", "state"]
        ordering = ["state", "suburb"]

    def __str__(self):
        return f"{self.suburb}, {self.state} {self.postcode}"

    @property
    def full_location(self):
        return f"{self.suburb}, {self.state} {self.postcode}"


class Service(models.Model):
    SERVICE_TYPES = (
        ("general", "General Cleaning"),
        ("deep", "Deep Cleaning"),
        ("end_of_lease", "End of Lease Cleaning"),
        ("ndis", "NDIS Cleaning"),
        ("commercial", "Commercial Cleaning"),
        ("carpet", "Carpet Cleaning"),
        ("window", "Window Cleaning"),
        ("pressure_washing", "Pressure Washing"),
    )

    PRICING_TYPES = (
        ("fixed", "Fixed Price"),
        ("hourly", "Hourly Rate"),
        ("per_room", "Per Room"),
        ("per_sqm", "Per Square Meter"),
        ("ndis_rate", "NDIS Standard Rate"),
    )

    DURATION_UNITS = (
        ("minutes", "Minutes"),
        ("hours", "Hours"),
        ("days", "Days"),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="services"
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    short_description = models.CharField(max_length=300)

    pricing_type = models.CharField(
        max_length=20, choices=PRICING_TYPES, default="fixed"
    )
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_pricing]
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    minimum_charge = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )

    estimated_duration = models.PositiveIntegerField(
        validators=[validate_service_duration]
    )
    duration_unit = models.CharField(
        max_length=10, choices=DURATION_UNITS, default="hours"
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_ndis_eligible = models.BooleanField(default=False)
    requires_quote = models.BooleanField(default=False)

    ndis_service_code = models.ForeignKey(
        NDISServiceCode, on_delete=models.SET_NULL, null=True, blank=True
    )
    service_areas = models.ManyToManyField(ServiceArea, related_name="services")

    minimum_rooms = models.PositiveIntegerField(default=1)
    maximum_rooms = models.PositiveIntegerField(null=True, blank=True)

    equipment_required = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ServiceManager()

    class Meta:
        db_table = "services"
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["service_type", "is_active"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_ndis_eligible", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        if self.pricing_type == "fixed":
            return f"${self.base_price}"
        elif self.pricing_type == "hourly":
            return f"${self.hourly_rate}/hour"
        elif self.pricing_type == "per_room":
            return f"${self.base_price}/room"
        elif self.pricing_type == "per_sqm":
            return f"${self.base_price}/sqm"
        elif self.pricing_type == "ndis_rate":
            return f"NDIS Rate: ${self.base_price}"
        return f"${self.base_price}"

    @property
    def duration_display(self):
        return f"{self.estimated_duration} {self.duration_unit}"

    def calculate_price(self, rooms=1, hours=None, square_meters=None):
        if self.pricing_type == "fixed":
            return self.base_price
        elif self.pricing_type == "hourly" and hours:
            return max(self.hourly_rate * hours, self.minimum_charge)
        elif self.pricing_type == "per_room":
            return self.base_price * rooms
        elif self.pricing_type == "per_sqm" and square_meters:
            return self.base_price * square_meters
        elif self.pricing_type == "ndis_rate":
            return self.base_price
        return self.base_price

    def is_available_in_area(self, postcode):
        return self.service_areas.filter(postcode=postcode, is_active=True).exists()


class ServiceAddOn(models.Model):
    ADDON_TYPES = (
        ("extra_service", "Extra Service"),
        ("equipment", "Equipment"),
        ("material", "Material"),
        ("upgrade", "Service Upgrade"),
    )

    name = models.CharField(max_length=100)
    addon_type = models.CharField(max_length=20, choices=ADDON_TYPES)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    is_active = models.BooleanField(default=True)
    is_optional = models.BooleanField(default=True)
    services = models.ManyToManyField(Service, related_name="addons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_addons"
        verbose_name = "Service Add-on"
        verbose_name_plural = "Service Add-ons"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (+${self.price})"


class ServiceAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="availability"
    )
    day_of_week = models.PositiveIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_bookings = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_availability"
        verbose_name = "Service Availability"
        verbose_name_plural = "Service Availabilities"
        unique_together = ["service", "day_of_week", "start_time"]
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.service.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ServicePricing(models.Model):
    PRICING_TIERS = (
        ("standard", "Standard"),
        ("premium", "Premium"),
        ("ndis", "NDIS"),
        ("commercial", "Commercial"),
    )

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="pricing_tiers"
    )
    tier = models.CharField(max_length=20, choices=PRICING_TIERS)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(default=timezone.now)
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_pricing"
        verbose_name = "Service Pricing"
        verbose_name_plural = "Service Pricing"
        unique_together = ["service", "tier"]
        ordering = ["service", "tier"]

    def __str__(self):
        return f"{self.service.name} - {self.tier} (${self.price})"

    @property
    def is_current(self):
        today = timezone.now().date()
        return self.effective_from <= today and (
            self.effective_to is None or self.effective_to >= today
        )
