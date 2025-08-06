from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.signals import user_logged_in
import logging

from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from .utils import (
    send_quote_notification,
    calculate_quote_pricing,
    sync_quote_with_external_systems,
    generate_quote_number,
)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Quote)
def quote_pre_save(sender, instance, **kwargs):
    if not instance.quote_number:
        instance.quote_number = generate_quote_number()

    if instance.pk:
        try:
            old_instance = Quote.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_final_price = old_instance.final_price
        except Quote.DoesNotExist:
            instance._old_status = None
            instance._old_final_price = None
    else:
        instance._old_status = None
        instance._old_final_price = None


@receiver(post_save, sender=Quote)
def quote_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New quote created: {instance.quote_number}")

        if instance.status == "submitted":
            send_quote_notification(instance, "submitted", "staff")

        cache.delete("quote_statistics")
        cache.delete(f"user_quotes_{instance.client.id}")

    else:
        old_status = getattr(instance, "_old_status", None)
        old_price = getattr(instance, "_old_final_price", None)

        if old_status and old_status != instance.status:
            handle_quote_status_change(instance, old_status, instance.status)

        if old_price and old_price != instance.final_price:
            handle_quote_price_change(instance, old_price, instance.final_price)

        cache.delete("quote_statistics")
        cache.delete(f"quote_detail_{instance.id}")


@receiver(post_delete, sender=Quote)
def quote_post_delete(sender, instance, **kwargs):
    logger.info(f"Quote deleted: {instance.quote_number}")

    cache.delete("quote_statistics")
    cache.delete(f"user_quotes_{instance.client.id}")
    cache.delete(f"quote_detail_{instance.id}")


@receiver(post_save, sender=QuoteItem)
def quote_item_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Quote item added to {instance.quote.quote_number}: {instance.name}"
        )

    instance.quote.update_pricing()

    cache.delete(f"quote_detail_{instance.quote.id}")
    cache.delete(f"quote_items_{instance.quote.id}")


@receiver(post_delete, sender=QuoteItem)
def quote_item_post_delete(sender, instance, **kwargs):
    logger.info(
        f"Quote item removed from {instance.quote.quote_number}: {instance.name}"
    )

    instance.quote.update_pricing()

    cache.delete(f"quote_detail_{instance.quote.id}")
    cache.delete(f"quote_items_{instance.quote.id}")


@receiver(post_save, sender=QuoteAttachment)
def quote_attachment_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Attachment added to quote {instance.quote.quote_number}: {instance.original_filename}"
        )

        if instance.quote.status in ["submitted", "under_review"]:
            send_quote_notification(instance.quote, "attachment_added", "staff")

    cache.delete(f"quote_detail_{instance.quote.id}")
    cache.delete(f"quote_attachments_{instance.quote.id}")


@receiver(post_delete, sender=QuoteAttachment)
def quote_attachment_post_delete(sender, instance, **kwargs):
    logger.info(
        f"Attachment removed from quote {instance.quote.quote_number}: {instance.original_filename}"
    )

    cache.delete(f"quote_detail_{instance.quote.id}")
    cache.delete(f"quote_attachments_{instance.quote.id}")


@receiver(post_save, sender=QuoteRevision)
def quote_revision_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"Quote revision created for {instance.quote.quote_number}: Rev {instance.revision_number}"
        )

        send_quote_notification(instance.quote, "revised", "client")

    cache.delete(f"quote_detail_{instance.quote.id}")
    cache.delete(f"quote_revisions_{instance.quote.id}")


@receiver(post_save, sender=QuoteTemplate)
def quote_template_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Quote template created: {instance.name}")

    cache.delete("quote_templates")
    cache.delete("active_quote_templates")


