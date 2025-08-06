from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Min, Max
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import (
    Service,
    ServiceCategory,
    ServiceArea,
    NDISServiceCode,
    ServiceAddOn,
    ServiceAvailability,
    ServicePricing,
)
from .serializers import (
    ServiceSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
    ServiceCreateUpdateSerializer,
    ServiceCategorySerializer,
    ServiceCategoryListSerializer,
    ServiceAreaSerializer,
    ServiceAreaListSerializer,
    NDISServiceCodeSerializer,
    ServiceAddOnSerializer,
    ServiceAvailabilitySerializer,
    ServicePricingSerializer,
    ServiceQuoteRequestSerializer,
    ServiceSearchSerializer,
    ServiceStatsSerializer,
    BulkServiceActionSerializer,
)
from .permissions import (
    CanViewServices,
    CanManageServices,
    CanAccessNDISServices,
    CanViewServicePricing,
    CanManageServicePricing,
    CanViewServiceAreas,
    CanManageServiceAreas,
    CanAccessServiceAvailability,
    CanManageServiceAvailability,
    CanViewNDISServiceCodes,
    CanManageNDISServiceCodes,
    CanViewServiceCategories,
    CanManageServiceCategories,
    CanAccessServiceAddOns,
    CanManageServiceAddOns,
    CanBulkManageServices,
    CanAccessServiceReports,
    NDISCompliancePermission,
    ServiceLocationPermission,
    ServiceQuotePermission,
    ServiceBookingPermission,
)
from .filters import ServiceFilter, ServiceCategoryFilter, ServiceAreaFilter
from .utils import (
    calculate_service_quote,
    get_available_time_slots,
    validate_service_request,
)


class ServiceCategoryViewSet(ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True).order_by(
        "display_order", "name"
    )
    permission_classes = [CanViewServiceCategories]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceCategoryFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_at"]
    ordering = ["display_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceCategoryListSerializer
        return ServiceCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            if (
                self.request.user.user_type == "client"
                and self.request.user.client_type == "ndis"
            ):
                return queryset.filter(
                    Q(is_ndis_eligible=True) | Q(category_type="general")
                )

        return queryset


class ServiceCategoryManagementViewSet(ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [CanManageServiceCategories]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceCategoryFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "display_order", "created_at"]
    ordering = ["display_order", "name"]


class NDISServiceCodeViewSet(ReadOnlyModelViewSet):
    queryset = NDISServiceCode.objects.current()
    serializer_class = NDISServiceCodeSerializer
    permission_classes = [CanViewNDISServiceCodes]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["code", "name", "standard_rate"]
    ordering = ["code"]

    def get_queryset(self):
        queryset = super().get_queryset()

        unit_type = self.request.query_params.get("unit_type")
        if unit_type:
            queryset = queryset.filter(unit_type=unit_type)

        min_rate = self.request.query_params.get("min_rate")
        if min_rate:
            queryset = queryset.filter(standard_rate__gte=min_rate)

        max_rate = self.request.query_params.get("max_rate")
        if max_rate:
            queryset = queryset.filter(standard_rate__lte=max_rate)

        return queryset


class NDISServiceCodeManagementViewSet(ModelViewSet):
    queryset = NDISServiceCode.objects.all()
    serializer_class = NDISServiceCodeSerializer
    permission_classes = [CanManageNDISServiceCodes]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["code", "name", "description"]
    ordering_fields = ["code", "name", "standard_rate", "effective_from"]
    ordering = ["code"]


class ServiceAreaViewSet(ReadOnlyModelViewSet):
    queryset = ServiceArea.objects.active()
    permission_classes = [CanViewServiceAreas]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceAreaFilter
    search_fields = ["suburb", "postcode"]
    ordering_fields = ["suburb", "postcode", "state", "priority_level"]
    ordering = ["state", "suburb"]

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceAreaListSerializer
        return ServiceAreaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        state = self.request.query_params.get("state")
        if state:
            queryset = queryset.filter(state=state)

        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority_level__gte=priority)

        return queryset


class ServiceAreaManagementViewSet(ModelViewSet):
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer
    permission_classes = [CanManageServiceAreas]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceAreaFilter
    search_fields = ["suburb", "postcode"]
    ordering_fields = ["suburb", "postcode", "state", "priority_level", "created_at"]
    ordering = ["state", "suburb"]


