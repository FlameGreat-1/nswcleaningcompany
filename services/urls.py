from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet, ServiceManagementViewSet, ServiceCategoryViewSet,
    ServiceCategoryManagementViewSet, ServiceAreaViewSet, ServiceAreaManagementViewSet,
    NDISServiceCodeViewSet, NDISServiceCodeManagementViewSet, ServiceAddOnViewSet,
    ServiceAddOnManagementViewSet, ServicePricingViewSet, ServicePricingManagementViewSet,
    ServiceSearchView, ServiceQuoteRequestView, ServiceAvailabilityView,
    ServiceStatsView, BulkServiceActionView, FeaturedServicesView,
    RecommendedServicesView, ServicesByLocationView, ServiceCategoriesWithServicesView,
    service_types_list, service_areas_by_state, duplicate_service, health_check
)

app_name = 'services'

public_router = DefaultRouter()
public_router.register(r'services', ServiceViewSet, basename='service')
public_router.register(r'categories', ServiceCategoryViewSet, basename='category')
public_router.register(r'areas', ServiceAreaViewSet, basename='area')
public_router.register(r'ndis-codes', NDISServiceCodeViewSet, basename='ndis-code')
public_router.register(r'addons', ServiceAddOnViewSet, basename='addon')
public_router.register(r'pricing', ServicePricingViewSet, basename='pricing')

management_router = DefaultRouter()
management_router.register(r'services', ServiceManagementViewSet, basename='service-management')
management_router.register(r'categories', ServiceCategoryManagementViewSet, basename='category-management')
management_router.register(r'areas', ServiceAreaManagementViewSet, basename='area-management')
management_router.register(r'ndis-codes', NDISServiceCodeManagementViewSet, basename='ndis-code-management')
management_router.register(r'addons', ServiceAddOnManagementViewSet, basename='addon-management')
management_router.register(r'pricing', ServicePricingManagementViewSet, basename='pricing-management')

urlpatterns = [
    path('health/', health_check, name='health_check'),
    
    path('search/', ServiceSearchView.as_view(), name='service_search'),
    path('quote/request/', ServiceQuoteRequestView.as_view(), name='quote_request'),
    path('featured/', FeaturedServicesView.as_view(), name='featured_services'),
    path('recommended/', RecommendedServicesView.as_view(), name='recommended_services'),
    path('types/', service_types_list, name='service_types'),
    path('categories/with-services/', ServiceCategoriesWithServicesView.as_view(), name='categories_with_services'),
    path('areas/by-state/', service_areas_by_state, name='areas_by_state'),
    path('location/<str:postcode>/', ServicesByLocationView.as_view(), name='services_by_location'),
    
    path('<int:service_id>/availability/', ServiceAvailabilityView.as_view(), name='service_availability'),
    
    path('admin/stats/', ServiceStatsView.as_view(), name='service_stats'),
    path('admin/bulk-action/', BulkServiceActionView.as_view(), name='bulk_service_action'),
    path('admin/<int:service_id>/duplicate/', duplicate_service, name='duplicate_service'),
    
    path('admin/', include(management_router.urls)),
    path('', include(public_router.urls)),
]