def handle_quote_status_change(instance, old_status, new_status):
    logger.info(
        f"Quote {instance.quote_number} status changed: {old_status} -> {new_status}"
    )

    status_notifications = {
        "submitted": ("submitted", "staff"),
        "under_review": ("under_review", "client"),
        "approved": ("approved", "client"),
        "rejected": ("rejected", "client"),
        "expired": ("expired", "both"),
        "converted": ("converted", "both"),
        "cancelled": ("cancelled", "both"),
    }

    if new_status in status_notifications:
        notification_type, recipient_type = status_notifications[new_status]
        send_quote_notification(instance, notification_type, recipient_type)

    if new_status == "approved":
        instance.approved_at = timezone.now()
        if not instance.expires_at:
            instance.expires_at = timezone.now() + timezone.timedelta(days=30)
        instance.save(update_fields=["approved_at", "expires_at"])

    elif new_status == "converted":
        sync_quote_with_external_systems(instance)

    elif new_status in ["rejected", "cancelled", "expired"]:
        instance.expires_at = None
        instance.save(update_fields=["expires_at"])


def handle_quote_price_change(instance, old_price, new_price):
    logger.info(
        f"Quote {instance.quote_number} price changed: ${old_price} -> ${new_price}"
    )

    price_difference = new_price - old_price
    percentage_change = (price_difference / old_price) * 100 if old_price > 0 else 0

    if abs(percentage_change) >= 10:
        QuoteRevision.objects.create(
            quote=instance,
            previous_price=old_price,
            new_price=new_price,
            changes_summary=f"Price changed by {percentage_change:.1f}%",
            reason="Automatic revision due to significant price change",
        )


@receiver(user_logged_in)
def user_logged_in_quote_handler(sender, request, user, **kwargs):
    if hasattr(user, "quotes"):
        pending_quotes = user.quotes.filter(
            status__in=["submitted", "under_review"]
        ).count()

        if pending_quotes > 0:
            request.session["pending_quotes_count"] = pending_quotes
            logger.info(f"User {user.email} has {pending_quotes} pending quotes")


def clear_quote_caches(quote_id=None, user_id=None):
    cache_keys = ["quote_statistics", "active_quote_templates", "quote_dashboard_data"]

    if quote_id:
        cache_keys.extend(
            [
                f"quote_detail_{quote_id}",
                f"quote_items_{quote_id}",
                f"quote_attachments_{quote_id}",
                f"quote_revisions_{quote_id}",
            ]
        )

    if user_id:
        cache_keys.extend([f"user_quotes_{user_id}", f"user_quote_stats_{user_id}"])

    for key in cache_keys:
        cache.delete(key)


def update_quote_metrics(quote):
    try:
        from django.core.cache import cache

        cache_key = "quote_metrics"
        metrics = cache.get(cache_key, {})

        metrics["last_updated"] = timezone.now().isoformat()
        metrics["total_quotes"] = Quote.objects.count()
        metrics["pending_quotes"] = Quote.objects.filter(
            status__in=["submitted", "under_review"]
        ).count()
        metrics["approved_quotes"] = Quote.objects.filter(status="approved").count()
        metrics["converted_quotes"] = Quote.objects.filter(status="converted").count()

        cache.set(cache_key, metrics, 3600)

    except Exception as e:
        logger.error(f"Failed to update quote metrics: {str(e)}")


def validate_quote_business_rules(instance):
    errors = []

    if instance.status == "approved" and not instance.expires_at:
        errors.append("Approved quotes must have an expiry date")

    if instance.status == "rejected" and not instance.rejection_reason:
        errors.append("Rejected quotes must have a rejection reason")

    if instance.final_price < 0:
        errors.append("Quote price cannot be negative")

    if instance.is_ndis_client and not instance.ndis_participant_number:
        errors.append("NDIS clients must have a participant number")

    if instance.urgency_level >= 4 and not instance.assigned_to:
        errors.append("High urgency quotes should be assigned to staff")

    return errors


@receiver(pre_save, sender=Quote)
def validate_quote_before_save(sender, instance, **kwargs):
    validation_errors = validate_quote_business_rules(instance)

    if validation_errors:
        logger.warning(
            f"Quote {instance.quote_number} validation warnings: {validation_errors}"
        )


