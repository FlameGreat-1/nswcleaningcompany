import django_filters
from django.db.models import Q, Count, Avg
from django.utils import timezone
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


class ServiceCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Category Name"
    )

    category_type = django_filters.ChoiceFilter(
        field_name="category_type",
        choices=ServiceCategory.CATEGORY_TYPES,
        label="Category Type",
    )

    is_active = django_filters.BooleanFilter(field_name="is_active", label="Active")

    is_ndis_eligible = django_filters.BooleanFilter(
        field_name="is_ndis_eligible", label="NDIS Eligible"
    )

    has_services = django_filters.BooleanFilter(
        method="filter_has_services", label="Has Active Services"
    )

    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Created After"
    )

    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Created Before"
    )

    class Meta:
        model = ServiceCategory
        fields = [
            "name",
            "category_type",
            "is_active",
            "is_ndis_eligible",
            "has_services",
            "created_after",
            "created_before",
        ]

    def filter_has_services(self, queryset, name, value):
        if value:
            return queryset.annotate(
                service_count=Count("services", filter=Q(services__is_active=True))
            ).filter(service_count__gt=0)
        return queryset


class ServiceAreaFilter(django_filters.FilterSet):
    suburb = django_filters.CharFilter(
        field_name="suburb", lookup_expr="icontains", label="Suburb"
    )

    postcode = django_filters.CharFilter(
        field_name="postcode", lookup_expr="exact", label="Postcode"
    )

    postcode_range = django_filters.CharFilter(
        method="filter_postcode_range", label="Postcode Range (e.g., 2000-2099)"
    )

    state = django_filters.ChoiceFilter(
        field_name="state", choices=ServiceArea.STATE_CHOICES, label="State"
    )

    is_active = django_filters.BooleanFilter(field_name="is_active", label="Active")

    priority_level = django_filters.NumberFilter(
        field_name="priority_level", label="Priority Level"
    )

    priority_min = django_filters.NumberFilter(
        field_name="priority_level", lookup_expr="gte", label="Minimum Priority"
    )

    travel_cost_max = django_filters.NumberFilter(
        field_name="travel_cost", lookup_expr="lte", label="Maximum Travel Cost"
    )

    travel_time_max = django_filters.NumberFilter(
        field_name="travel_time_minutes",
        lookup_expr="lte",
        label="Maximum Travel Time (minutes)",
    )

    service_radius_min = django_filters.NumberFilter(
        field_name="service_radius_km",
        lookup_expr="gte",
        label="Minimum Service Radius (km)",
    )

    class Meta:
        model = ServiceArea
        fields = [
            "suburb",
            "postcode",
            "postcode_range",
            "state",
            "is_active",
            "priority_level",
            "priority_min",
            "travel_cost_max",
            "travel_time_max",
            "service_radius_min",
        ]

    def filter_postcode_range(self, queryset, name, value):
        if "-" in value:
            try:
                start, end = value.split("-")
                start_code = int(start.strip())
                end_code = int(end.strip())
                return queryset.filter(
                    postcode__gte=str(start_code).zfill(4),
                    postcode__lte=str(end_code).zfill(4),
                )
            except (ValueError, AttributeError):
                pass
        return queryset


class NDISServiceCodeFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(
        field_name="code", lookup_expr="icontains", label="Service Code"
    )

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Service Name"
    )

    unit_type = django_filters.CharFilter(
        field_name="unit_type", lookup_expr="icontains", label="Unit Type"
    )

    is_active = django_filters.BooleanFilter(field_name="is_active", label="Active")

    is_current = django_filters.BooleanFilter(
        method="filter_is_current", label="Currently Valid"
    )

    standard_rate_min = django_filters.NumberFilter(
        field_name="standard_rate", lookup_expr="gte", label="Minimum Rate"
    )

    standard_rate_max = django_filters.NumberFilter(
        field_name="standard_rate", lookup_expr="lte", label="Maximum Rate"
    )

    effective_from = django_filters.DateFilter(
        field_name="effective_from", lookup_expr="gte", label="Effective From"
    )

    effective_to = django_filters.DateFilter(
        field_name="effective_to", lookup_expr="lte", label="Effective To"
    )

    support_category = django_filters.CharFilter(
        method="filter_support_category", label="Support Category (first 2 digits)"
    )

    class Meta:
        model = NDISServiceCode
        fields = [
            "code",
            "name",
            "unit_type",
            "is_active",
            "is_current",
            "standard_rate_min",
            "standard_rate_max",
            "effective_from",
            "effective_to",
            "support_category",
        ]

    def filter_is_current(self, queryset, name, value):
        today = timezone.now().date()
        if value:
            return queryset.filter(effective_from__lte=today, is_active=True).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=today)
            )
        return queryset

    def filter_support_category(self, queryset, name, value):
        if value and len(value) >= 2:
            return queryset.filter(code__startswith=value[:2])
        return queryset


class ServiceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Service Name"
    )

    search = django_filters.CharFilter(method="filter_search", label="Search")

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        queryset=ServiceCategory.objects.filter(is_active=True),
        label="Category",
    )

    category_slug = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="exact", label="Category Slug"
    )

    service_type = django_filters.ChoiceFilter(
        field_name="service_type", choices=Service.SERVICE_TYPES, label="Service Type"
    )

    pricing_type = django_filters.ChoiceFilter(
        field_name="pricing_type", choices=Service.PRICING_TYPES, label="Pricing Type"
    )

    is_active = django_filters.BooleanFilter(field_name="is_active", label="Active")

    is_featured = django_filters.BooleanFilter(
        field_name="is_featured", label="Featured"
    )

    is_ndis_eligible = django_filters.BooleanFilter(
        field_name="is_ndis_eligible", label="NDIS Eligible"
    )

    requires_quote = django_filters.BooleanFilter(
        field_name="requires_quote", label="Requires Quote"
    )

    base_price_min = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="gte", label="Minimum Price"
    )

    base_price_max = django_filters.NumberFilter(
        field_name="base_price", lookup_expr="lte", label="Maximum Price"
    )

    price_range = django_filters.CharFilter(
        method="filter_price_range", label="Price Range (e.g., 50-200)"
    )

    duration_min = django_filters.NumberFilter(
        field_name="estimated_duration", lookup_expr="gte", label="Minimum Duration"
    )

    duration_max = django_filters.NumberFilter(
        field_name="estimated_duration", lookup_expr="lte", label="Maximum Duration"
    )

    duration_unit = django_filters.ChoiceFilter(
        field_name="duration_unit",
        choices=Service.DURATION_UNITS,
        label="Duration Unit",
    )

    rooms_min = django_filters.NumberFilter(
        field_name="minimum_rooms",
        lookup_expr="lte",
        label="Suitable for Rooms (minimum)",
    )

    rooms_max = django_filters.NumberFilter(
        field_name="maximum_rooms",
        lookup_expr="gte",
        label="Suitable for Rooms (maximum)",
    )

    postcode = django_filters.CharFilter(
        method="filter_postcode", label="Available in Postcode"
    )

    state = django_filters.ChoiceFilter(
        method="filter_state",
        choices=ServiceArea.STATE_CHOICES,
        label="Available in State",
    )

    suburb = django_filters.CharFilter(
        method="filter_suburb", label="Available in Suburb"
    )

    ndis_service_code = django_filters.ModelChoiceFilter(
        field_name='ndis_service_code',
        queryset=NDISServiceCode.objects.filter(is_active=True),
        label='NDIS Service Code'
    )
    
    has_addons = django_filters.BooleanFilter(
        method='filter_has_addons',
        label='Has Add-ons'
    )
    
    has_availability = django_filters.BooleanFilter(
        method='filter_has_availability',
        label='Has Availability'
    )
    
    available_today = django_filters.BooleanFilter(
        method='filter_available_today',
        label='Available Today'
    )
    
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created After'
    )
    
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created Before'
    )
    
    updated_after = django_filters.DateFilter(
        field_name='updated_at',
        lookup_expr='gte',
        label='Updated After'
    )
    
    class Meta:
        model = Service
        fields = [
            'name', 'search', 'category', 'category_slug', 'service_type',
            'pricing_type', 'is_active', 'is_featured', 'is_ndis_eligible',
            'requires_quote', 'base_price_min', 'base_price_max', 'price_range',
            'duration_min', 'duration_max', 'duration_unit', 'rooms_min',
            'rooms_max', 'postcode', 'state', 'suburb', 'ndis_service_code',
            'has_addons', 'has_availability', 'available_today',
            'created_after', 'created_before', 'updated_after'
        ]
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(category__name__icontains=value)
            ).distinct()
        return queryset
    
    def filter_price_range(self, queryset, name, value):
        if '-' in value:
            try:
                min_price, max_price = value.split('-')
                min_price = Decimal(min_price.strip())
                max_price = Decimal(max_price.strip())
                return queryset.filter(
                    base_price__gte=min_price,
                    base_price__lte=max_price
                )
            except (ValueError, AttributeError):
                pass
        return queryset
    
    def filter_postcode(self, queryset, name, value):
        if value:
            return queryset.filter(
                service_areas__postcode=value,
                service_areas__is_active=True
            ).distinct()
        return queryset
    
    def filter_state(self, queryset, name, value):
        if value:
            return queryset.filter(
                service_areas__state=value,
                service_areas__is_active=True
            ).distinct()
        return queryset
    
    def filter_suburb(self, queryset, name, value):
        if value:
            return queryset.filter(
                service_areas__suburb__icontains=value,
                service_areas__is_active=True
            ).distinct()
        return queryset
    
    def filter_has_addons(self, queryset, name, value):
        if value:
            return queryset.annotate(
                addon_count=Count('addons', filter=Q(addons__is_active=True))
            ).filter(addon_count__gt=0)
        return queryset
    
    def filter_has_availability(self, queryset, name, value):
        if value:
            return queryset.annotate(
                availability_count=Count('availability', filter=Q(availability__is_available=True))
            ).filter(availability_count__gt=0)
        return queryset
    
    def filter_available_today(self, queryset, name, value):
        if value:
            today = timezone.now().weekday()
            current_time = timezone.now().time()
            return queryset.filter(
                availability__day_of_week=today,
                availability__is_available=True,
                availability__start_time__lte=current_time,
                availability__end_time__gte=current_time
            ).distinct()
        return queryset


class ServiceAddOnFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Add-on Name'
    )
    
    addon_type = django_filters.ChoiceFilter(
        field_name='addon_type',
        choices=ServiceAddOn.ADDON_TYPES,
        label='Add-on Type'
    )
    
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Active'
    )
    
    is_optional = django_filters.BooleanFilter(
        field_name='is_optional',
        label='Optional'
    )
    
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Minimum Price'
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Maximum Price'
    )
    
    service = django_filters.ModelChoiceFilter(
        field_name='services',
        queryset=Service.objects.filter(is_active=True),
        label='Available for Service'
    )
    
    service_category = django_filters.ModelChoiceFilter(
        method='filter_service_category',
        queryset=ServiceCategory.objects.filter(is_active=True),
        label='Available for Category'
    )
    
    class Meta:
        model = ServiceAddOn
        fields = [
            'name', 'addon_type', 'is_active', 'is_optional',
            'price_min', 'price_max', 'service', 'service_category'
        ]
    
    def filter_service_category(self, queryset, name, value):
        if value:
            return queryset.filter(services__category=value).distinct()
        return queryset


class ServiceAvailabilityFilter(django_filters.FilterSet):
    service = django_filters.ModelChoiceFilter(
        field_name='service',
        queryset=Service.objects.filter(is_active=True),
        label='Service'
    )
    
    day_of_week = django_filters.ChoiceFilter(
        field_name='day_of_week',
        choices=ServiceAvailability.DAYS_OF_WEEK,
        label='Day of Week'
    )
    
    is_available = django_filters.BooleanFilter(
        field_name='is_available',
        label='Available'
    )
    
    start_time_after = django_filters.TimeFilter(
        field_name='start_time',
        lookup_expr='gte',
        label='Start Time After'
    )
    
    end_time_before = django_filters.TimeFilter(
        field_name='end_time',
        lookup_expr='lte',
        label='End Time Before'
    )
    
    max_bookings_min = django_filters.NumberFilter(
        field_name='max_bookings',
        lookup_expr='gte',
        label='Minimum Capacity'
    )
    
    weekdays_only = django_filters.BooleanFilter(
        method='filter_weekdays_only',
        label='Weekdays Only'
    )
    
    weekends_only = django_filters.BooleanFilter(
        method='filter_weekends_only',
        label='Weekends Only'
    )
    
    class Meta:
        model = ServiceAvailability
        fields = [
            'service', 'day_of_week', 'is_available', 'start_time_after',
            'end_time_before', 'max_bookings_min', 'weekdays_only', 'weekends_only'
        ]
    
    def filter_weekdays_only(self, queryset, name, value):
        if value:
            return queryset.filter(day_of_week__in=[0, 1, 2, 3, 4])
        return queryset
    
    def filter_weekends_only(self, queryset, name, value):
        if value:
            return queryset.filter(day_of_week__in=[5, 6])
        return queryset


