from django.db import models
from django.utils import timezone
from django.db.models import Q, Count, Avg, Min, Max
from decimal import Decimal


class ServiceCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def by_type(self, category_type):
        return self.active().filter(category_type=category_type)

    def ndis_eligible(self):
        return self.active().filter(is_ndis_eligible=True)

    def with_services(self):
        return (
            self.active()
            .annotate(
                service_count=Count("services", filter=Q(services__is_active=True))
            )
            .filter(service_count__gt=0)
        )

    def ordered(self):
        return self.active().order_by("display_order", "name")


class NDISServiceCodeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def current(self):
        today = timezone.now().date()
        return (
            self.active()
            .filter(effective_from__lte=today)
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        )

    def by_code(self, code):
        return self.current().filter(code=code).first()

    def search(self, query):
        return self.current().filter(
            Q(code__icontains=query)
            | Q(name__icontains=query)
            | Q(description__icontains=query)
        )


class ServiceAreaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def by_state(self, state):
        return self.active().filter(state=state)

    def by_postcode(self, postcode):
        return self.active().filter(postcode=postcode)

    def by_suburb(self, suburb):
        return self.active().filter(suburb__icontains=suburb)

    def within_radius(self, center_postcode, radius_km):
        return self.active().filter(service_radius_km__gte=radius_km)

    def priority_areas(self):
        return self.active().filter(priority_level__gte=3).order_by("-priority_level")

    def search_location(self, query):
        return (
            self.active()
            .filter(Q(suburb__icontains=query) | Q(postcode__icontains=query))
            .order_by("suburb")
        )


class ServiceManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "ndis_service_code")
            .prefetch_related("service_areas", "addons")
        )

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def featured(self):
        return self.active().filter(is_featured=True)

    def by_type(self, service_type):
        return self.active().filter(service_type=service_type)

    def by_category(self, category):
        if isinstance(category, str):
            return self.active().filter(category__slug=category)
        return self.active().filter(category=category)

    def ndis_eligible(self):
        return self.active().filter(is_ndis_eligible=True)

    def general_services(self):
        return self.active().filter(is_ndis_eligible=False)

    def by_pricing_type(self, pricing_type):
        return self.active().filter(pricing_type=pricing_type)

    def requires_quote(self):
        return self.active().filter(requires_quote=True)

    def instant_booking(self):
        return self.active().filter(requires_quote=False)

    def available_in_area(self, postcode):
        return (
            self.active()
            .filter(service_areas__postcode=postcode, service_areas__is_active=True)
            .distinct()
        )

    def available_in_suburb(self, suburb):
        return (
            self.active()
            .filter(
                service_areas__suburb__icontains=suburb, service_areas__is_active=True
            )
            .distinct()
        )

    def by_price_range(self, min_price=None, max_price=None):
        queryset = self.active()
        if min_price is not None:
            queryset = queryset.filter(base_price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(base_price__lte=max_price)
        return queryset

    def by_duration_range(self, min_duration=None, max_duration=None):
        queryset = self.active()
        if min_duration is not None:
            queryset = queryset.filter(estimated_duration__gte=min_duration)
        if max_duration is not None:
            queryset = queryset.filter(estimated_duration__lte=max_duration)
        return queryset

    def search(self, query):
        return (
            self.active()
            .filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(short_description__icontains=query)
                | Q(category__name__icontains=query)
            )
            .distinct()
        )

    def with_pricing_stats(self):
        return self.active().aggregate(
            min_price=Min("base_price"),
            max_price=Max("base_price"),
            avg_price=Avg("base_price"),
            total_services=Count("id"),
        )

    def popular_services(self, limit=10):
        return self.featured().order_by("display_order", "name")[:limit]

    def recommended_for_user(self, user):
        if hasattr(user, "is_ndis_client") and user.is_ndis_client:
            return self.ndis_eligible().order_by("display_order", "name")
        return self.general_services().order_by("display_order", "name")

    def available_today(self):
        today = timezone.now().weekday()
        current_time = timezone.now().time()

        return (
            self.active()
            .filter(
                availability__day_of_week=today,
                availability__is_available=True,
                availability__start_time__lte=current_time,
                availability__end_time__gte=current_time,
            )
            .distinct()
        )

    def with_addons(self):
        return (
            self.active()
            .prefetch_related("addons")
            .annotate(addon_count=Count("addons", filter=Q(addons__is_active=True)))
            .filter(addon_count__gt=0)
        )

    def bulk_activate(self, service_ids):
        return self.filter(id__in=service_ids).update(is_active=True)

    def bulk_deactivate(self, service_ids):
        return self.filter(id__in=service_ids).update(is_active=False)

    def bulk_feature(self, service_ids):
        return self.filter(id__in=service_ids).update(is_featured=True)

    def bulk_unfeature(self, service_ids):
        return self.filter(id__in=service_ids).update(is_featured=False)

    def get_service_with_pricing(self, service_id, tier="standard"):
        try:
            service = self.get(id=service_id)
            pricing = (
                service.pricing_tiers.filter(
                    tier=tier, is_active=True, effective_from__lte=timezone.now().date()
                )
                .filter(
                    Q(effective_to__isnull=True)
                    | Q(effective_to__gte=timezone.now().date())
                )
                .first()
            )

            if pricing:
                service._current_pricing = pricing
            return service
        except self.model.DoesNotExist:
            return None

    def services_by_location_and_type(self, postcode, service_type=None):
        queryset = self.available_in_area(postcode)
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        return queryset.order_by("display_order", "name")

    def calculate_service_metrics(self):
        return {
            "total_active": self.active().count(),
            "ndis_services": self.ndis_eligible().count(),
            "general_services": self.general_services().count(),
            "featured_services": self.featured().count(),
            "quote_required": self.requires_quote().count(),
            "instant_booking": self.instant_booking().count(),
            "price_range": self.with_pricing_stats(),
            "service_types": self.active()
            .values("service_type")
            .annotate(count=Count("id"))
            .order_by("-count"),
        }


class ServiceAvailabilityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("service")

    def available(self):
        return self.get_queryset().filter(is_available=True)

    def for_service(self, service):
        return self.available().filter(service=service)

    def for_day(self, day_of_week):
        return self.available().filter(day_of_week=day_of_week)

    def current_availability(self):
        today = timezone.now().weekday()
        current_time = timezone.now().time()

        return self.available().filter(
            day_of_week=today, start_time__lte=current_time, end_time__gte=current_time
        )

    def get_weekly_schedule(self, service):
        return self.for_service(service).order_by("day_of_week", "start_time")

    def has_capacity(self, service, day_of_week, time_slot):
        availability = (
            self.available()
            .filter(
                service=service,
                day_of_week=day_of_week,
                start_time__lte=time_slot,
                end_time__gte=time_slot,
            )
            .first()
        )

        if not availability:
            return False

        return availability.max_bookings > 0


class ServicePricingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("service")

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def current(self):
        today = timezone.now().date()
        return (
            self.active()
            .filter(effective_from__lte=today)
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        )

    def by_tier(self, tier):
        return self.current().filter(tier=tier)

    def for_service(self, service):
        return self.current().filter(service=service)

    def get_current_price(self, service, tier="standard"):
        pricing = self.current().filter(service=service, tier=tier).first()
        return pricing.price if pricing else service.base_price

    def bulk_update_prices(self, service_ids, tier, new_price, effective_from=None):
        if effective_from is None:
            effective_from = timezone.now().date()

        return self.filter(service_id__in=service_ids, tier=tier).update(
            price=new_price, effective_from=effective_from, updated_at=timezone.now()
        )