@receiver(post_save, sender=Quote)
def update_quote_search_index(sender, instance, created, **kwargs):
    try:
        search_data = {
            "quote_number": instance.quote_number,
            "client_name": instance.client.get_full_name(),
            "client_email": instance.client.email,
            "service_name": instance.service.name,
            "cleaning_type": instance.cleaning_type,
            "property_address": instance.property_address,
            "suburb": instance.suburb,
            "postcode": instance.postcode,
            "status": instance.status,
        }

        cache.set(f"quote_search_{instance.id}", search_data, 86400)

    except Exception as e:
        logger.error(
            f"Failed to update search index for quote {instance.quote_number}: {str(e)}"
        )


@receiver(post_save, sender=Quote)
def trigger_quote_workflows(sender, instance, created, **kwargs):
    if created:
        if instance.urgency_level >= 4:
            assign_urgent_quote(instance)

        if instance.final_price >= 1000:
            flag_high_value_quote(instance)

        if instance.is_ndis_client:
            validate_ndis_requirements(instance)

    else:
        old_status = getattr(instance, "_old_status", None)
        if old_status and old_status != instance.status:
            trigger_status_workflow(instance, old_status, instance.status)


def assign_urgent_quote(quote):
    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        available_staff = (
            User.objects.filter(is_staff=True, is_active=True).order_by("?").first()
        )

        if available_staff:
            quote.assigned_to = available_staff
            quote.save(update_fields=["assigned_to"])

            logger.info(
                f"Urgent quote {quote.quote_number} auto-assigned to {available_staff.email}"
            )

    except Exception as e:
        logger.error(
            f"Failed to auto-assign urgent quote {quote.quote_number}: {str(e)}"
        )


def flag_high_value_quote(quote):
    try:
        logger.info(
            f"High value quote flagged: {quote.quote_number} - ${quote.final_price}"
        )

        send_quote_notification(quote, "high_value_alert", "staff")

    except Exception as e:
        logger.error(f"Failed to flag high value quote {quote.quote_number}: {str(e)}")


def validate_ndis_requirements(quote):
    try:
        if not quote.ndis_participant_number:
            logger.warning(
                f"NDIS quote {quote.quote_number} missing participant number"
            )

        if not quote.plan_manager_name and not quote.support_coordinator_name:
            logger.warning(
                f"NDIS quote {quote.quote_number} missing plan manager or support coordinator"
            )

    except Exception as e:
        logger.error(
            f"Failed to validate NDIS requirements for quote {quote.quote_number}: {str(e)}"
        )


def trigger_status_workflow(quote, old_status, new_status):
    workflow_map = {
        ("draft", "submitted"): handle_quote_submission,
        ("submitted", "under_review"): handle_quote_review_start,
        ("under_review", "approved"): handle_quote_approval,
        ("under_review", "rejected"): handle_quote_rejection,
        ("approved", "converted"): handle_quote_conversion,
        ("approved", "expired"): handle_quote_expiry,
    }

    workflow_key = (old_status, new_status)
    if workflow_key in workflow_map:
        try:
            workflow_map[workflow_key](quote)
        except Exception as e:
            logger.error(
                f"Workflow failed for quote {quote.quote_number} ({old_status} -> {new_status}): {str(e)}"
            )


def handle_quote_submission(quote):
    logger.info(f"Processing quote submission: {quote.quote_number}")
    quote.submitted_at = timezone.now()
    quote.save(update_fields=["submitted_at"])


def handle_quote_review_start(quote):
    logger.info(f"Starting quote review: {quote.quote_number}")
    quote.reviewed_at = timezone.now()
    quote.save(update_fields=["reviewed_at"])


def handle_quote_approval(quote):
    logger.info(f"Processing quote approval: {quote.quote_number}")

    if not quote.expires_at:
        quote.expires_at = timezone.now() + timezone.timedelta(days=30)
        quote.save(update_fields=["expires_at"])


def handle_quote_rejection(quote):
    logger.info(f"Processing quote rejection: {quote.quote_number}")

    if quote.expires_at:
        quote.expires_at = None
        quote.save(update_fields=["expires_at"])


def handle_quote_conversion(quote):
    logger.info(f"Processing quote conversion: {quote.quote_number}")

    try:
        sync_quote_with_external_systems(quote)
    except Exception as e:
        logger.error(f"Failed to sync converted quote {quote.quote_number}: {str(e)}")


