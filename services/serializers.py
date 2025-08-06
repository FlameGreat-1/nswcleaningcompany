from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from .models import (
    Service,
    ServiceCategory,
    ServiceArea,
    NDISServiceCode,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)
from .validators import (
    validate_postcode,
    validate_service_duration,
    validate_ndis_service_code,
    validate_pricing,
    validate_service_name,
    validate_service_description,
    validate_hourly_rate,
    validate_room_count,
    validate_square_meters,
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    service_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServiceCategory
        fields = (
            "id",
            "name",
            "slug",
            "category_type",
            "description",
            "icon",
            "is_active",
            "is_ndis_eligible",
            "display_order",
            "service_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "service_count", "created_at", "updated_at")

    def validate_name(self, value):
        validate_service_name(value)
        return value

    def validate_description(self, value):
        validate_service_description(value)
        return value


class ServiceCategoryListSerializer(serializers.ModelSerializer):
    service_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServiceCategory
        fields = (
            "id",
            "name",
            "slug",
            "category_type",
            "icon",
            "is_ndis_eligible",
            "service_count",
        )


class NDISServiceCodeSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = NDISServiceCode
        fields = (
            "id",
            "code",
            "name",
            "description",
            "unit_type",
            "standard_rate",
            "is_active",
            "is_current",
            "effective_from",
            "effective_to",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_current", "created_at", "updated_at")

    def validate_code(self, value):
        validate_ndis_service_code(value)
        return value

    def validate_standard_rate(self, value):
        validate_pricing(value)
        return value

    def validate(self, attrs):
        effective_from = attrs.get("effective_from")
        effective_to = attrs.get("effective_to")

        if effective_to and effective_from and effective_to <= effective_from:
            raise serializers.ValidationError(
                "Effective end date must be after start date"
            )

        return attrs


class ServiceAreaSerializer(serializers.ModelSerializer):
    full_location = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceArea
        fields = (
            "id",
            "suburb",
            "postcode",
            "state",
            "full_location",
            "is_active",
            "travel_time_minutes",
            "travel_cost",
            "service_radius_km",
            "priority_level",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "full_location", "created_at", "updated_at")

    def validate_postcode(self, value):
        validate_postcode(value)
        return value

    def validate_travel_cost(self, value):
        if value < Decimal("0"):
            raise serializers.ValidationError("Travel cost cannot be negative")
        return value


class ServiceAreaListSerializer(serializers.ModelSerializer):
    full_location = serializers.CharField(read_only=True)

    class Meta:
        model = ServiceArea
        fields = ("id", "suburb", "postcode", "state", "full_location")


class ServiceAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAddOn
        fields = (
            "id",
            "name",
            "addon_type",
            "description",
            "price",
            "is_active",
            "is_optional",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_price(self, value):
        validate_pricing(value)
        return value


class ServiceAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = ServiceAvailability
        fields = (
            "id",
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
            "is_available",
            "max_bookings",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "day_name", "created_at", "updated_at")

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time")

        return attrs


class ServicePricingSerializer(serializers.ModelSerializer):
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = ServicePricing
        fields = (
            "id",
            "tier",
            "price",
            "description",
            "is_active",
            "is_current",
            "effective_from",
            "effective_to",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_current", "created_at", "updated_at")

    def validate_price(self, value):
        validate_pricing(value)
        return value


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    ndis_service_code_display = serializers.CharField(
        source="ndis_service_code.code", read_only=True
    )
    price_display = serializers.CharField(read_only=True)
    duration_display = serializers.CharField(read_only=True)
    service_areas = ServiceAreaListSerializer(many=True, read_only=True)
    addons = ServiceAddOnSerializer(many=True, read_only=True)
    availability = ServiceAvailabilitySerializer(many=True, read_only=True)
    pricing_tiers = ServicePricingSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "category_name",
            "category_slug",
            "service_type",
            "description",
            "short_description",
            "pricing_type",
            "base_price",
            "hourly_rate",
            "minimum_charge",
            "price_display",
            "estimated_duration",
            "duration_unit",
            "duration_display",
            "is_active",
            "is_featured",
            "is_ndis_eligible",
            "requires_quote",
            "ndis_service_code",
            "ndis_service_code_display",
            "minimum_rooms",
            "maximum_rooms",
            "equipment_required",
            "special_requirements",
            "display_order",
            "service_areas",
            "addons",
            "availability",
            "pricing_tiers",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "category_name",
            "category_slug",
            "ndis_service_code_display",
            "price_display",
            "duration_display",
            "service_areas",
            "addons",
            "availability",
            "pricing_tiers",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        validate_service_name(value)
        return value

    def validate_description(self, value):
        validate_service_description(value)
        return value

    def validate_base_price(self, value):
        validate_pricing(value)
        return value

    def validate_hourly_rate(self, value):
        if value is not None:
            validate_hourly_rate(value)
        return value

    def validate_estimated_duration(self, value):
        validate_service_duration(value)
        return value

    def validate_minimum_rooms(self, value):
        validate_room_count(value)
        return value

    def validate_maximum_rooms(self, value):
        if value is not None:
            validate_room_count(value)
        return value

    def validate(self, attrs):
        pricing_type = attrs.get("pricing_type")
        hourly_rate = attrs.get("hourly_rate")
        minimum_rooms = attrs.get("minimum_rooms", 1)
        maximum_rooms = attrs.get("maximum_rooms")

        if pricing_type == "hourly" and not hourly_rate:
            raise serializers.ValidationError(
                "Hourly rate is required for hourly pricing type"
            )

        if maximum_rooms and minimum_rooms and maximum_rooms < minimum_rooms:
            raise serializers.ValidationError(
                "Maximum rooms cannot be less than minimum rooms"
            )

        is_ndis_eligible = attrs.get("is_ndis_eligible", False)
        ndis_service_code = attrs.get("ndis_service_code")

        if is_ndis_eligible and not ndis_service_code:
            raise serializers.ValidationError(
                "NDIS service code is required for NDIS eligible services"
            )

        return attrs


class ServiceListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    price_display = serializers.CharField(read_only=True)
    duration_display = serializers.CharField(read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "slug",
            "category_name",
            "service_type",
            "short_description",
            "price_display",
            "duration_display",
            "is_featured",
            "is_ndis_eligible",
            "requires_quote",
        )


class ServiceDetailSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    ndis_service_code = NDISServiceCodeSerializer(read_only=True)
    service_areas = ServiceAreaSerializer(many=True, read_only=True)
    addons = ServiceAddOnSerializer(many=True, read_only=True)
    availability = ServiceAvailabilitySerializer(many=True, read_only=True)
    pricing_tiers = ServicePricingSerializer(many=True, read_only=True)
    price_display = serializers.CharField(read_only=True)
    duration_display = serializers.CharField(read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "service_type",
            "description",
            "short_description",
            "pricing_type",
            "base_price",
            "hourly_rate",
            "minimum_charge",
            "price_display",
            "estimated_duration",
            "duration_unit",
            "duration_display",
            "is_active",
            "is_featured",
            "is_ndis_eligible",
            "requires_quote",
            "ndis_service_code",
            "minimum_rooms",
            "maximum_rooms",
            "equipment_required",
            "special_requirements",
            "service_areas",
            "addons",
            "availability",
            "pricing_tiers",
            "created_at",
            "updated_at",
        )


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    service_area_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    addon_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Service
        fields = (
            "name",
            "slug",
            "category",
            "service_type",
            "description",
            "short_description",
            "pricing_type",
            "base_price",
            "hourly_rate",
            "minimum_charge",
            "estimated_duration",
            "duration_unit",
            "is_active",
            "is_featured",
            "is_ndis_eligible",
            "requires_quote",
            "ndis_service_code",
            "minimum_rooms",
            "maximum_rooms",
            "equipment_required",
            "special_requirements",
            "display_order",
            "service_area_ids",
            "addon_ids",
        )

    def create(self, validated_data):
        service_area_ids = validated_data.pop("service_area_ids", [])
        addon_ids = validated_data.pop("addon_ids", [])

        service = Service.objects.create(**validated_data)

        if service_area_ids:
            service.service_areas.set(service_area_ids)

        if addon_ids:
            service.addons.set(addon_ids)

        return service

    def update(self, instance, validated_data):
        service_area_ids = validated_data.pop("service_area_ids", None)
        addon_ids = validated_data.pop("addon_ids", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if service_area_ids is not None:
            instance.service_areas.set(service_area_ids)

        if addon_ids is not None:
            instance.addons.set(addon_ids)

        return instance


class ServiceQuoteRequestSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    rooms = serializers.IntegerField(default=1, validators=[validate_room_count])
    square_meters = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        validators=[validate_square_meters],
    )
    hours = serializers.IntegerField(required=False, min_value=1, max_value=12)
    postcode = serializers.CharField(validators=[validate_postcode])
    addon_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
    special_requests = serializers.CharField(max_length=1000, required=False)
    preferred_date = serializers.DateField(required=False)
    preferred_time = serializers.TimeField(required=False)

    def validate_service_id(self, value):
        try:
            service = Service.objects.active().get(id=value)
            return value
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive")

    def validate_preferred_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Preferred date cannot be in the past")
        return value

    def validate(self, attrs):
        service_id = attrs.get("service_id")
        postcode = attrs.get("postcode")
        addon_ids = attrs.get("addon_ids", [])

        try:
            service = Service.objects.get(id=service_id)

            if not service.is_available_in_area(postcode):
                raise serializers.ValidationError(
                    "Service is not available in the specified area"
                )

            if addon_ids:
                valid_addons = service.addons.filter(
                    id__in=addon_ids, is_active=True
                ).count()
                if valid_addons != len(addon_ids):
                    raise serializers.ValidationError(
                        "Some selected add-ons are not available for this service"
                    )

        except Service.DoesNotExist:
            raise serializers.ValidationError("Service not found")

        return attrs


class ServiceSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    service_type = serializers.CharField(required=False)
    postcode = serializers.CharField(required=False, validators=[validate_postcode])
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    max_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    is_ndis_eligible = serializers.BooleanField(required=False)
    requires_quote = serializers.BooleanField(required=False)
    is_featured = serializers.BooleanField(required=False)

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")

        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError(
                "Minimum price cannot be greater than maximum price"
            )

        return attrs


class ServiceStatsSerializer(serializers.Serializer):
    total_services = serializers.IntegerField()
    active_services = serializers.IntegerField()
    ndis_services = serializers.IntegerField()
    featured_services = serializers.IntegerField()
    services_by_type = serializers.DictField()
    services_by_category = serializers.DictField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_range = serializers.DictField()


class BulkServiceActionSerializer(serializers.Serializer):
    service_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1, max_length=100
    )
    action = serializers.ChoiceField(
        choices=[
            ("activate", "Activate"),
            ("deactivate", "Deactivate"),
            ("feature", "Feature"),
            ("unfeature", "Unfeature"),
            ("delete", "Delete"),
        ]
    )

    def validate_service_ids(self, value):
        existing_ids = Service.objects.filter(id__in=value).values_list("id", flat=True)
        if len(existing_ids) != len(value):
            missing_ids = set(value) - set(existing_ids)
            raise serializers.ValidationError(
                f"Services with IDs {list(missing_ids)} do not exist"
            )
        return value
