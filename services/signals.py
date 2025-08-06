from django.db.models.signals import (
    post_save,
    pre_save,
    post_delete,
    pre_delete,
    m2m_changed,
)
from django.db.models import F  
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging
from .models import (
    Service,
    ServiceCategory,
    ServiceArea,
    NDISServiceCode,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)
from .utils import generate_service_slug, optimize_service_display_order

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Service)
def service_pre_save(sender, instance, **kwargs):
    try:
        if not instance.slug or instance.slug == "":
            instance.slug = generate_service_slug(instance.name, instance.id)

        if instance.pricing_type == "hourly" and not instance.hourly_rate:
            instance.hourly_rate = instance.base_price

        if instance.is_ndis_eligible and not instance.ndis_service_code:
            logger.warning(
                f"NDIS eligible service '{instance.name}' created without NDIS service code"
            )

        if instance.maximum_rooms and instance.minimum_rooms:
            if instance.maximum_rooms < instance.minimum_rooms:
                instance.maximum_rooms = instance.minimum_rooms
                logger.warning(
                    f"Adjusted maximum rooms for service '{instance.name}' to match minimum rooms"
                )

        if instance.base_price < Decimal("0.01"):
            instance.base_price = Decimal("0.01")
            logger.warning(
                f"Adjusted base price for service '{instance.name}' to minimum value"
            )

    except Exception as e:
        logger.error(f"Error in service pre_save signal: {str(e)}")


@receiver(post_save, sender=Service)
def service_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"New service created: {instance.name} (ID: {instance.id})")

            if instance.is_featured:
                optimize_service_display_order(instance.category.id)

            cache.delete("featured_services")
            cache.delete(f"category_services_{instance.category.slug}")
            cache.delete("service_stats")
        else:
            logger.info(f"Service updated: {instance.name} (ID: {instance.id})")

            if "is_active" in kwargs.get("update_fields", []):
                cache.delete("active_services_count")

            if "is_featured" in kwargs.get("update_fields", []):
                cache.delete("featured_services")
                optimize_service_display_order(instance.category.id)

        cache.delete(f"service_{instance.id}")
        cache.delete(f"service_slug_{instance.slug}")

        if instance.is_ndis_eligible:
            cache.delete("ndis_services")

    except Exception as e:
        logger.error(f"Error in service post_save signal: {str(e)}")


@receiver(pre_delete, sender=Service)
def service_pre_delete(sender, instance, **kwargs):
    try:
        logger.info(f"Service being deleted: {instance.name} (ID: {instance.id})")

        if hasattr(instance, "bookings") and instance.bookings.exists():
            logger.warning(f"Deleting service '{instance.name}' with existing bookings")

        if hasattr(instance, "quotes") and instance.quotes.exists():
            logger.warning(f"Deleting service '{instance.name}' with existing quotes")

    except Exception as e:
        logger.error(f"Error in service pre_delete signal: {str(e)}")


@receiver(post_delete, sender=Service)
def service_post_delete(sender, instance, **kwargs):
    try:
        logger.info(f"Service deleted: {instance.name} (ID: {instance.id})")

        cache.delete(f"service_{instance.id}")
        cache.delete(f"service_slug_{instance.slug}")
        cache.delete("featured_services")
        cache.delete(f"category_services_{instance.category.slug}")
        cache.delete("service_stats")
        cache.delete("active_services_count")

        if instance.is_ndis_eligible:
            cache.delete("ndis_services")

        optimize_service_display_order(instance.category.id)

    except Exception as e:
        logger.error(f"Error in service post_delete signal: {str(e)}")


@receiver(m2m_changed, sender=Service.service_areas.through)
def service_areas_changed(sender, instance, action, pk_set, **kwargs):
    try:
        if action in ["post_add", "post_remove", "post_clear"]:
            logger.info(f"Service areas updated for service: {instance.name}")

            cache.delete(f"service_{instance.id}")
            cache.delete(f"service_areas_{instance.id}")

            if pk_set:
                for area_id in pk_set:
                    cache.delete(f"area_services_{area_id}")

    except Exception as e:
        logger.error(f"Error in service_areas_changed signal: {str(e)}")


