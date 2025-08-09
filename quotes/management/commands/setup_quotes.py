from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import connection
from quotes.models import (
    Quote,
    QuoteItem,
    QuoteAttachment,
    QuoteRevision,
    QuoteTemplate,
)
from services.models import Service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Setup initial quote data and permissions"

    def handle(self, *args, **options):
        try:
            self.setup_templates()
            self.setup_permissions()
            self.stdout.write(self.style.SUCCESS("Successfully setup quote data"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to setup quote data: {e}"))

    def setup_templates(self):
        User = get_user_model()

        try:
            default_service = Service.objects.filter(is_active=True).first()
            if not default_service:
                self.stdout.write(
                    self.style.WARNING(
                        "No active service found, skipping template creation"
                    )
                )
                return

            staff_user = User.objects.filter(is_staff=True, is_active=True).first()
            if not staff_user:
                self.stdout.write(
                    self.style.WARNING(
                        "No staff user found, skipping template creation"
                    )
                )
                return

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
                    self.stdout.write(f"Created quote template: {template.name}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create templates: {e}"))

    def setup_permissions(self):
        try:
            table_names = connection.introspection.table_names()
            required_tables = ["quotes_quote", "django_content_type", "auth_permission"]

            if not all(table in table_names for table in required_tables):
                self.stdout.write(
                    self.style.WARNING(
                        "Required tables not ready, skipping permission setup"
                    )
                )
                return

            quote_manager_group, created = Group.objects.get_or_create(
                name="Quote Managers"
            )

            if created:
                quote_ct = ContentType.objects.get_for_model(Quote)
                quote_item_ct = ContentType.objects.get_for_model(QuoteItem)
                quote_attachment_ct = ContentType.objects.get_for_model(QuoteAttachment)
                quote_revision_ct = ContentType.objects.get_for_model(QuoteRevision)
                quote_template_ct = ContentType.objects.get_for_model(QuoteTemplate)

                permissions_to_add = [
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
                self.stdout.write("Created Quote Managers group with permissions")

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
                self.stdout.write("Created Quote Viewers group with permissions")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to setup permissions: {e}"))