class ServiceViewSet(ReadOnlyModelViewSet):
    queryset = Service.objects.active()
    permission_classes = [CanViewServices, NDISCompliancePermission]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceFilter
    search_fields = ["name", "description", "short_description"]
    ordering_fields = [
        "name",
        "base_price",
        "estimated_duration",
        "display_order",
        "created_at",
    ]
    ordering = ["display_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceListSerializer
        return ServiceDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            if (
                self.request.user.user_type == "client"
                and self.request.user.client_type == "ndis"
            ):
                queryset = queryset.filter(
                    Q(is_ndis_eligible=True) | Q(is_ndis_eligible=False)
                )
            elif self.request.user.user_type == "client":
                queryset = queryset.filter(is_ndis_eligible=False)
        else:
            queryset = queryset.filter(is_ndis_eligible=False)

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)

        service_type = self.request.query_params.get("service_type")
        if service_type:
            queryset = queryset.filter(service_type=service_type)

        postcode = self.request.query_params.get("postcode")
        if postcode:
            queryset = queryset.filter(
                service_areas__postcode=postcode, service_areas__is_active=True
            ).distinct()

        featured = self.request.query_params.get("featured")
        if featured and featured.lower() == "true":
            queryset = queryset.filter(is_featured=True)

        requires_quote = self.request.query_params.get("requires_quote")
        if requires_quote is not None:
            queryset = queryset.filter(requires_quote=requires_quote.lower() == "true")

        return queryset


class ServiceManagementViewSet(ModelViewSet):
    queryset = Service.objects.all()
    permission_classes = [CanManageServices]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ServiceFilter
    search_fields = ["name", "description", "short_description"]
    ordering_fields = [
        "name",
        "base_price",
        "estimated_duration",
        "display_order",
        "created_at",
    ]
    ordering = ["display_order", "name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ServiceCreateUpdateSerializer
        elif self.action == "list":
            return ServiceListSerializer
        return ServiceDetailSerializer


class ServiceSearchView(APIView):
    permission_classes = [CanViewServices]

    def get(self, request):
        serializer = ServiceSearchSerializer(data=request.query_params)
        if serializer.is_valid():
            queryset = Service.objects.active()

            query = serializer.validated_data.get("query")
            if query:
                queryset = queryset.search(query)

            category = serializer.validated_data.get("category")
            if category:
                queryset = queryset.by_category(category)

            service_type = serializer.validated_data.get("service_type")
            if service_type:
                queryset = queryset.by_type(service_type)

            postcode = serializer.validated_data.get("postcode")
            if postcode:
                queryset = queryset.available_in_area(postcode)

            min_price = serializer.validated_data.get("min_price")
            max_price = serializer.validated_data.get("max_price")
            if min_price or max_price:
                queryset = queryset.by_price_range(min_price, max_price)

            is_ndis_eligible = serializer.validated_data.get("is_ndis_eligible")
            if is_ndis_eligible is not None:
                if is_ndis_eligible:
                    queryset = queryset.ndis_eligible()
                else:
                    queryset = queryset.general_services()

            requires_quote = serializer.validated_data.get("requires_quote")
            if requires_quote is not None:
                if requires_quote:
                    queryset = queryset.requires_quote()
                else:
                    queryset = queryset.instant_booking()

            is_featured = serializer.validated_data.get("is_featured")
            if is_featured:
                queryset = queryset.featured()

            if request.user.is_authenticated:
                if (
                    request.user.user_type == "client"
                    and request.user.client_type == "ndis"
                ):
                    queryset = queryset.filter(
                        Q(is_ndis_eligible=True) | Q(is_ndis_eligible=False)
                    )
                elif request.user.user_type == "client":
                    queryset = queryset.filter(is_ndis_eligible=False)
            else:
                queryset = queryset.filter(is_ndis_eligible=False)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = ServiceListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = ServiceListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceQuoteRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated, ServiceQuotePermission]

    def post(self, request):
        serializer = ServiceQuoteRequestSerializer(data=request.data)
        if serializer.is_valid():
            service_id = serializer.validated_data["service_id"]
            service = get_object_or_404(Service, id=service_id, is_active=True)

            self.check_object_permissions(request, service)

            quote_data = calculate_service_quote(
                service=service, user=request.user, **serializer.validated_data
            )

            return Response(
                {
                    "message": "Quote calculated successfully",
                    "service": ServiceListSerializer(service).data,
                    "quote": quote_data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceAvailabilityView(APIView):
    permission_classes = [CanAccessServiceAvailability]

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id, is_active=True)
        self.check_object_permissions(request, service)

        date = request.query_params.get("date")
        if date:
            try:
                date = timezone.datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        available_slots = get_available_time_slots(service, date)

        return Response(
            {
                "service": ServiceListSerializer(service).data,
                "date": date,
                "available_slots": available_slots,
            },
            status=status.HTTP_200_OK,
        )


class ServiceAddOnViewSet(ReadOnlyModelViewSet):
    queryset = ServiceAddOn.objects.filter(is_active=True)
    serializer_class = ServiceAddOnSerializer
    permission_classes = [CanAccessServiceAddOns]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "addon_type"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()

        service_id = self.request.query_params.get("service_id")
        if service_id:
            queryset = queryset.filter(services__id=service_id)

        addon_type = self.request.query_params.get("addon_type")
        if addon_type:
            queryset = queryset.filter(addon_type=addon_type)

        optional = self.request.query_params.get("optional")
        if optional is not None:
            queryset = queryset.filter(is_optional=optional.lower() == "true")

        return queryset


class ServiceAddOnManagementViewSet(ModelViewSet):
    queryset = ServiceAddOn.objects.all()
    serializer_class = ServiceAddOnSerializer
    permission_classes = [CanManageServiceAddOns]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "addon_type", "created_at"]
    ordering = ["name"]


