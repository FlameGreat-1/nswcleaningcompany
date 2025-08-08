from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class InvoiceNumberGenerator:
    
    @staticmethod
    def generate_invoice_number() -> str:
        from django.db.models import Max
        from .models import Invoice
        import re
        
        current_year = timezone.now().year
        prefix = f"INV-{current_year}-"
        
        latest_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).aggregate(Max("invoice_number"))["invoice_number__max"]
        
        if latest_invoice:
            match = re.search(r"-(\d{4})$", latest_invoice)
            next_number = int(match.group(1)) + 1 if match else 1
        else:
            next_number = 1
            
        return f"{prefix}{next_number:04d}"


class NDISComplianceValidator:
    
    @staticmethod
    def validate_ndis_invoice_fields(invoice_data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        
        if not invoice_data.get('participant_name'):
            errors.setdefault('participant_name', []).append('Participant name is required for NDIS invoices')
            
        if not invoice_data.get('ndis_number'):
            errors.setdefault('ndis_number', []).append('NDIS number is required for NDIS invoices')
            
        if not invoice_data.get('service_dates'):
            errors.setdefault('service_dates', []).append('Service dates are required for NDIS invoices')
            
        if not invoice_data.get('provider_details'):
            errors.setdefault('provider_details', []).append('Provider details are required for NDIS invoices')
            
        return errors
    
    @staticmethod
    def format_ndis_number(ndis_number: str) -> str:
        cleaned = ''.join(filter(str.isdigit, ndis_number))
        if len(cleaned) == 9:
            return f"{cleaned[:2]} {cleaned[2:5]} {cleaned[5:8]} {cleaned[8:]}"
        return ndis_number


class PricingCalculator:
    
    @staticmethod
    def calculate_gst(amount: Decimal, gst_rate: Decimal = Decimal('0.10')) -> Decimal:
        return (amount * gst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_total_with_gst(amount: Decimal, gst_rate: Decimal = Decimal('0.10')) -> Decimal:
        gst_amount = PricingCalculator.calculate_gst(amount, gst_rate)
        return amount + gst_amount
    
    @staticmethod
    def calculate_invoice_totals(items: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        subtotal = Decimal('0.00')
        gst_total = Decimal('0.00')
        
        for item in items:
            item_total = Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
            subtotal += item_total
            
            if item.get('is_taxable', True):
                gst_total += PricingCalculator.calculate_gst(item_total)
        
        return {
            'subtotal': subtotal,
            'gst_amount': gst_total,
            'total_amount': subtotal + gst_total
        }


class PDFInvoiceGenerator:
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#34495e')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ClientInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#34495e')
        ))
    
    def generate_pdf(self, invoice, file_path: str) -> bool:
        try:
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            story.extend(self._build_header(invoice))
            story.extend(self._build_invoice_details(invoice))
            story.extend(self._build_client_info(invoice))
            story.extend(self._build_items_table(invoice))
            story.extend(self._build_totals_section(invoice))
            
            if invoice.is_ndis_invoice:
                story.extend(self._build_ndis_section(invoice))
            
            story.extend(self._build_footer(invoice))
            
            doc.build(story)
            return True
            
        except Exception as e:
            logger.error(f"PDF generation failed for invoice {invoice.invoice_number}: {str(e)}")
            return False
    
    def _build_header(self, invoice) -> List:
        elements = []
        
        logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(logo)
        
        elements.append(Spacer(1, 20))
        
        company_info = f"""
        <b>{getattr(settings, 'COMPANY_NAME', 'Cleaning Service')}</b><br/>
        ABN: {getattr(settings, 'COMPANY_ABN', 'XX XXX XXX XXX')}<br/>
        {getattr(settings, 'COMPANY_ADDRESS', '')}<br/>
        Phone: {getattr(settings, 'COMPANY_PHONE', '')}<br/>
        Email: {getattr(settings, 'COMPANY_EMAIL', '')}
        """
        
        elements.append(Paragraph(company_info, self.styles['CompanyInfo']))
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_invoice_details(self, invoice) -> List:
        elements = []
        
        elements.append(Paragraph("INVOICE", self.styles['InvoiceTitle']))
        
        invoice_details = [
            ['Invoice Number:', invoice.invoice_number],
            ['Invoice Date:', invoice.invoice_date.strftime('%d/%m/%Y')],
            ['Due Date:', invoice.due_date.strftime('%d/%m/%Y')],
            ['Status:', invoice.get_status_display()]
        ]
        
        if invoice.quote:
            invoice_details.append(['Quote Number:', invoice.quote.quote_number])
        
        details_table = Table(invoice_details, colWidths=[2*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_client_info(self, invoice) -> List:
        elements = []
        
        client_info = f"""
        <b>Bill To:</b><br/>
        {invoice.client.full_name}<br/>
        {invoice.billing_address}<br/>
        Phone: {invoice.client.phone_number or 'N/A'}<br/>
        Email: {invoice.client.email}
        """
        
        elements.append(Paragraph(client_info, self.styles['ClientInfo']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_items_table(self, invoice) -> List:
        elements = []
        
        data = [['Description', 'Quantity', 'Unit Price', 'GST', 'Total']]
        
        for item in invoice.items.all():
            gst_status = 'Inc. GST' if item.is_taxable else 'GST Free'
            data.append([
                item.description,
                str(item.quantity),
                f"${item.unit_price:.2f}",
                gst_status,
                f"${item.total_price:.2f}"
            ])
        
        items_table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_totals_section(self, invoice) -> List:
        elements = []
        
        totals_data = [
            ['Subtotal:', f"${invoice.subtotal:.2f}"],
            ['GST Amount:', f"${invoice.gst_amount:.2f}"],
            ['Total Amount:', f"${invoice.total_amount:.2f}"]
        ]
        
        if invoice.paid_amount > 0:
            totals_data.append(['Paid Amount:', f"${invoice.paid_amount:.2f}"])
            totals_data.append(['Balance Due:', f"${invoice.balance_due:.2f}"])
        
        totals_table = Table(totals_data, colWidths=[2*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_ndis_section(self, invoice) -> List:
        elements = []
        
        elements.append(Paragraph("<b>NDIS Information</b>", self.styles['Heading2']))
        
        ndis_data = [
            ['Participant Name:', invoice.participant_name or 'N/A'],
            ['NDIS Number:', NDISComplianceValidator.format_ndis_number(invoice.ndis_number or '')],
            ['Service Period:', f"{invoice.service_start_date.strftime('%d/%m/%Y')} - {invoice.service_end_date.strftime('%d/%m/%Y')}"],
            ['Provider Registration:', getattr(settings, 'NDIS_PROVIDER_NUMBER', 'N/A')]
        ]
        
        ndis_table = Table(ndis_data, colWidths=[2*inch, 3*inch])
        ndis_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(ndis_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_footer(self, invoice) -> List:
        elements = []
        
        footer_text = f"""
        <b>Payment Terms:</b> Payment due within {invoice.payment_terms} days<br/>
        <b>Payment Methods:</b> Bank Transfer, Credit Card<br/>
        <br/>
        Thank you for choosing our services!
        """
        
        elements.append(Paragraph(footer_text, self.styles['Normal']))
        
        return elements


class InvoiceEmailService:
    
    @staticmethod
    def send_invoice_email(invoice, pdf_path: str) -> bool:
        try:
            subject = f"Invoice {invoice.invoice_number} - {getattr(settings, 'COMPANY_NAME', 'Cleaning Service')}"
            
            context = {
                'invoice': invoice,
                'client_name': invoice.client.full_name,
                'company_name': getattr(settings, 'COMPANY_NAME', 'Cleaning Service')
            }
            
            html_content = render_to_string('emails/invoice_email.html', context)
            text_content = render_to_string('emails/invoice_email.txt', context)
            
            email = EmailMessage(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client.email],
                reply_to=[getattr(settings, 'COMPANY_EMAIL', settings.DEFAULT_FROM_EMAIL)]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            if os.path.exists(pdf_path):
                email.attach_file(pdf_path)
            
            email.send()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send invoice email for {invoice.invoice_number}: {str(e)}")
            return False


class DateTimeUtils:
    
    @staticmethod
    def calculate_due_date(invoice_date: datetime, payment_terms: int) -> datetime:
        return invoice_date + timedelta(days=payment_terms)
    
    @staticmethod
    def is_overdue(due_date: datetime) -> bool:
        return timezone.now().date() > due_date
    
    @staticmethod
    def days_overdue(due_date: datetime) -> int:
        if DateTimeUtils.is_overdue(due_date):
            return (timezone.now().date() - due_date).days
        return 0


class FilePathGenerator:
    
    @staticmethod
    def generate_invoice_pdf_path(invoice) -> str:
        year = invoice.invoice_date.year
        month = invoice.invoice_date.month
        filename = f"{invoice.invoice_number}.pdf"
        
        return os.path.join(
            settings.MEDIA_ROOT,
            'invoices',
            'pdfs',
            str(year),
            f"{month:02d}",
            filename
        )
    
    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