class ServicePricingFilter(django_filters.FilterSet):
    service = django_filters.ModelChoiceFilter(
        field_name='service',
        queryset=Service.objects.filter(is_active=True),
        label='Service'
    )
    
    tier = django_filters.ChoiceFilter(
        field_name='tier',
        choices=ServicePricing.PRICING_TIERS,
        label='Pricing Tier'
    )
    
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='Active'
    )
    
    is_current = django_filters.BooleanFilter(
        method='filter_is_current',
        label='Currently Valid'
    )
    
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Minimum Price'
    )
    
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Maximum Price'
    )
    
    effective_from = django_filters.DateFilter(
        field_name='effective_from',
        lookup_expr='gte',
        label='Effective From'
    )
    
    effective_to = django_filters.DateFilter(
        field_name='effective_to',
        lookup_expr='lte',
        label='Effective To'
    )
    
    service_category = django_filters.ModelChoiceFilter(
        field_name='service__category',
        queryset=ServiceCategory.objects.filter(is_active=True),
        label='Service Category'
    )
    
    class Meta:
        model = ServicePricing
        fields = [
            'service', 'tier', 'is_active', 'is_current', 'price_min',
            'price_max', 'effective_from', 'effective_to', 'service_category'
        ]
    
    def filter_is_current(self, queryset, name, value):
        today = timezone.now().date()
        if value:
            return queryset.filter(
                effective_from__lte=today,
                is_active=True
            ).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=today)
            )
        return queryset


