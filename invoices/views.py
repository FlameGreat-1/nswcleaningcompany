from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Sum
from decimal import Decimal
import os
import logging
from .models import Invoice, InvoiceItem
from .serializers import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceItemSerializer,
    NDISInvoiceSerializer,
    InvoiceActionSerializer,
    ClientInvoiceListSerializer,
)
from .permissions import InvoiceViewPermission, NDISInvoicePermission, IsOwnerOrAdmin
from .signals import send_invoice_email

logger = logging.getLogger(__name__)


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, InvoiceViewPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "is_ndis_invoice", "email_sent"]
    search_fields = [
        "invoice_number",
        "client__first_name",
        "client__last_name",
        "participant_name",
    ]
    ordering_fields = ["invoice_date", "due_date", "total_amount", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_admin_user or user.is_staff:
            return Invoice.objects.select_related("client", "quote").prefetch_related(
                "items"
            )

        if user.is_client:
            return (
                Invoice.objects.filter(client=user)
                .select_related("client", "quote")
                .prefetch_related("items")
            )

        return Invoice.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        return InvoiceSerializer

    def retrieve(self, request, *args, **kwargs):
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def download_pdf(self, request, pk=None):
        invoice = self.get_object()

        if not invoice.pdf_file:
            try:
                success = invoice.generate_pdf()
                if not success:
                    return Response(
                        {"error": "Failed to generate PDF"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except Exception as e:
                logger.error(
                    f"PDF generation failed for invoice {invoice.invoice_number}: {str(e)}"
                )
                return Response(
                    {"error": "PDF generation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if not os.path.exists(invoice.pdf_file.path):
            return Response(
                {"error": "PDF file not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with open(invoice.pdf_file.path, "rb") as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type="application/pdf")
                response["Content-Disposition"] = (
                    f'attachment; filename="{invoice.invoice_number}.pdf"'
                )
                return response
        except Exception as e:
            logger.error(
                f"PDF download failed for invoice {invoice.invoice_number}: {str(e)}"
            )
            return Response(
                {"error": "Failed to download PDF"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def resend_email(self, request, pk=None):
        invoice = self.get_object()

        if not invoice.client.email:
            return Response(
                {"error": "Client email address is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            success = invoice.send_email()
            if success:
                return Response(
                    {
                        "message": f"Invoice {invoice.invoice_number} sent successfully to {invoice.client.email}",
                        "email_sent": True,
                        "email_sent_at": invoice.email_sent_at,
                    }
                )
            else:
                return Response(
                    {"error": "Failed to send invoice email"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            logger.error(
                f"Email sending failed for invoice {invoice.invoice_number}: {str(e)}"
            )
            return Response(
                {"error": "Failed to send invoice email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def regenerate_pdf(self, request, pk=None):
        invoice = self.get_object()

        if not (request.user.is_admin_user or request.user.is_staff):
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            success = invoice.generate_pdf()
            if success:
                return Response(
                    {
                        "message": f"PDF regenerated successfully for invoice {invoice.invoice_number}",
                        "pdf_url": (
                            request.build_absolute_uri(invoice.pdf_file.url)
                            if invoice.pdf_file
                            else None
                        ),
                    }
                )
            else:
                return Response(
                    {"error": "Failed to regenerate PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            logger.error(
                f"PDF regeneration failed for invoice {invoice.invoice_number}: {str(e)}"
            )
            return Response(
                {"error": "PDF regeneration failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path='my-invoices')
    def my_invoices(self, request):
        if not request.user.is_client:
            return Response(
                {"error": "Only clients can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )

        invoices = (
            Invoice.objects.filter(client=request.user)
            .select_related("client", "quote")
            .prefetch_related("items")
        )

        status_filter = request.query_params.get("status")
        if status_filter and status_filter != "all":
            invoices = invoices.filter(status=status_filter)

        search = request.query_params.get("search")
        if search:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search)
                | Q(client__first_name__icontains=search)
                | Q(client__last_name__icontains=search)
                | Q(participant_name__icontains=search)
            )

        is_ndis = request.query_params.get("is_ndis_invoice")
        if is_ndis is not None and is_ndis != "null":
            invoices = invoices.filter(is_ndis_invoice=is_ndis.lower() == "true")

        email_sent = request.query_params.get("email_sent")
        if email_sent is not None and email_sent != "null":
            invoices = invoices.filter(email_sent=email_sent.lower() == "true")

        ordering = request.query_params.get("ordering", "-created_at")
        invoices = invoices.order_by(ordering)

        serializer = ClientInvoiceListSerializer(
            invoices, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def ndis_invoices(self, request):
        user = request.user

        if user.is_admin_user or user.is_staff:
            invoices = Invoice.objects.filter(is_ndis_invoice=True)
        elif user.is_client and user.is_ndis_client:
            invoices = Invoice.objects.filter(client=user, is_ndis_invoice=True)
        else:
            return Response(
                {"error": "Access denied to NDIS invoices"},
                status=status.HTTP_403_FORBIDDEN,
            )

        invoices = invoices.select_related("client").prefetch_related("items")
        serializer = NDISInvoiceSerializer(
            invoices, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def dashboard_stats(self, request):
        if not (request.user.is_admin_user or request.user.is_staff):
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        stats = Invoice.objects.aggregate(
            total_invoices=Count("id"),
            total_amount=Sum("total_amount"),
            draft_count=Count("id", filter=Q(status="draft")),
            sent_count=Count("id", filter=Q(status="sent")),
            ndis_count=Count("id", filter=Q(is_ndis_invoice=True)),
            emails_sent=Count("id", filter=Q(email_sent=True)),
        )

        stats["total_amount"] = stats["total_amount"] or Decimal("0.00")

        return Response(stats)


class InvoiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user

        if user.is_admin_user or user.is_staff:
            return InvoiceItem.objects.select_related("invoice", "invoice__client")

        if user.is_client:
            return InvoiceItem.objects.filter(invoice__client=user).select_related(
                "invoice"
            )

        return InvoiceItem.objects.none()


class NDISInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NDISInvoiceSerializer
    permission_classes = [IsAuthenticated, NDISInvoicePermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["invoice_number", "participant_name", "ndis_number"]
    ordering_fields = ["invoice_date", "service_start_date", "total_amount"]
    ordering = ["-invoice_date"]

    def get_queryset(self):
        user = self.request.user

        base_queryset = (
            Invoice.objects.filter(is_ndis_invoice=True)
            .select_related("client")
            .prefetch_related("items")
        )

        if user.is_admin_user or user.is_staff:
            return base_queryset

        if user.is_client and user.is_ndis_client:
            return base_queryset.filter(client=user)

        return Invoice.objects.none()

    @action(detail=True, methods=["get"])
    def compliance_check(self, request, pk=None):
        invoice = self.get_object()

        compliance_issues = []

        if not invoice.participant_name:
            compliance_issues.append("Missing participant name")

        if not invoice.ndis_number:
            compliance_issues.append("Missing NDIS number")

        if not invoice.service_start_date:
            compliance_issues.append("Missing service start date")

        if not invoice.service_end_date:
            compliance_issues.append("Missing service end date")

        return Response(
            {
                "is_compliant": len(compliance_issues) == 0,
                "issues": compliance_issues,
                "invoice_number": invoice.invoice_number,
            }
        )
