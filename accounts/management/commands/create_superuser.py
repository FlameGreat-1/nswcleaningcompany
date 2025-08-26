from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create superuser, fix site domain, and clear problematic sessions"

    def handle(self, *args, **options):
        # Part 1: Create superuser if needed
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

        # Part 2: Fix site domain
        self.stdout.write("🔍 Checking site configuration...")
        sites = Site.objects.all()

        if sites.exists():
            site = sites.first()
            old_domain = site.domain
            site.domain = "www.nswcleaningcompany.com"
            site.name = "NSW Cleaning Company"
            site.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Updated site domain from {old_domain} to {site.domain}"
                )
            )
            logger.info(f"Updated site domain from {old_domain} to {site.domain}")
        else:
            site = Site.objects.create(
                id=1, domain="www.nswcleaningcompany.com", name="NSW Cleaning Company"
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Created new site: {site.domain}"))
            logger.info(f"Created new site: {site.domain}")

        # Part 3: Fix session issue
        self.stdout.write("🔍 Checking for problematic user sessions...")
        try:
            # Import the UserSession model
            from accounts.models import UserSession

            # Clear the problematic session
            problematic_key = "2a2i7p7205qjnads5hkdzkd3gf6kgdhu"
            deleted_count = UserSession.objects.filter(
                session_key=problematic_key
            ).delete()[0]

            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Deleted {deleted_count} problematic session(s)"
                    )
                )
                logger.info(f"Deleted {deleted_count} problematic session(s)")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️ No problematic sessions found with key: {problematic_key}"
                    )
                )
                logger.info(
                    f"No problematic sessions found with key: {problematic_key}"
                )

        except ImportError:
            self.stdout.write(self.style.ERROR("❌ Could not import UserSession model"))
            logger.error("Could not import UserSession model")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error clearing sessions: {str(e)}"))
            logger.error(f"Error clearing sessions: {str(e)}")