class ServiceReportFilter(django_filters.FilterSet):
    """Advanced filter for service reporting and analytics"""
    
    date_range = django_filters.CharFilter(
        method='filter_date_range',
        label='Date Range (YYYY-MM-DD to YYYY-MM-DD)'
    )
    
    performance_metric = django_filters.ChoiceFilter(
        method='filter_performance_metric',
        choices=[
            ('popular', 'Most Popular'),
            ('profitable', 'Most Profitable'),
            ('recent', 'Recently Added'),
            ('updated', 'Recently Updated'),
        ],
        label='Performance Metric'
    )
    
    price_comparison = django_filters.ChoiceFilter(
        method='filter_price_comparison',
        choices=[
            ('above_average', 'Above Average Price'),
            ('below_average', 'Below Average Price'),
            ('premium', 'Premium Services'),
            ('budget', 'Budget Services'),
        ],
        label='Price Comparison'
    )
    
    availability_status = django_filters.ChoiceFilter(
        method='filter_availability_status',
        choices=[
            ('high_availability', 'High Availability'),
            ('limited_availability', 'Limited Availability'),
            ('no_availability', 'No Availability'),
        ],
        label='Availability Status'
    )
    
    market_segment = django_filters.ChoiceFilter(
        method='filter_market_segment',
        choices=[
            ('ndis_only', 'NDIS Only'),
            ('general_only', 'General Market Only'),
            ('both_markets', 'Both Markets'),
        ],
        label='Market Segment'
    )
    
    class Meta:
        model = Service
        fields = [
            'date_range', 'performance_metric', 'price_comparison',
            'availability_status', 'market_segment'
        ]
    
    def filter_date_range(self, queryset, name, value):
        if ' to ' in value:
            try:
                start_date, end_date = value.split(' to ')
                start_date = timezone.datetime.strptime(start_date.strip(), '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date.strip(), '%Y-%m-%d').date()
                return queryset.filter(
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date
                )
            except (ValueError, AttributeError):
                pass
        return queryset
    
    def filter_performance_metric(self, queryset, name, value):
        if value == 'popular':
            return queryset.filter(is_featured=True).order_by('display_order')
        elif value == 'profitable':
            return queryset.order_by('-base_price')
        elif value == 'recent':
            return queryset.order_by('-created_at')
        elif value == 'updated':
            return queryset.order_by('-updated_at')
        return queryset
    
    def filter_price_comparison(self, queryset, name, value):
        avg_price = queryset.aggregate(avg_price=Avg('base_price'))['avg_price']
        if avg_price:
            if value == 'above_average':
                return queryset.filter(base_price__gt=avg_price)
            elif value == 'below_average':
                return queryset.filter(base_price__lt=avg_price)
            elif value == 'premium':
                return queryset.filter(base_price__gte=avg_price * Decimal('1.5'))
            elif value == 'budget':
                return queryset.filter(base_price__lte=avg_price * Decimal('0.7'))
        return queryset
    
    def filter_availability_status(self, queryset, name, value):
        if value == 'high_availability':
            return queryset.annotate(
                availability_count=Count('availability', filter=Q(availability__is_available=True))
            ).filter(availability_count__gte=20)
        elif value == 'limited_availability':
            return queryset.annotate(
                availability_count=Count('availability', filter=Q(availability__is_available=True))
            ).filter(availability_count__gt=0, availability_count__lt=20)
        elif value == 'no_availability':
            return queryset.annotate(
                availability_count=Count('availability', filter=Q(availability__is_available=True))
            ).filter(availability_count=0)
        return queryset
    
    def filter_market_segment(self, queryset, name, value):
        if value == 'ndis_only':
            return queryset.filter(is_ndis_eligible=True)
        elif value == 'general_only':
            return queryset.filter(is_ndis_eligible=False)
        elif value == 'both_markets':
            return queryset.filter(is_ndis_eligible=True)
        return queryset


class ServiceSearchFilter(django_filters.FilterSet):
    """Comprehensive search filter for frontend service discovery"""
    
    q = django_filters.CharFilter(
        method='filter_global_search',
        label='Search Query'
    )
    
    location = django_filters.CharFilter(
        method='filter_location',
        label='Location (Postcode or Suburb)'
    )
    
    budget = django_filters.CharFilter(
        method='filter_budget',
        label='Budget Range (e.g., 0-100, 100+)'
    )
    
    urgency = django_filters.ChoiceFilter(
        method='filter_urgency',
        choices=[
            ('today', 'Today'),
            ('this_week', 'This Week'),
            ('flexible', 'Flexible'),
        ],
        label='Urgency'
    )
    
    class Meta:
        model = Service
        fields = ['q', 'location', 'budget', 'urgency']
    
    def filter_global_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(category__name__icontains=value) |
                Q(service_type__icontains=value)
            ).distinct()
        return queryset
    
    def filter_location(self, queryset, name, value):
        if value:
            if value.isdigit() and len(value) == 4:
                return queryset.filter(
                    service_areas__postcode=value,
                    service_areas__is_active=True
                ).distinct()
            else:
                return queryset.filter(
                    service_areas__suburb__icontains=value,
                    service_areas__is_active=True
                ).distinct()
        return queryset
    
    def filter_budget(self, queryset, name, value):
        if value:
            if value.endswith('+'):
                min_price = Decimal(value[:-1])
                return queryset.filter(base_price__gte=min_price)
            elif '-' in value:
                try:
                    min_price, max_price = value.split('-')
                    return queryset.filter(
                        base_price__gte=Decimal(min_price),
                        base_price__lte=Decimal(max_price)
                    )
                except (ValueError, AttributeError):
                    pass
        return queryset
    
    def filter_urgency(self, queryset, name, value):
        today = timezone.now().weekday()
        current_time = timezone.now().time()
        
        if value == 'today':
            return queryset.filter(
                availability__day_of_week=today,
                availability__is_available=True,
                availability__start_time__lte=current_time,
                availability__end_time__gte=current_time,
                requires_quote=False
            ).distinct()
        elif value == 'this_week':
            return queryset.filter(
                availability__is_available=True,
                requires_quote=False
            ).distinct()
        elif value == 'flexible':
            return queryset.filter(requires_quote=True)
        
        return queryset


