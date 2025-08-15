from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from decimal import Decimal
import csv
import json

from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate
from .serializers import (
    QuoteListSerializer,
    QuoteDetailSerializer,
    QuoteCreateSerializer,
    QuoteUpdateSerializer,
    QuoteStatusUpdateSerializer,
    QuoteItemSerializer,
    QuoteAttachmentSerializer,
    QuoteRevisionSerializer,
    QuoteTemplateSerializer,
    QuoteCalculatorSerializer,
    QuoteCalculatorResponseSerializer,
    QuoteAssignmentSerializer,
    QuoteApprovalSerializer,
    QuoteRejectionSerializer,
    QuoteDuplicateSerializer,
    BulkQuoteOperationSerializer,
    QuoteAnalyticsSerializer,
    QuoteReportSerializer,
    QuoteExportSerializer,
    QuoteSearchSerializer,
    QuoteStatisticsSerializer,
    QuoteDashboardSerializer,
    QuoteConversionSerializer,
    QuoteNotificationSerializer,
)
from .permissions import (
    IsQuoteOwnerOrStaff,
    IsQuoteOwner,
    IsStaffUser,
    CanViewQuote,
    CanEditQuote,
    CanApproveQuote,
    CanRejectQuote,
    CanDeleteQuote,
    CanUploadAttachment,
    CanViewAttachment,
    CanDeleteAttachment,
    CanCreateQuoteRevision,
    CanManageQuoteTemplate,
    CanViewQuoteAnalytics,
    CanExportQuotes,
    CanBulkUpdateQuotes,
    CanAssignQuote,
    QuoteStatusPermission,
    NDISQuotePermission,
    QuoteItemPermission,
    check_quote_permission,
)
from .filters import QuoteFilter, QuoteItemFilter, QuoteAttachmentFilter
from .validators import QuoteValidator
from .utils import (
    calculate_quote_pricing,
    generate_quote_pdf,
    send_quote_notification,
    duplicate_quote,
    bulk_quote_operation,
    get_quote_analytics_data,
    generate_quote_report,
    export_quotes_data,
)
from services.models import Service, ServiceAddOn
from django.db import transaction
import logging
from django.http import Http404

logger = logging.getLogger(__name__)