class ServicePricingViewSet(ReadOnlyModelViewSet):
    queryset = ServicePricing.objects.current()
    serializer_class = ServicePricingSerializer
    permission_classes = [CanViewServicePricing]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["service__name", "description"]
    ordering_fields = ["service__name", "tier", "price"]
    ordering = ["service__name", "tier"]

    def get_queryset(self):
        queryset = super().get_queryset()

        service_id = self.request.query_params.get("service_id")
        if service_id:
            queryset = queryset.filter(service_id=service_id)

        tier = self.request.query_params.get("tier")
        if tier:
            queryset = queryset.filter(tier=tier)

        return queryset


class ServicePricingManagementViewSet(ModelViewSet):
    queryset = ServicePricing.objects.all()
    serializer_class = ServicePricingSerializer
    permission_classes = [CanManageServicePricing]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["service__name", "description"]
    ordering_fields = ["service__name", "tier", "price", "effective_from"]
    ordering = ["service__name", "tier"]


class ServiceStatsView(APIView):
    permission_classes = [CanAccessServiceReports]

    def get(self, request):
        stats = Service.objects.calculate_service_metrics()

        category_stats = (
            ServiceCategory.objects.active()
            .annotate(
                service_count=Count("services", filter=Q(services__is_active=True))
            )
            .values("name", "service_count")
        )

        area_stats = (
            ServiceArea.objects.active()
            .values("state")
            .annotate(
                area_count=Count("id"),
                service_count=Count("services", filter=Q(services__is_active=True)),
            )
            .order_by("state")
        )

        ndis_stats = {
            "total_ndis_codes": NDISServiceCode.objects.current().count(),
            "ndis_services": Service.objects.ndis_eligible().count(),
            "ndis_categories": ServiceCategory.objects.filter(
                is_ndis_eligible=True
            ).count(),
        }

        response_data = {
            "service_stats": stats,
            "category_stats": list(category_stats),
            "area_stats": list(area_stats),
            "ndis_stats": ndis_stats,
            "generated_at": timezone.now(),
        }

        serializer = ServiceStatsSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BulkServiceActionView(APIView):
    permission_classes = [CanBulkManageServices]

    def post(self, request):
        serializer = BulkServiceActionSerializer(data=request.data)
        if serializer.is_valid():
            service_ids = serializer.validated_data["service_ids"]
            action = serializer.validated_data["action"]

            services = Service.objects.filter(id__in=service_ids)

            if action == "activate":
                updated = services.update(is_active=True)
            elif action == "deactivate":
                updated = services.update(is_active=False)
            elif action == "feature":
                updated = services.update(is_featured=True)
            elif action == "unfeature":
                updated = services.update(is_featured=False)
            elif action == "delete":
                updated = services.count()
                services.delete()

            return Response(
                {
                    "message": f"Successfully {action}d {updated} services",
                    "affected_services": updated,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeaturedServicesView(APIView):
    permission_classes = [CanViewServices]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))

        queryset = Service.objects.featured()

        if request.user.is_authenticated:
            if (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            ):
                queryset = queryset.filter(
                    Q(is_ndis_eligible=True) | Q(is_ndis_eligible=False)
                )
            elif request.user.user_type == "client":
                queryset = queryset.filter(is_ndis_eligible=False)
        else:
            queryset = queryset.filter(is_ndis_eligible=False)

        services = queryset[:limit]
        serializer = ServiceListSerializer(services, many=True)

        return Response(
            {"featured_services": serializer.data, "total_count": queryset.count()},
            status=status.HTTP_200_OK,
        )


class RecommendedServicesView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewServices]

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))

        recommended_services = Service.objects.recommended_for_user(request.user)[
            :limit
        ]
        serializer = ServiceListSerializer(recommended_services, many=True)

        return Response(
            {
                "recommended_services": serializer.data,
                "user_type": request.user.user_type,
                "client_type": getattr(request.user, "client_type", None),
            },
            status=status.HTTP_200_OK,
        )


