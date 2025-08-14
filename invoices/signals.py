from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from celery import shared_task
import logging
from .models import Invoice, InvoiceItem
from .utils import PDFInvoiceGenerator, InvoiceEmailService, FilePathGenerator

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Invoice)
def handle_invoice_creation(sender, instance, created, **kwargs):
    if created:
        try:
            instance.calculate_totals()

            if instance.is_ndis_invoice:
                validate_ndis_compliance(instance)

            logger.info(f"Invoice {instance.invoice_number} totals calculated")

        except Exception as e:
            logger.error(
                f"Failed to process new invoice {instance.invoice_number}: {str(e)}"
            )


@receiver(pre_save, sender=Invoice)
def update_invoice_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Invoice.objects.get(pk=instance.pk)

            if old_instance.status != instance.status:
                if instance.status == "sent" and not instance.email_sent:
                    send_invoice_email.delay(instance.id)

                logger.info(
                    f"Invoice {instance.invoice_number} status changed from {old_instance.status} to {instance.status}"
                )

        except Invoice.DoesNotExist:
            pass
        except Exception as e:
            logger.error(
                f"Failed to update invoice status for {instance.invoice_number}: {str(e)}"
            )


@shared_task
def generate_and_send_invoice(invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)

        pdf_generated = generate_invoice_pdf(invoice)

        if pdf_generated:
            email_sent = send_invoice_email_task(invoice)

            if email_sent:
                invoice.mark_as_sent()
                logger.info(
                    f"Invoice {invoice.invoice_number} generated and sent successfully"
                )
            else:
                logger.error(
                    f"Failed to send email for invoice {invoice.invoice_number}"
                )
        else:
            logger.error(f"Failed to generate PDF for invoice {invoice.invoice_number}")

    except Invoice.DoesNotExist:
        logger.error(f"Invoice with id {invoice_id} not found")
    except Exception as e:
        logger.error(f"Failed to generate and send invoice {invoice_id}: {str(e)}")


@shared_task
def send_invoice_email(invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        success = send_invoice_email_task(invoice)

        if success:
            logger.info(f"Invoice email sent successfully for {invoice.invoice_number}")
        else:
            logger.error(f"Failed to send invoice email for {invoice.invoice_number}")

        return success

    except Invoice.DoesNotExist:
        logger.error(f"Invoice with id {invoice_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send invoice email for {invoice_id}: {str(e)}")
        return False


def validate_ndis_compliance(invoice):
    errors = []

    if not invoice.participant_name:
        errors.append("Participant name missing")

    if not invoice.ndis_number:
        errors.append("NDIS number missing")

    if not invoice.service_start_date:
        errors.append("Service start date missing")

    if not invoice.service_end_date:
        errors.append("Service end date missing")

    if errors:
        logger.warning(
            f"NDIS compliance issues for invoice {invoice.invoice_number}: {', '.join(errors)}"
        )

    return len(errors) == 0


def generate_invoice_pdf(invoice):
    try:
        pdf_path = FilePathGenerator.generate_invoice_pdf_path(invoice)
        FilePathGenerator.ensure_directory_exists(pdf_path)

        generator = PDFInvoiceGenerator()
        success = generator.generate_pdf(invoice, pdf_path)

        if success:
            import os

            relative_path = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            invoice.pdf_file.name = relative_path
            invoice.save(update_fields=["pdf_file"])

        return success

    except Exception as e:
        logger.error(
            f"PDF generation failed for invoice {invoice.invoice_number}: {str(e)}"
        )
        return False


def send_invoice_email_task(invoice):
    try:
        pdf_path = invoice.pdf_file.path if invoice.pdf_file else None
        success = InvoiceEmailService.send_invoice_email(invoice, pdf_path)

        if success:
            invoice.email_sent = True
            invoice.email_sent_at = timezone.now()
            invoice.save(update_fields=["email_sent", "email_sent_at"])

        return success

    except Exception as e:
        logger.error(
            f"Email sending failed for invoice {invoice.invoice_number}: {str(e)}"
        )
        return False
