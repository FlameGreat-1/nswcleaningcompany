from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class QuotesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quotes"
    verbose_name = "Quote Management System"

    def ready(self):
        try:
            from . import signals

            logger.info("Quotes app initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize quotes app: {str(e)}")