class ServicesByLocationView(APIView):
    permission_classes = [CanViewServices]

    def get(self, request, postcode):
        try:
            from .validators import validate_postcode

            validate_postcode(postcode)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        service_type = request.query_params.get("service_type")

        services = Service.objects.services_by_location_and_type(postcode, service_type)

        if request.user.is_authenticated:
            if (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            ):
                services = services.filter(
                    Q(is_ndis_eligible=True) | Q(is_ndis_eligible=False)
                )
            elif request.user.user_type == "client":
                services = services.filter(is_ndis_eligible=False)
        else:
            services = services.filter(is_ndis_eligible=False)

        serializer = ServiceListSerializer(services, many=True)

        area = ServiceArea.objects.filter(postcode=postcode, is_active=True).first()

        return Response(
            {
                "postcode": postcode,
                "area_info": ServiceAreaSerializer(area).data if area else None,
                "services": serializer.data,
                "total_count": services.count(),
            },
            status=status.HTTP_200_OK,
        )


class ServiceCategoriesWithServicesView(APIView):
    permission_classes = [CanViewServiceCategories]

    def get(self, request):
        categories = ServiceCategory.objects.with_services()

        category_data = []
        for category in categories:
            services = category.services.filter(is_active=True)

            if request.user.is_authenticated:
                if (
                    request.user.user_type == "client"
                    and request.user.client_type == "ndis"
                ):
                    services = services.filter(
                        Q(is_ndis_eligible=True) | Q(is_ndis_eligible=False)
                    )
                elif request.user.user_type == "client":
                    services = services.filter(is_ndis_eligible=False)
            else:
                services = services.filter(is_ndis_eligible=False)

            if services.exists():
                category_data.append(
                    {
                        "category": ServiceCategorySerializer(category).data,
                        "services": ServiceListSerializer(services[:5], many=True).data,
                        "total_services": services.count(),
                    }
                )

        return Response(
            {"categories_with_services": category_data}, status=status.HTTP_200_OK
        )


@api_view(["GET"])
@permission_classes([CanViewServices])
def service_types_list(request):
    service_types = (
        Service.objects.active().values_list("service_type", flat=True).distinct()
    )

    type_data = []
    for service_type in service_types:
        count = Service.objects.active().filter(service_type=service_type).count()
        type_data.append(
            {
                "type": service_type,
                "display_name": dict(Service.SERVICE_TYPES).get(
                    service_type, service_type
                ),
                "count": count,
            }
        )

    return Response({"service_types": type_data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([CanViewServiceAreas])
def service_areas_by_state(request):
    state = request.query_params.get("state")

    queryset = ServiceArea.objects.active()
    if state:
        queryset = queryset.filter(state=state)

    areas_by_state = {}
    for area in queryset:
        if area.state not in areas_by_state:
            areas_by_state[area.state] = []
        areas_by_state[area.state].append(ServiceAreaListSerializer(area).data)

    return Response({"areas_by_state": areas_by_state}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, CanManageServices])
def duplicate_service(request, service_id):
    try:
        original_service = Service.objects.get(id=service_id)

        new_service = Service.objects.create(
            name=f"{original_service.name} (Copy)",
            slug=f"{original_service.slug}-copy",
            category=original_service.category,
            service_type=original_service.service_type,
            description=original_service.description,
            short_description=original_service.short_description,
            pricing_type=original_service.pricing_type,
            base_price=original_service.base_price,
            hourly_rate=original_service.hourly_rate,
            minimum_charge=original_service.minimum_charge,
            estimated_duration=original_service.estimated_duration,
            duration_unit=original_service.duration_unit,
            is_active=False,
            is_featured=False,
            is_ndis_eligible=original_service.is_ndis_eligible,
            requires_quote=original_service.requires_quote,
            ndis_service_code=original_service.ndis_service_code,
            minimum_rooms=original_service.minimum_rooms,
            maximum_rooms=original_service.maximum_rooms,
            equipment_required=original_service.equipment_required,
            special_requirements=original_service.special_requirements,
        )

        new_service.service_areas.set(original_service.service_areas.all())
        new_service.addons.set(original_service.addons.all())

        return Response(
            {
                "message": "Service duplicated successfully",
                "original_service": ServiceListSerializer(original_service).data,
                "new_service": ServiceDetailSerializer(new_service).data,
            },
            status=status.HTTP_201_CREATED,
        )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response(
        {
            "status": "healthy",
            "timestamp": timezone.now(),
            "service": "services",
            "stats": {
                "total_services": Service.objects.active().count(),
                "total_categories": ServiceCategory.objects.active().count(),
                "total_areas": ServiceArea.objects.active().count(),
                "ndis_services": Service.objects.ndis_eligible().count(),
            },
        },
        status=status.HTTP_200_OK,
    )
