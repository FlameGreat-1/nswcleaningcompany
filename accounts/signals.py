from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.sessions.models import Session
from .models import User, ClientProfile, Address, UserSession, EmailVerification
from .utils import send_welcome_email, send_profile_completion_reminder, get_client_ip
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.is_client:
                ClientProfile.objects.create(user=instance)
                logger.info(f"Client profile created for user: {instance.email}")

            if not instance.is_verified and instance.is_active:
                verification = EmailVerification.objects.create_verification(instance)
                send_welcome_email(instance, verification.token)
                logger.info(f"Welcome email sent to user: {instance.email}")

        except Exception as e:
            logger.error(f"Error creating profile for user {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if not created and instance.is_client:
        try:
            profile, created = ClientProfile.objects.get_or_create(user=instance)
            if created:
                logger.info(
                    f"Client profile created for existing user: {instance.email}"
                )
        except Exception as e:
            logger.error(f"Error updating profile for user {instance.email}: {str(e)}")


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)

            if old_instance.is_active and not instance.is_active:
                UserSession.objects.deactivate_user_sessions(instance)
                logger.info(f"User sessions deactivated for user: {instance.email}")

            if not old_instance.is_verified and instance.is_verified:
                logger.info(f"User verified: {instance.email}")

        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error in user pre_save for {instance.email}: {str(e)}")


@receiver(post_save, sender=ClientProfile)
def client_profile_updated(sender, instance, created, **kwargs):
    try:
        if created:
            logger.info(f"Client profile created: {instance.user.email}")
        else:
            logger.info(f"Client profile updated: {instance.user.email}")

        if instance.user.is_ndis_client and not instance.ndis_number:
            send_profile_completion_reminder(instance.user, "ndis_number")

    except Exception as e:
        logger.error(
            f"Error in client_profile_updated for {instance.user.email}: {str(e)}"
        )


@receiver(post_save, sender=Address)
def address_updated(sender, instance, created, **kwargs):
    try:
        if instance.is_primary:
            Address.objects.filter(user=instance.user).exclude(pk=instance.pk).update(
                is_primary=False
            )

        if created:
            logger.info(f"Address created for user: {instance.user.email}")
        else:
            logger.info(f"Address updated for user: {instance.user.email}")

    except Exception as e:
        logger.error(f"Error in address_updated for {instance.user.email}: {str(e)}")