@receiver(m2m_changed, sender=Service.addons.through)
def service_addons_changed(sender, instance, action, pk_set, **kwargs):
    try:
        if action in ["post_add", "post_remove", "post_clear"]:
            logger.info(f"Service add-ons updated for service: {instance.name}")

            cache.delete(f"service_{instance.id}")
            cache.delete(f"service_addons_{instance.id}")

    except Exception as e:
        logger.error(f"Error in service_addons_changed signal: {str(e)}")


@receiver(post_save, sender=ServiceCategory)
def service_category_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"New service category created: {instance.name}")
        else:
            logger.info(f"Service category updated: {instance.name}")

        cache.delete("service_categories")
        cache.delete(f"category_{instance.slug}")
        cache.delete("categories_with_services")

        if instance.is_ndis_eligible:
            cache.delete("ndis_categories")

    except Exception as e:
        logger.error(f"Error in service_category_post_save signal: {str(e)}")


@receiver(post_delete, sender=ServiceCategory)
def service_category_post_delete(sender, instance, **kwargs):
    try:
        logger.info(f"Service category deleted: {instance.name}")

        cache.delete("service_categories")
        cache.delete(f"category_{instance.slug}")
        cache.delete("categories_with_services")

        if instance.is_ndis_eligible:
            cache.delete("ndis_categories")

    except Exception as e:
        logger.error(f"Error in service_category_post_delete signal: {str(e)}")


@receiver(post_save, sender=ServiceArea)
def service_area_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"New service area created: {instance.full_location}")
        else:
            logger.info(f"Service area updated: {instance.full_location}")

        cache.delete("service_areas")
        cache.delete(f"area_{instance.postcode}")
        cache.delete(f"state_areas_{instance.state}")

        for service in instance.services.all():
            cache.delete(f"service_{service.id}")

    except Exception as e:
        logger.error(f"Error in service_area_post_save signal: {str(e)}")


@receiver(post_delete, sender=ServiceArea)
def service_area_post_delete(sender, instance, **kwargs):
    try:
        logger.info(f"Service area deleted: {instance.full_location}")

        cache.delete("service_areas")
        cache.delete(f"area_{instance.postcode}")
        cache.delete(f"state_areas_{instance.state}")

    except Exception as e:
        logger.error(f"Error in service_area_post_delete signal: {str(e)}")


@receiver(post_save, sender=NDISServiceCode)
def ndis_service_code_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"New NDIS service code created: {instance.code}")
        else:
            logger.info(f"NDIS service code updated: {instance.code}")

        cache.delete("ndis_service_codes")
        cache.delete(f"ndis_code_{instance.code}")

        if not instance.is_active:
            affected_services = Service.objects.filter(ndis_service_code=instance)
            for service in affected_services:
                logger.warning(
                    f"Service '{service.name}' uses inactive NDIS code '{instance.code}'"
                )

    except Exception as e:
        logger.error(f"Error in ndis_service_code_post_save signal: {str(e)}")


@receiver(post_save, sender=ServiceAddOn)
def service_addon_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"New service add-on created: {instance.name}")
        else:
            logger.info(f"Service add-on updated: {instance.name}")

        cache.delete("service_addons")
        cache.delete(f"addon_{instance.id}")

        for service in instance.services.all():
            cache.delete(f"service_{service.id}")
            cache.delete(f"service_addons_{service.id}")

    except Exception as e:
        logger.error(f"Error in service_addon_post_save signal: {str(e)}")


