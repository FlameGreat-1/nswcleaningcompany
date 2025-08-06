from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management.color import no_style
from django.db import connection


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "User Accounts Management"

    def ready(self):
        import accounts.signals

        self.setup_custom_user_model()
        self.register_periodic_tasks()
        self.setup_logging()

    def setup_custom_user_model(self):
        from django.conf import settings

        if not hasattr(settings, "AUTH_USER_MODEL"):
            settings.AUTH_USER_MODEL = "accounts.User"

    def register_periodic_tasks(self):
        try:
            from django_celery_beat.models import PeriodicTask, CrontabSchedule
            import json

            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=0,
                hour=2,
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
            )

            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                name="Cleanup Expired Tokens",
                task="accounts.tasks.cleanup_expired_tokens",
                defaults={"enabled": True},
            )

            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                name="Send Profile Completion Reminders",
                task="accounts.tasks.send_profile_completion_reminders",
                defaults={"enabled": True},
            )

        except ImportError:
            pass
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not register periodic tasks: {str(e)}")

    def setup_logging(self):
        import logging

        logger = logging.getLogger("accounts")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    def create_default_groups(self, sender, **kwargs):
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from .models import User, ClientProfile, Address

        try:
            admin_group, created = Group.objects.get_or_create(name="Administrators")
            if created:
                admin_permissions = Permission.objects.all()
                admin_group.permissions.set(admin_permissions)

            staff_group, created = Group.objects.get_or_create(name="Staff")
            if created:
                staff_permissions = Permission.objects.filter(
                    content_type__in=ContentType.objects.filter(app_label="accounts")
                ).exclude(codename__in=["delete_user", "delete_clientprofile"])
                staff_group.permissions.set(staff_permissions)

            client_group, created = Group.objects.get_or_create(name="Clients")
            if created:
                client_permissions = Permission.objects.filter(
                    content_type__in=ContentType.objects.filter(
                        app_label="accounts", model__in=["clientprofile", "address"]
                    ),
                    codename__in=[
                        "view_clientprofile",
                        "change_clientprofile",
                        "add_address",
                        "view_address",
                        "change_address",
                        "delete_address",
                    ],
                )
                client_group.permissions.set(client_permissions)

            ndis_group, created = Group.objects.get_or_create(name="NDIS Clients")
            if created:
                ndis_permissions = Permission.objects.filter(
                    content_type__in=ContentType.objects.filter(app_label="accounts"),
                    codename__in=[
                        "view_clientprofile",
                        "change_clientprofile",
                        "add_address",
                        "view_address",
                        "change_address",
                        "delete_address",
                    ],
                )
                ndis_group.permissions.set(ndis_permissions)

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error creating default groups: {str(e)}")

    def create_default_admin_user(self, sender, **kwargs):
        from .models import User
        from django.conf import settings

        try:
            if not User.objects.filter(is_superuser=True).exists():
                admin_email = getattr(
                    settings, "DEFAULT_ADMIN_EMAIL", "admin@cleaningservice.com"
                )
                admin_password = getattr(settings, "DEFAULT_ADMIN_PASSWORD", "admin123")

                User.objects.create_superuser(
                    email=admin_email,
                    password=admin_password,
                    first_name="System",
                    last_name="Administrator",
                )

                import logging

                logger = logging.getLogger(__name__)
                logger.info(f"Default admin user created: {admin_email}")

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error creating default admin user: {str(e)}")

    def setup_database_indexes(self, sender, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_user_email_active 
                    ON auth_user (email, is_active);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_user_type_client_type 
                    ON auth_user (user_type, client_type);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_user_verified_active 
                    ON auth_user (is_verified, is_active);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_client_profile_ndis 
                    ON client_profiles (ndis_number);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_address_user_primary 
                    ON addresses (user_id, is_primary);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_address_suburb_postcode 
                    ON addresses (suburb, postcode);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_user_session_active 
                    ON user_sessions (user_id, is_active);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_email_verification_token 
                    ON email_verifications (token, is_used);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_password_reset_token 
                    ON password_resets (token, is_used);
                """
                )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create database indexes: {str(e)}")

    def setup_cache_keys(self):
        from django.core.cache import cache

        cache_keys = {
            "user_stats": "accounts:user_stats",
            "active_users_count": "accounts:active_users_count",
            "ndis_clients_count": "accounts:ndis_clients_count",
            "recent_registrations": "accounts:recent_registrations",
            "failed_login_attempts": "accounts:failed_login_attempts:{user_id}",
            "rate_limit": "accounts:rate_limit:{user_id}:{action}",
            "user_sessions": "accounts:user_sessions:{user_id}",
            "email_verification": "accounts:email_verification:{token}",
            "password_reset": "accounts:password_reset:{token}",
        }

        for key, pattern in cache_keys.items():
            cache.set(f"cache_patterns:{key}", pattern, timeout=None)

    def register_custom_checks(self):
        from django.core.checks import register, Error, Warning

        @register()
        def check_auth_user_model(app_configs, **kwargs):
            from django.conf import settings

            errors = []

            if not hasattr(settings, "AUTH_USER_MODEL"):
                errors.append(
                    Error(
                        "AUTH_USER_MODEL setting is not defined",
                        hint='Add AUTH_USER_MODEL = "accounts.User" to your settings',
                        id="accounts.E001",
                    )
                )
            elif settings.AUTH_USER_MODEL != "accounts.User":
                errors.append(
                    Warning(
                        "AUTH_USER_MODEL is not set to accounts.User",
                        hint='Consider using AUTH_USER_MODEL = "accounts.User"',
                        id="accounts.W001",
                    )
                )

            return errors

        @register()
        def check_email_settings(app_configs, **kwargs):
            from django.conf import settings

            errors = []

            required_email_settings = [
                "EMAIL_HOST",
                "EMAIL_PORT",
                "EMAIL_HOST_USER",
                "EMAIL_HOST_PASSWORD",
                "DEFAULT_FROM_EMAIL",
            ]

            for setting in required_email_settings:
                if not hasattr(settings, setting) or not getattr(settings, setting):
                    errors.append(
                        Warning(
                            f"{setting} is not configured",
                            hint=f"Configure {setting} in your settings for email functionality",
                            id=f"accounts.W{setting.lower()}",
                        )
                    )

            return errors

        @register()
        def check_security_settings(app_configs, **kwargs):
            from django.conf import settings

            errors = []

            if not getattr(settings, "USE_TLS", False) and not getattr(
                settings, "USE_SSL", False
            ):
                errors.append(
                    Warning(
                        "Email security not configured",
                        hint="Set EMAIL_USE_TLS=True or EMAIL_USE_SSL=True for secure email",
                        id="accounts.W002",
                    )
                )

            if not hasattr(settings, "SECRET_KEY") or len(settings.SECRET_KEY) < 50:
                errors.append(
                    Error(
                        "SECRET_KEY is too short or not set",
                        hint="Use a strong SECRET_KEY with at least 50 characters",
                        id="accounts.E002",
                    )
                )

            return errors

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        post_migrate.connect(self.create_default_groups, sender=self)
        post_migrate.connect(self.create_default_admin_user, sender=self)
        post_migrate.connect(self.setup_database_indexes, sender=self)
        self.register_custom_checks()