def handle_quote_expiry(quote):
    logger.info(f"Processing quote expiry: {quote.quote_number}")

    send_quote_notification(quote, "expired", "both")


@receiver(post_save, sender=Quote)
def log_quote_activity(sender, instance, created, **kwargs):
    if created:
        activity_type = "created"
        details = f"Quote {instance.quote_number} created for {instance.client.get_full_name()}"
    else:
        old_status = getattr(instance, "_old_status", None)
        if old_status and old_status != instance.status:
            activity_type = "status_changed"
            details = f"Quote {instance.quote_number} status changed from {old_status} to {instance.status}"
        else:
            activity_type = "updated"
            details = f"Quote {instance.quote_number} updated"

    try:
        from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
        from django.contrib.contenttypes.models import ContentType

        LogEntry.objects.create(
            user_id=getattr(instance, "_current_user_id", None),
            content_type=ContentType.objects.get_for_model(Quote),
            object_id=instance.pk,
            object_repr=str(instance),
            action_flag=ADDITION if created else CHANGE,
            change_message=details,
        )

    except Exception as e:
        logger.error(f"Failed to log quote activity: {str(e)}")


@receiver(pre_delete, sender=Quote)
def quote_pre_delete(sender, instance, **kwargs):
    logger.info(f"Preparing to delete quote: {instance.quote_number}")

    if instance.status in ["approved", "converted"]:
        logger.warning(
            f"Attempting to delete quote {instance.quote_number} with status {instance.status}"
        )

    instance._items_count = instance.items.count()
    instance._attachments_count = instance.attachments.count()
    instance._revisions_count = instance.revisions.count()


@receiver(post_delete, sender=Quote)
def cleanup_quote_related_data(sender, instance, **kwargs):
    logger.info(
        f"Quote deleted: {instance.quote_number} "
        f"(Items: {getattr(instance, '_items_count', 0)}, "
        f"Attachments: {getattr(instance, '_attachments_count', 0)}, "
        f"Revisions: {getattr(instance, '_revisions_count', 0)})"
    )

    clear_quote_caches(quote_id=instance.id, user_id=instance.client.id)

    try:
        cache.delete(f"quote_pdf_{instance.id}")
        cache.delete(f"quote_analytics_{instance.id}")
    except Exception as e:
        logger.error(f"Failed to clear quote caches: {str(e)}")


@receiver(pre_save, sender=QuoteItem)
def quote_item_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = QuoteItem.objects.get(pk=instance.pk)
            instance._old_total_price = old_instance.total_price
        except QuoteItem.DoesNotExist:
            instance._old_total_price = None
    else:
        instance._old_total_price = None


@receiver(post_save, sender=QuoteItem)
def quote_item_price_change_handler(sender, instance, created, **kwargs):
    if not created:
        old_price = getattr(instance, "_old_total_price", None)
        if old_price and old_price != instance.total_price:
            logger.info(
                f"Quote item price changed in {instance.quote.quote_number}: "
                f"{instance.name} ${old_price} -> ${instance.total_price}"
            )


@receiver(pre_delete, sender=QuoteItem)
def quote_item_pre_delete(sender, instance, **kwargs):
    logger.info(
        f"Preparing to delete quote item: {instance.name} from {instance.quote.quote_number}"
    )


@receiver(pre_delete, sender=QuoteAttachment)
def quote_attachment_pre_delete(sender, instance, **kwargs):
    logger.info(
        f"Preparing to delete attachment: {instance.original_filename} from {instance.quote.quote_number}"
    )

    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception as e:
            logger.error(f"Failed to delete attachment file: {str(e)}")


@receiver(post_save, sender=QuoteTemplate)
def quote_template_usage_handler(sender, instance, created, **kwargs):
    if not created:
        cache.delete("quote_templates")
        cache.delete("active_quote_templates")
        cache.delete(f"quote_template_{instance.id}")