class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  # ← COMMENT OUT
    # filterset_class = QuoteFilter  # ← COMMENT OUT
    # search_fields = [  # ← COMMENT OUT THIS ENTIRE BLOCK
    #     "quote_number",
    #     "client__first_name",
    #     "client__last_name",
    #     "property_address",
    #     "suburb",
    #     "postcode",
    # ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "final_price",
        "urgency_level",
        "expires_at",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return QuoteListSerializer
        elif self.action == "create":
            return QuoteCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return QuoteUpdateSerializer
        elif self.action == "update_status":
            return QuoteStatusUpdateSerializer
        elif self.action == "assign":
            return QuoteAssignmentSerializer
        elif self.action == "approve":
            return QuoteApprovalSerializer
        elif self.action == "reject":
            return QuoteRejectionSerializer
        elif self.action == "duplicate":
            return QuoteDuplicateSerializer
        elif self.action == "convert":
            return QuoteConversionSerializer
        return QuoteDetailSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "destroy":
            permission_classes = [CanDeleteQuote]
        elif self.action in ["approve", "reject"]:
            permission_classes = [
                CanApproveQuote if self.action == "approve" else CanRejectQuote
            ]
        elif self.action == "assign":
            permission_classes = [CanAssignQuote]
        elif self.action in ["submit", "cancel"]:
            permission_classes = [QuoteStatusPermission]
        elif self.action == "convert":
            permission_classes = [IsStaffUser]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]    

    def get_queryset(self):
        logger.info(f"🔍 GET_QUERYSET - Action: {getattr(self, 'action', 'unknown')}")
        logger.info(f"🔍 GET_QUERYSET - User: {self.request.user.id} ({self.request.user.email})")
        logger.info(f"🔍 GET_QUERYSET - Is Staff: {self.request.user.is_staff}")
        logger.info(f"🔍 GET_QUERYSET - Request Path: {self.request.path}")

        queryset = Quote.objects.select_related(
            "client", "service", "assigned_to", "reviewed_by"
        ).prefetch_related("items", "attachments", "revisions")

        total_quotes = Quote.objects.count()
        logger.info(f"🔍 GET_QUERYSET - Total quotes in DB: {total_quotes}")

        if not self.request.user.is_staff:
            user_quotes = queryset.filter(client=self.request.user)
            user_count = user_quotes.count()
            logger.info(f"🔍 GET_QUERYSET - User's quotes: {user_count}")

            user_quote_ids = list(user_quotes.values_list('id', flat=True))
            logger.info(f"🔍 GET_QUERYSET - User's quote IDs: {user_quote_ids}")

            return user_quotes

        logger.info(f"🔍 GET_QUERYSET - Staff user, returning all quotes")
        return queryset

    def filter_queryset(self, queryset):
        """Override to disable all filtering for now"""
        logger.info(f"🔍 FILTER_QUERYSET - Original count: {queryset.count()}")
        
        # For retrieve action, return unfiltered queryset
        if self.action == 'retrieve':
            logger.info(f"🔍 FILTER_QUERYSET - Retrieve action, returning unfiltered")
            return queryset
        
        # For other actions, apply normal filtering
        filtered = super().filter_queryset(queryset)
        logger.info(f"🔍 FILTER_QUERYSET - Filtered count: {filtered.count()}")
        return filtered

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"🔍 RETRIEVE - Starting retrieve for: {kwargs}")
        logger.info(f"🔍 RETRIEVE - User: {request.user.id} ({request.user.email})")

        try:
            lookup_value = kwargs.get("pk")
            logger.info(f"🔍 RETRIEVE - Looking for quote: {lookup_value}")

            # Check if quote exists in database at all
            from quotes.models import Quote

            db_quote_exists = Quote.objects.filter(pk=lookup_value).exists()
            logger.info(f"🔍 RETRIEVE - Quote exists in DB: {db_quote_exists}")

            if db_quote_exists:
                db_quote = Quote.objects.get(pk=lookup_value)
                logger.info(f"🔍 RETRIEVE - DB Quote client: {db_quote.client.id}")
                logger.info(f"🔍 RETRIEVE - Current user: {request.user.id}")
                logger.info(
                    f"🔍 RETRIEVE - User owns quote: {db_quote.client.id == request.user.id}"
                )

            # Debug the queryset before get_object
            queryset = self.get_queryset()
            logger.info(
                f"🔍 RETRIEVE - Queryset count before get_object: {queryset.count()}"
            )
            quote_in_queryset = queryset.filter(pk=lookup_value).exists()
            logger.info(f"🔍 RETRIEVE - Quote in queryset: {quote_in_queryset}")

            # Try filter_queryset to see if that's the issue
            filtered_queryset = self.filter_queryset(queryset)
            logger.info(
                f"🔍 RETRIEVE - Filtered queryset count: {filtered_queryset.count()}"
            )
            quote_in_filtered = filtered_queryset.filter(pk=lookup_value).exists()
            logger.info(
                f"🔍 RETRIEVE - Quote in filtered queryset: {quote_in_filtered}"
            )

            # Now try the normal get_object
            instance = self.get_object()
            logger.info(f"🔍 RETRIEVE - get_object() succeeded: {instance.id}")

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"🔍 RETRIEVE - Error: {str(e)}")
            logger.error(f"🔍 RETRIEVE - Error type: {type(e)}")
            raise

    def perform_create(self, serializer):
        quote = serializer.save(client=self.request.user)
        return quote

    def create(self, request, *args, **kwargs):

        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            quote = self.perform_create(serializer)

            transaction.on_commit(lambda: None)

            quote.refresh_from_db()

            response_serializer = QuoteDetailSerializer(quote, context={"request": request})
            headers = self.get_success_headers(response_serializer.data)
            return Response(
                response_serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )    

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        quote = self.get_object()

        if quote.submit_quote():
            send_quote_notification(quote, "submitted", "staff")
            return Response(
                {"message": "Quote submitted successfully", "status": quote.status}
            )

        return Response(
            {"error": "Quote cannot be submitted"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        quote = self.get_object()
        serializer = self.get_serializer(quote, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if quote.approve_quote(request.user):
                send_quote_notification(quote, "approved", "client")
                return Response(
                    {
                        "message": "Quote approved successfully",
                        "status": quote.status,
                        "expires_at": quote.expires_at,
                    }
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        quote = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            rejection_reason = serializer.validated_data["rejection_reason"]

            if quote.reject_quote(request.user, rejection_reason):
                send_quote_notification(quote, "rejected", "client")
                return Response(
                    {
                        "message": "Quote rejected successfully",
                        "status": quote.status,
                        "rejection_reason": rejection_reason,
                    }
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        quote = self.get_object()

        if quote.status not in ["converted", "cancelled"]:
            quote.status = "cancelled"
            quote.save()

            send_quote_notification(quote, "cancelled", "both")
            return Response(
                {"message": "Quote cancelled successfully", "status": quote.status}
            )

        return Response(
            {"error": "Quote cannot be cancelled"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        quote = self.get_object()
        serializer = self.get_serializer(quote, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Quote assigned successfully",
                    "assigned_to": (
                        quote.assigned_to.get_full_name() if quote.assigned_to else None
                    ),
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        quote = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            new_quote = duplicate_quote(quote, request.user, serializer.validated_data)
            response_serializer = QuoteDetailSerializer(
                new_quote, context={"request": request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        quote = self.get_object()

        if not quote.can_be_accepted:
            return Response(
                {"error": "Quote cannot be converted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            quote.status = "converted"
            quote.save()

            return Response(
                {
                    "message": "Quote converted to job successfully",
                    "status": quote.status,
                    "job_data": serializer.validated_data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        quote = self.get_object()

        try:
            pdf_content = generate_quote_pdf(quote)
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="quote_{quote.quote_number}.pdf"'
            )
            return response
        except Exception as e:
            return Response(
                {"error": "Failed to generate PDF"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def recalculate_pricing(self, request, pk=None):
        quote = self.get_object()

        if quote.status in ["draft", "submitted", "under_review"]:
            quote.update_pricing()
            serializer = QuoteDetailSerializer(quote, context={"request": request})
            return Response(serializer.data)

        return Response(
            {"error": "Cannot recalculate pricing for quote with current status"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def bulk_operations(self, request):
        serializer = BulkQuoteOperationSerializer(data=request.data)

        if serializer.is_valid():
            result = bulk_quote_operation(serializer.validated_data, request.user)
            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        stats = Quote.objects.statistics()
        serializer = QuoteStatisticsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        dashboard_data = Quote.objects.get_dashboard_data(request.user)
        serializer = QuoteDashboardSerializer(dashboard_data)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def search(self, request):
        serializer = QuoteSearchSerializer(data=request.data)

        if serializer.is_valid():
            queryset = self.get_queryset()

            query = serializer.validated_data.get("query")
            if query:
                queryset = queryset.search(query)

            status_filter = serializer.validated_data.get("status")
            if status_filter:
                queryset = queryset.filter(status__in=status_filter)

            cleaning_type_filter = serializer.validated_data.get("cleaning_type")
            if cleaning_type_filter:
                queryset = queryset.filter(cleaning_type__in=cleaning_type_filter)

            urgency_filter = serializer.validated_data.get("urgency_level")
            if urgency_filter:
                queryset = queryset.filter(urgency_level__in=urgency_filter)

            is_ndis = serializer.validated_data.get("is_ndis_client")
            if is_ndis is not None:
                queryset = queryset.filter(is_ndis_client=is_ndis)

            postcode = serializer.validated_data.get("postcode")
            if postcode:
                queryset = queryset.filter(postcode=postcode)

            state = serializer.validated_data.get("state")
            if state:
                queryset = queryset.filter(state=state)

            date_from = serializer.validated_data.get("date_from")
            date_to = serializer.validated_data.get("date_to")
            if date_from and date_to:
                queryset = queryset.by_date_range(date_from, date_to)

            price_min = serializer.validated_data.get("price_min")
            price_max = serializer.validated_data.get("price_max")
            if price_min is not None:
                queryset = queryset.filter(final_price__gte=price_min)
            if price_max is not None:
                queryset = queryset.filter(final_price__lte=price_max)

            assigned_to = serializer.validated_data.get("assigned_to")
            if assigned_to:
                queryset = queryset.filter(assigned_to_id=assigned_to)

            page = self.paginate_queryset(queryset)
            if page is not None:
                result_serializer = QuoteListSerializer(page, many=True)
                return self.get_paginated_response(result_serializer.data)

            result_serializer = QuoteListSerializer(queryset, many=True)
            return Response(result_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuoteCalculatorView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QuoteCalculatorSerializer(data=request.data)

        if serializer.is_valid():
            try:
                service = Service.objects.get(
                    service_type=serializer.validated_data["service_id"], is_active=True
                )

                addon_ids = serializer.validated_data.get("addon_ids", [])
                addons = (
                    ServiceAddOn.objects.filter(id__in=addon_ids, is_active=True)
                    if addon_ids
                    else []
                )

                pricing_data = calculate_quote_pricing(
                    {
                        "service": service,
                        "cleaning_type": serializer.validated_data["cleaning_type"],
                        "number_of_rooms": serializer.validated_data["number_of_rooms"],
                        "square_meters": serializer.validated_data.get("square_meters"),
                        "urgency_level": serializer.validated_data["urgency_level"],
                        "postcode": serializer.validated_data["postcode"],
                        "addons": addons,
                    }
                )

                response_serializer = QuoteCalculatorResponseSerializer(pricing_data)
                return Response(response_serializer.data)

            except Service.DoesNotExist:
                return Response(
                    {"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": "Calculation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class QuoteItemViewSet(viewsets.ModelViewSet):
    queryset = QuoteItem.objects.all()
    serializer_class = QuoteItemSerializer
    permission_classes = [QuoteItemPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = QuoteItemFilter
    ordering_fields = ["display_order", "created_at", "total_price"]
    ordering = ["display_order"]

    def get_queryset(self):
        queryset = QuoteItem.objects.select_related("quote", "service", "addon")

        if not self.request.user.is_staff:
            queryset = queryset.filter(quote__client=self.request.user)

        quote_id = self.request.query_params.get("quote_id")
        if quote_id:
            queryset = queryset.filter(quote_id=quote_id)

        return queryset

    def perform_create(self, serializer):
        quote = serializer.validated_data["quote"]
        if quote.status in ["draft", "submitted"]:
            serializer.save()
            quote.update_pricing()
        else:
            raise ValidationError("Cannot add items to quote with current status")

    def perform_update(self, serializer):
        quote = serializer.instance.quote
        if quote.status in ["draft", "submitted"]:
            serializer.save()
            quote.update_pricing()
        else:
            raise ValidationError("Cannot update items for quote with current status")

    def perform_destroy(self, instance):
        quote = instance.quote
        if quote.status in ["draft", "submitted"]:
            instance.delete()
            quote.update_pricing()
        else:
            raise ValidationError("Cannot delete items from quote with current status")


class QuoteAttachmentViewSet(viewsets.ModelViewSet):
    queryset = QuoteAttachment.objects.all()
    serializer_class = QuoteAttachmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = QuoteAttachmentFilter
    ordering_fields = ["display_order", "created_at", "file_size"]
    ordering = ["display_order"]

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [CanUploadAttachment]
        elif self.action in ["retrieve", "list"]:
            permission_classes = [CanViewAttachment]
        elif self.action == "destroy":
            permission_classes = [CanDeleteAttachment]
        else:
            permission_classes = [IsQuoteOwnerOrStaff]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = QuoteAttachment.objects.select_related("quote", "uploaded_by")

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(quote__client=self.request.user) | Q(uploaded_by=self.request.user)
            )

        quote_id = self.request.query_params.get("quote_id")
        if quote_id:
            queryset = queryset.filter(quote_id=quote_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        attachment = self.get_object()

        try:
            response = HttpResponse(
                attachment.file.read(),
                content_type=attachment.file_type or "application/octet-stream",
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{attachment.original_filename}"'
            )
            return response
        except Exception:
            return Response(
                {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
            )


class QuoteRevisionViewSet(viewsets.ModelViewSet):
    queryset = QuoteRevision.objects.all()
    serializer_class = QuoteRevisionSerializer
    permission_classes = [CanCreateQuoteRevision]
    ordering = ["-revision_number"]

    def get_queryset(self):
        queryset = QuoteRevision.objects.select_related("quote", "revised_by")

        if not self.request.user.is_staff:
            queryset = queryset.filter(quote__client=self.request.user)

        quote_id = self.request.query_params.get("quote_id")
        if quote_id:
            queryset = queryset.filter(quote_id=quote_id)

        return queryset

    def perform_create(self, serializer):
        quote = serializer.validated_data["quote"]
        last_revision = quote.revisions.order_by("-revision_number").first()
        revision_number = (last_revision.revision_number + 1) if last_revision else 1

        serializer.save(revised_by=self.request.user, revision_number=revision_number)

class QuoteTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = QuoteTemplateSerializer
    permission_classes = [CanManageQuoteTemplate]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "usage_count", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        user_templates = QuoteTemplate.objects.filter(created_by=self.request.user)
        system_templates = QuoteTemplate.objects.filter(
            created_by__is_staff=True, is_active=True
        )

        queryset = (
            (user_templates | system_templates)
            .select_related("default_service", "created_by")
            .distinct()
        )

        cleaning_type = self.request.query_params.get("cleaning_type")
        if cleaning_type:
            queryset = queryset.filter(cleaning_type=cleaning_type)

        is_ndis = self.request.query_params.get("is_ndis")
        if is_ndis is not None:
            queryset = queryset.filter(is_ndis_template=is_ndis.lower() == "true")

        if self.action == "list":
            queryset = queryset.filter(is_active=True)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.created_by != self.request.user:
            raise PermissionDenied("You can only update your own templates")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied("You can only delete your own templates")
        instance.delete()

    @action(detail=True, methods=["post"])
    def use_template(self, request, pk=None):
        template = self.get_object()

        quote_data = {
            "service_type": (
                template.default_service.service_type
                if template.default_service
                else None
            ),
            "cleaning_type": template.cleaning_type,
            "urgency_level": template.default_urgency_level,
            "number_of_rooms": template.number_of_rooms,
            "square_meters": template.square_meters,
            "special_requirements": template.special_requirements,
            "access_instructions": template.access_instructions,
            "is_ndis_client": template.is_ndis_template,
        }

        quote_data.update(request.data)

        serializer = QuoteCreateSerializer(
            data=quote_data, context={"request": request}
        )
        if serializer.is_valid():
            quote = serializer.save(client=request.user)
            template.increment_usage()

            response_serializer = QuoteDetailSerializer(
                quote, context={"request": request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class QuoteAnalyticsView(APIView):
    permission_classes = [CanViewQuoteAnalytics]

    def post(self, request):
        serializer = QuoteAnalyticsSerializer(data=request.data)

        if serializer.is_valid():
            analytics_data = get_quote_analytics_data(serializer.validated_data)
            return Response(analytics_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        default_params = {
            "group_by": "status",
            "include_ndis": True,
            "include_general": True,
        }

        analytics_data = get_quote_analytics_data(default_params)
        return Response(analytics_data)


class QuoteReportView(APIView):
    permission_classes = [CanViewQuoteAnalytics]

    def post(self, request):
        serializer = QuoteReportSerializer(data=request.data)

        if serializer.is_valid():
            try:
                report_data = generate_quote_report(serializer.validated_data)

                if serializer.validated_data["format"] == "pdf":
                    response = HttpResponse(report_data, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        'attachment; filename="quote_report.pdf"'
                    )
                elif serializer.validated_data["format"] == "excel":
                    response = HttpResponse(
                        report_data,
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    response["Content-Disposition"] = (
                        'attachment; filename="quote_report.xlsx"'
                    )
                else:
                    response = HttpResponse(report_data, content_type="text/csv")
                    response["Content-Disposition"] = (
                        'attachment; filename="quote_report.csv"'
                    )

                return response

            except Exception as e:
                return Response(
                    {"error": "Report generation failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuoteExportView(APIView):
    permission_classes = [CanExportQuotes]

    def post(self, request):
        serializer = QuoteExportSerializer(data=request.data)

        if serializer.is_valid():
            try:
                export_data = export_quotes_data(
                    serializer.validated_data, request.user
                )

                if serializer.validated_data["format"] == "csv":
                    response = HttpResponse(export_data, content_type="text/csv")
                    response["Content-Disposition"] = (
                        'attachment; filename="quotes_export.csv"'
                    )
                elif serializer.validated_data["format"] == "excel":
                    response = HttpResponse(
                        export_data,
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    response["Content-Disposition"] = (
                        'attachment; filename="quotes_export.xlsx"'
                    )
                else:
                    response = HttpResponse(export_data, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        'attachment; filename="quotes_export.pdf"'
                    )

                return response

            except Exception as e:
                return Response(
                    {"error": "Export failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuoteNotificationView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = QuoteNotificationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                quote = Quote.objects.get(id=serializer.validated_data["quote_id"])

                send_quote_notification(
                    quote,
                    serializer.validated_data["notification_type"],
                    serializer.validated_data["recipient_type"],
                    serializer.validated_data.get("custom_message"),
                )

                return Response({"message": "Notification sent successfully"})

            except Quote.DoesNotExist:
                return Response(
                    {"error": "Quote not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"error": "Notification failed"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = QuoteFilter
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Quote.objects.filter(client=self.request.user)
            .select_related("service", "assigned_to")
            .prefetch_related("items", "attachments")
        )


class PendingQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["created_at"]

    def get_queryset(self):
        return (
            Quote.objects.pending()
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )


class ExpiringQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    ordering = ["expires_at"]

    def get_queryset(self):
        days = self.request.query_params.get("days", 7)
        try:
            days = int(days)
        except (ValueError, TypeError):
            days = 7

        return (
            Quote.objects.expiring_soon(days)
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )


class UrgentQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    ordering = ["-urgency_level", "created_at"]

    def get_queryset(self):
        return (
            Quote.objects.urgent()
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )


class NDISQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [NDISQuotePermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Quote.objects.ndis_quotes()
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )

        if not self.request.user.is_staff:
            queryset = queryset.filter(client=self.request.user)

        return queryset


class HighValueQuotesView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    ordering = ["-final_price"]

    def get_queryset(self):
        threshold = self.request.query_params.get("threshold", 1000)
        try:
            threshold = float(threshold)
        except (ValueError, TypeError):
            threshold = 1000

        return (
            Quote.objects.high_value(threshold)
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )


class QuotesByServiceView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        service_id = self.kwargs.get("service_id")
        return (
            Quote.objects.filter(service_id=service_id)
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )

class QuotesByClientView(ListAPIView):
    serializer_class = QuoteListSerializer
    permission_classes = [IsStaffUser]
    filter_backends = [OrderingFilter]
    ordering = ["-created_at"]

    def get_queryset(self):
        client_id = self.kwargs.get("client_id")
        return (
            Quote.objects.filter(client_id=client_id)
            .select_related("client", "service", "assigned_to")
            .prefetch_related("items", "attachments")
        )

class QuoteConversionRateView(APIView):
    permission_classes = [CanViewQuoteAnalytics]

    def get(self, request):
        total_quotes = Quote.objects.count()
        converted_quotes = Quote.objects.filter(status="converted").count()

        conversion_rate = (
            (converted_quotes / total_quotes * 100) if total_quotes > 0 else 0
        )

        return Response(
            {
                "total_quotes": total_quotes,
                "converted_quotes": converted_quotes,
                "conversion_rate": round(conversion_rate, 2),
            }
        )

class QuoteStatusDistributionView(APIView):
    permission_classes = [CanViewQuoteAnalytics]

    def get(self, request):
        distribution = (
            Quote.objects.values("status")
            .annotate(
                count=Count("id"),
                total_value=Sum("final_price"),
                avg_value=Avg("final_price"),
            )
            .order_by("-count")
        )

        return Response(list(distribution))


class QuoteMonthlyTrendsView(APIView):
    permission_classes = [CanViewQuoteAnalytics]

    def get(self, request):
        trends = (
            Quote.objects.extra(select={"month": "DATE_FORMAT(created_at, '%%Y-%%m')"})
            .values("month")
            .annotate(
                count=Count("id"),
                total_value=Sum("final_price"),
                avg_value=Avg("final_price"),
            )
            .order_by("month")
        )

        return Response(list(trends))
