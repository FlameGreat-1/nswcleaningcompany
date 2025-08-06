from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)


class QuotesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "quotes"
    verbose_name = "Quote Management System"

    def ready(self):
        """
        Initialize the quotes app when Django starts
        """
        try:
            # Import signals to ensure they are connected
            from . import signals

            # Import and initialize signal manager
            from .signals import initialize_quote_signals

            initialize_quote_signals()

            # Connect post-migration signal for initial data setup
            post_migrate.connect(self.create_initial_data, sender=self)

            logger.info("Quotes app initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize quotes app: {str(e)}")

    def create_initial_data(self, sender, **kwargs):
        """
        Create initial data after migrations
        """
        try:
            self.create_default_quote_templates()
            self.setup_default_permissions()
            logger.info("Initial quote data created successfully")

        except Exception as e:
            logger.error(f"Failed to create initial quote data: {str(e)}")

    def create_default_quote_templates(self):
        """
        Create default quote templates
        """
        from .models import QuoteTemplate
        from services.models import Service
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Get first active service or create a default one
        try:
            default_service = Service.objects.filter(is_active=True).first()
            if not default_service:
                return

            # Get first staff user for template creation
            staff_user = User.objects.filter(is_staff=True, is_active=True).first()
            if not staff_user:
                return

            # Default templates to create
            templates = [
                {
                    "name": "Standard General Cleaning",
                    "description": "Standard template for general cleaning services",
                    "cleaning_type": "general",
                    "default_urgency_level": 2,
                    "is_ndis_template": False,
                },
                {
                    "name": "Deep Cleaning Service",
                    "description": "Template for deep cleaning services",
                    "cleaning_type": "deep",
                    "default_urgency_level": 2,
                    "is_ndis_template": False,
                },
                {
                    "name": "End of Lease Cleaning",
                    "description": "Template for end of lease cleaning",
                    "cleaning_type": "end_of_lease",
                    "default_urgency_level": 3,
                    "is_ndis_template": False,
                },
                {
                    "name": "NDIS General Cleaning",
                    "description": "Template for NDIS general cleaning services",
                    "cleaning_type": "general",
                    "default_urgency_level": 2,
                    "is_ndis_template": True,
                },
                {
                    "name": "NDIS Deep Cleaning",
                    "description": "Template for NDIS deep cleaning services",
                    "cleaning_type": "deep",
                    "default_urgency_level": 2,
                    "is_ndis_template": True,
                },
            ]

            for template_data in templates:
                template, created = QuoteTemplate.objects.get_or_create(
                    name=template_data["name"],
                    defaults={
                        "description": template_data["description"],
                        "cleaning_type": template_data["cleaning_type"],
                        "default_service": default_service,
                        "default_urgency_level": template_data["default_urgency_level"],
                        "is_active": True,
                        "is_ndis_template": template_data["is_ndis_template"],
                        "created_by": staff_user,
                    },
                )

                if created:
                    logger.info(f"Created quote template: {template.name}")

        except Exception as e:
            logger.error(f"Failed to create default quote templates: {str(e)}")

    def setup_default_permissions(self):
        """
        Setup default permissions for quote management
        """
        try:
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from .models import (
                Quote,
                QuoteItem,
                QuoteAttachment,
                QuoteRevision,
                QuoteTemplate,
            )

            # Create Quote Manager group if it doesn't exist
            quote_manager_group, created = Group.objects.get_or_create(
                name="Quote Managers"
            )

            if created:
                # Get content types for quote models
                quote_ct = ContentType.objects.get_for_model(Quote)
                quote_item_ct = ContentType.objects.get_for_model(QuoteItem)
                quote_attachment_ct = ContentType.objects.get_for_model(QuoteAttachment)
                quote_revision_ct = ContentType.objects.get_for_model(QuoteRevision)
                quote_template_ct = ContentType.objects.get_for_model(QuoteTemplate)

                # Define permissions for Quote Managers
                permissions_to_add = [
                    # Quote permissions
                    Permission.objects.get(content_type=quote_ct, codename="add_quote"),
                    Permission.objects.get(
                        content_type=quote_ct, codename="change_quote"
                    ),
                    Permission.objects.get(
                        content_type=quote_ct, codename="delete_quote"
                    ),
                    Permission.objects.get(
                        content_type=quote_ct, codename="view_quote"
                    ),
                    # QuoteItem permissions
                    Permission.objects.get(
                        content_type=quote_item_ct, codename="add_quoteitem"
                    ),
                    Permission.objects.get(
                        content_type=quote_item_ct, codename="change_quoteitem"
                    ),
                    Permission.objects.get(
                        content_type=quote_item_ct, codename="delete_quoteitem"
                    ),
                    Permission.objects.get(
                        content_type=quote_item_ct, codename="view_quoteitem"
                    ),
                    # QuoteAttachment permissions
                    Permission.objects.get(
                        content_type=quote_attachment_ct, codename="add_quoteattachment"
                    ),
                    Permission.objects.get(
                        content_type=quote_attachment_ct,
                        codename="change_quoteattachment",
                    ),
                    Permission.objects.get(
                        content_type=quote_attachment_ct,
                        codename="delete_quoteattachment",
                    ),
                    Permission.objects.get(
                        content_type=quote_attachment_ct,
                        codename="view_quoteattachment",
                    ),
                    # QuoteRevision permissions
                    Permission.objects.get(
                        content_type=quote_revision_ct, codename="add_quoterevision"
                    ),
                    Permission.objects.get(
                        content_type=quote_revision_ct, codename="change_quoterevision"
                    ),
                    Permission.objects.get(
                        content_type=quote_revision_ct, codename="delete_quoterevision"
                    ),
                    Permission.objects.get(
                        content_type=quote_revision_ct, codename="view_quoterevision"
                    ),
                    # QuoteTemplate permissions
                    Permission.objects.get(
                        content_type=quote_template_ct, codename="add_quotetemplate"
                    ),
                    Permission.objects.get(
                        content_type=quote_template_ct, codename="change_quotetemplate"
                    ),
                    Permission.objects.get(
                        content_type=quote_template_ct, codename="delete_quotetemplate"
                    ),
                    Permission.objects.get(
                        content_type=quote_template_ct, codename="view_quotetemplate"
                    ),
                ]

                quote_manager_group.permissions.set(permissions_to_add)
                logger.info("Created Quote Managers group with permissions")

            # Create Quote Viewers group for limited access
            quote_viewer_group, created = Group.objects.get_or_create(
                name="Quote Viewers"
            )

            if created:
                view_permissions = [
                    Permission.objects.get(
                        content_type=quote_ct, codename="view_quote"
                    ),
                    Permission.objects.get(
                        content_type=quote_item_ct, codename="view_quoteitem"
                    ),
                    Permission.objects.get(
                        content_type=quote_attachment_ct,
                        codename="view_quoteattachment",
                    ),
                    Permission.objects.get(
                        content_type=quote_revision_ct, codename="view_quoterevision"
                    ),
                    Permission.objects.get(
                        content_type=quote_template_ct, codename="view_quotetemplate"
                    ),
                ]

                quote_viewer_group.permissions.set(view_permissions)
                logger.info("Created Quote Viewers group with permissions")

        except Exception as e:
            logger.error(f"Failed to setup default permissions: {str(e)}")