@receiver(pre_delete, sender=QuoteTemplate)
def quote_template_pre_delete(sender, instance, **kwargs):
    if instance.usage_count > 0:
        logger.warning(
            f"Deleting quote template {instance.name} with {instance.usage_count} uses"
        )


def connect_quote_signals():
    logger.info("Quote signals connected successfully")


def disconnect_quote_signals():
    signals_to_disconnect = [
        (pre_save, quote_pre_save, Quote),
        (post_save, quote_post_save, Quote),
        (post_delete, quote_post_delete, Quote),
        (post_save, quote_item_post_save, QuoteItem),
        (post_delete, quote_item_post_delete, QuoteItem),
        (post_save, quote_attachment_post_save, QuoteAttachment),
        (post_delete, quote_attachment_post_delete, QuoteAttachment),
        (post_save, quote_revision_post_save, QuoteRevision),
        (post_save, quote_template_post_save, QuoteTemplate),
    ]

    for signal, handler, sender in signals_to_disconnect:
        signal.disconnect(handler, sender=sender)

    logger.info("Quote signals disconnected")


class QuoteSignalManager:
    @staticmethod
    def enable_signals():
        connect_quote_signals()

    @staticmethod
    def disable_signals():
        disconnect_quote_signals()

    @staticmethod
    def clear_all_caches():
        cache_patterns = [
            "quote_*",
            "user_quotes_*",
            "quote_statistics",
            "quote_templates",
            "active_quote_templates",
        ]

        for pattern in cache_patterns:
            try:
                cache.delete_pattern(pattern)
            except AttributeError:
                pass

    @staticmethod
    def get_signal_status():
        return {
            "quote_signals_active": True,
            "cache_backend": cache.__class__.__name__,
            "last_activity": timezone.now().isoformat(),
        }


def handle_quote_bulk_update(quote_ids, update_data, user):
    try:
        quotes = Quote.objects.filter(id__in=quote_ids)
        updated_count = 0

        for quote in quotes:
            old_status = quote.status

            for field, value in update_data.items():
                if hasattr(quote, field):
                    setattr(quote, field, value)

            quote.save()

            if "status" in update_data and old_status != quote.status:
                handle_quote_status_change(quote, old_status, quote.status)

            updated_count += 1

        logger.info(f"Bulk updated {updated_count} quotes by user {user.email}")

        clear_quote_caches()

        return updated_count

    except Exception as e:
        logger.error(f"Bulk quote update failed: {str(e)}")
        raise


def schedule_quote_maintenance_tasks():
    from django.utils import timezone
    from datetime import timedelta

    try:
        now = timezone.now()

        expired_quotes = Quote.objects.filter(status="approved", expires_at__lt=now)

        expired_count = expired_quotes.update(status="expired")

        if expired_count > 0:
            logger.info(f"Automatically expired {expired_count} quotes")

            for quote in expired_quotes:
                send_quote_notification(quote, "expired", "both")

        expiring_soon = Quote.objects.filter(
            status="approved",
            expires_at__lte=now + timedelta(days=3),
            expires_at__gt=now,
        )

        for quote in expiring_soon:
            send_quote_notification(quote, "expiry_reminder", "client")

        logger.info(f"Sent expiry reminders for {expiring_soon.count()} quotes")

        clear_quote_caches()

    except Exception as e:
        logger.error(f"Quote maintenance tasks failed: {str(e)}")


def initialize_quote_signals():
    logger.info("Initializing quote signal handlers...")

    try:
        connect_quote_signals()

        signal_handlers = [
            "quote_pre_save",
            "quote_post_save",
            "quote_post_delete",
            "quote_item_post_save",
            "quote_item_post_delete",
            "quote_attachment_post_save",
            "quote_attachment_post_delete",
            "quote_revision_post_save",
            "quote_template_post_save",
        ]

        logger.info(f"Quote signal handlers initialized: {', '.join(signal_handlers)}")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize quote signals: {str(e)}")
        return False


quote_signal_manager = QuoteSignalManager()

if initialize_quote_signals():
    logger.info("Quote signals system ready")
else:
    logger.error("Quote signals system failed to initialize")
