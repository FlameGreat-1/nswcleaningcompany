from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create superuser if it does not exist"

    def handle(self, *args, **options):
        User = get_user_model()
        email = "admin@nswcleaningcompany.com"

        self.stdout.write("🔍 Checking for existing superuser...")
        logger.info(f"Checking for superuser: {email}")

        if not User.objects.filter(email=email).exists():
            self.stdout.write("👤 Creating superuser...")
            User.objects.create_superuser(
                email=email,
                password="$$123abcChuks",
                first_name="Soft",
                last_name="Verse",
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Superuser {email} created successfully")
            )
            logger.info(f"Superuser created: {email}")
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Superuser {email} already exists"))
            logger.info(f"Superuser already exists: {email}")