@receiver(pre_delete, sender=Address)
def address_pre_delete(sender, instance, **kwargs):
    try:
        if instance.is_primary:
            other_addresses = Address.objects.filter(user=instance.user).exclude(
                pk=instance.pk
            )

            if other_addresses.exists():
                other_addresses.first().update(is_primary=True)
                logger.info(
                    f"Primary address reassigned for user: {instance.user.email}"
                )

    except Exception as e:
        logger.error(f"Error in address_pre_delete for {instance.user.email}: {str(e)}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        session_key = request.session.session_key

        if session_key:
            UserSession.objects.create_session(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        logger.info(f"User logged in: {user.email} from {ip_address}")

    except Exception as e:
        logger.error(f"Error in user_logged_in_handler for {user.email}: {str(e)}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    try:
        if user and hasattr(request, "session"):
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.deactivate_session(session_key)

        if user:
            logger.info(f"User logged out: {user.email}")

    except Exception as e:
        if user:
            logger.error(f"Error in user_logged_out_handler for {user.email}: {str(e)}")


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    try:
        email = credentials.get("email", "Unknown")
        ip_address = get_client_ip(request)

        logger.warning(f"Failed login attempt for email: {email} from {ip_address}")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            failed_attempts = getattr(user, "failed_login_attempts", 0) + 1

            if failed_attempts >= 5:
                user.is_active = False
                user.save()
                logger.warning(
                    f"User account locked due to multiple failed attempts: {email}"
                )

                send_mail(
                    subject="Account Security Alert",
                    message=f"Your account has been temporarily locked due to multiple failed login attempts from {ip_address}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

    except Exception as e:
        logger.error(f"Error in user_login_failed_handler: {str(e)}")


@receiver(post_delete, sender=User)
def user_deleted_handler(sender, instance, **kwargs):
    try:
        UserSession.objects.filter(user=instance).delete()
        EmailVerification.objects.filter(user=instance).delete()

        logger.info(f"User deleted and related data cleaned up: {instance.email}")

    except Exception as e:
        logger.error(f"Error in user_deleted_handler for {instance.email}: {str(e)}")


@receiver(post_save, sender=EmailVerification)
def email_verification_created(sender, instance, created, **kwargs):
    if created:
        try:
            logger.info(
                f"Email verification token created for user: {instance.user.email}"
            )

        except Exception as e:
            logger.error(f"Error in email_verification_created: {str(e)}")


@receiver(post_save, sender=UserSession)
def user_session_created(sender, instance, created, **kwargs):
    if created:
        try:
            max_sessions = getattr(settings, "MAX_USER_SESSIONS", 5)
            user_sessions = UserSession.objects.filter(
                user=instance.user, is_active=True
            ).order_by("-created_at")

            if user_sessions.count() > max_sessions:
                old_sessions = user_sessions[max_sessions:]
                for session in old_sessions:
                    session.is_active = False
                    session.save()

                logger.info(f"Old sessions deactivated for user: {instance.user.email}")

        except Exception as e:
            logger.error(f"Error in user_session_created: {str(e)}")


def send_admin_notification(subject, message):
    try:
        admin_emails = [email for name, email in settings.ADMINS]

        if admin_emails:
            send_mail(
                subject=f"[Cleaning Service] {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )

    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")


@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    if created:
        try:
            subject = "New User Registration"
            message = f"""
            A new user has registered on the cleaning service platform:
            
            Email: {instance.email}
            Name: {instance.full_name}
            User Type: {instance.get_user_type_display()}
            Client Type: {instance.get_client_type_display() if instance.client_type else 'N/A'}
            Registration Date: {instance.date_joined}
            
            Please review the user account in the admin panel.
            """

            send_admin_notification(subject, message)

        except Exception as e:
            logger.error(
                f"Error sending admin notification for new user {instance.email}: {str(e)}"
            )


@receiver(post_save, sender=ClientProfile)
def notify_admin_ndis_client(sender, instance, created, **kwargs):
    if instance.user.is_ndis_client and instance.ndis_number:
        try:
            subject = "New NDIS Client Profile"
            message = f"""
            A new NDIS client profile has been completed:
            
            User: {instance.user.full_name} ({instance.user.email})
            NDIS Number: {instance.ndis_number}
            Plan Manager: {instance.plan_manager or 'Not specified'}
            Support Coordinator: {instance.support_coordinator or 'Not specified'}
            Accessibility Needs: {instance.get_accessibility_needs_display()}
            
            Please review the NDIS client profile in the admin panel.
            """

            send_admin_notification(subject, message)

        except Exception as e:
            logger.error(f"Error sending NDIS client notification: {str(e)}")


def cleanup_expired_data():
    try:
        email_count = EmailVerification.objects.cleanup_expired()
        session_count = UserSession.objects.cleanup_inactive_sessions()

        logger.info(
            f"Cleanup completed: {email_count} email verifications, {session_count} sessions"
        )

        if email_count > 0 or session_count > 0:
            send_admin_notification(
                "Data Cleanup Report",
                f"Automated cleanup completed:\n- Email verifications: {email_count}\n- User sessions: {session_count}",
            )

    except Exception as e:
        logger.error(f"Error in cleanup_expired_data: {str(e)}")


@receiver(post_save, sender=User)
def track_user_verification(sender, instance, created, **kwargs):
    if not created:
        try:
            if (
                instance.is_verified
                and hasattr(instance, "_state")
                and instance._state.adding is False
            ):
                old_instance = User.objects.get(pk=instance.pk)
                if not old_instance.is_verified:
                    logger.info(f"User email verified: {instance.email}")

                    send_mail(
                        subject="Email Verification Successful",
                        message=f"Welcome to our cleaning service platform! Your email has been successfully verified.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.email],
                        fail_silently=True,
                    )

        except User.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error in track_user_verification: {str(e)}")