@receiver(post_save, sender=ServiceAvailability)
def service_availability_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(
                f"New availability slot created for service: {instance.service.name}"
            )
        else:
            logger.info(
                f"Availability slot updated for service: {instance.service.name}"
            )

        cache.delete(f"service_availability_{instance.service.id}")
        cache.delete(f"service_{instance.service.id}")

        if not instance.is_available:
            logger.info(
                f"Availability slot disabled for {instance.service.name} on {instance.get_day_of_week_display()}"
            )

    except Exception as e:
        logger.error(f"Error in service_availability_post_save signal: {str(e)}")


@receiver(post_save, sender=ServicePricing)
def service_pricing_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(
                f"New pricing tier created for service: {instance.service.name} - {instance.tier}"
            )
        else:
            logger.info(
                f"Pricing tier updated for service: {instance.service.name} - {instance.tier}"
            )

        cache.delete(f"service_pricing_{instance.service.id}")
        cache.delete(f"service_{instance.service.id}")
        cache.delete(f"pricing_tier_{instance.service.id}_{instance.tier}")

        if instance.is_current and instance.price != instance.service.base_price:
            logger.info(
                f"Price difference detected for {instance.service.name}: base=${instance.service.base_price}, {instance.tier}=${instance.price}"
            )

    except Exception as e:
        logger.error(f"Error in service_pricing_post_save signal: {str(e)}")


@receiver(pre_save, sender=ServicePricing)
def service_pricing_pre_save(sender, instance, **kwargs):
    try:
        if instance.effective_to and instance.effective_from:
            if instance.effective_to <= instance.effective_from:
                logger.warning(
                    f"Invalid date range for pricing tier {instance.tier} of service {instance.service.name}"
                )
                instance.effective_to = None

        if instance.price < Decimal("0.01"):
            instance.price = Decimal("0.01")
            logger.warning(
                f"Adjusted pricing for service '{instance.service.name}' tier '{instance.tier}' to minimum value"
            )

    except Exception as e:
        logger.error(f"Error in service_pricing_pre_save signal: {str(e)}")


def clear_service_caches():
    try:
        cache_keys = [
            "featured_services",
            "service_stats",
            "active_services_count",
            "ndis_services",
            "service_categories",
            "categories_with_services",
            "ndis_categories",
            "service_areas",
            "ndis_service_codes",
            "service_addons",
        ]

        for key in cache_keys:
            cache.delete(key)

        logger.info("Service caches cleared")

    except Exception as e:
        logger.error(f"Error clearing service caches: {str(e)}")


def log_service_activity(service, action, user=None, details=None):
    try:
        activity_data = {
            "service_id": service.id,
            "service_name": service.name,
            "action": action,
            "timestamp": timezone.now(),
            "user_id": user.id if user else None,
            "user_email": user.email if user else None,
            "details": details or {},
        }

        logger.info(f"Service activity: {activity_data}")

    except Exception as e:
        logger.error(f"Error logging service activity: {str(e)}")


def validate_service_integrity():
    try:
        issues = []

        services_without_areas = Service.objects.filter(
            is_active=True, service_areas__isnull=True
        )
        if services_without_areas.exists():
            issues.append(
                f"{services_without_areas.count()} active services have no service areas"
            )

        ndis_services_without_codes = Service.objects.filter(
            is_ndis_eligible=True, ndis_service_code__isnull=True
        )
        if ndis_services_without_codes.exists():
            issues.append(
                f"{ndis_services_without_codes.count()} NDIS services have no service codes"
            )

        services_with_invalid_rooms = Service.objects.filter(
            maximum_rooms__lt=F("minimum_rooms")
        )

        if services_with_invalid_rooms.exists():
            issues.append(
                f"{services_with_invalid_rooms.count()} services have invalid room configurations"
            )

        if issues:
            logger.warning(f"Service integrity issues found: {'; '.join(issues)}")
        else:
            logger.info("Service integrity validation passed")

        return issues

    except Exception as e:
        logger.error(f"Error in service integrity validation: {str(e)}")
        return [f"Validation error: {str(e)}"]
