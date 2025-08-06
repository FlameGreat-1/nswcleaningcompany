from django.apps import AppConfig
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services"
    verbose_name = "Service Management"

    def ready(self):
        """
        Initialize the services app when Django starts.
        This method is called once Django has loaded all models.
        """
        try:
            from . import signals

            from .models import (
                Service,
                ServiceCategory,
                ServiceArea,
                NDISServiceCode,
                ServiceAddOn,
                ServiceAvailability,
                ServicePricing,
            )

            self._initialize_cache_keys()

            if self._is_development_environment():
                self._validate_service_integrity()

            logger.info(f"Services app '{self.name}' initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing services app: {str(e)}")

    def _initialize_cache_keys(self):
        """Initialize cache keys used by the services app"""
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
                cache.get(f"services:{key}")

            logger.debug("Services cache keys initialized")

        except Exception as e:
            logger.warning(f"Could not initialize cache keys: {str(e)}")

    def _validate_service_integrity(self):
        """Validate service data integrity on startup (development only)"""
        try:
            from .signals import validate_service_integrity

            issues = validate_service_integrity()

            if issues:
                logger.warning(f"Service integrity issues found: {len(issues)} issues")
                for issue in issues:
                    logger.warning(f"  - {issue}")
            else:
                logger.info("Service integrity validation passed")

        except Exception as e:
            logger.error(f"Error during service integrity validation: {str(e)}")

    def _is_development_environment(self):
        """Check if we're running in development environment"""
        try:
            from django.conf import settings

            return settings.DEBUG
        except:
            return False

    def _setup_periodic_tasks(self):
        """Setup periodic tasks for the services app (if using Celery)"""
        try:
            # This would be called if Celery is configured
            # from .tasks import cleanup_expired_quotes, update_service_stats
            logger.debug("Periodic tasks setup completed")

        except ImportError:
        
            logger.debug("Celery not available, skipping periodic tasks setup")
        except Exception as e:
            logger.warning(f"Could not setup periodic tasks: {str(e)}")
