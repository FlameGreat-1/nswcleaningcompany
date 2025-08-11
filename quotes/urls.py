from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuoteViewSet,
    QuoteItemViewSet,
    QuoteAttachmentViewSet,
    QuoteRevisionViewSet,
    QuoteTemplateViewSet,
    QuoteCalculatorView,
    QuoteAnalyticsView,
    QuoteReportView,
    QuoteExportView,
    QuoteNotificationView,
    MyQuotesView,
    PendingQuotesView,
    ExpiringQuotesView,
    UrgentQuotesView,
    NDISQuotesView,
    HighValueQuotesView,
    QuotesByServiceView,
    QuotesByClientView,
    QuoteConversionRateView,
    QuoteStatusDistributionView,
    QuoteMonthlyTrendsView,
)

app_name = "quotes"

# Create router for ViewSets
router = DefaultRouter()
router.register(r'main', QuoteViewSet, basename='quote')  
router.register(r'templates', QuoteTemplateViewSet, basename='template')
router.register(r'items', QuoteItemViewSet, basename='item')
router.register(r'attachments', QuoteAttachmentViewSet, basename='attachment')
router.register(r'revisions', QuoteRevisionViewSet, basename='revision')

urlpatterns = [
    # Custom list views FIRST
    path("my-quotes/", MyQuotesView.as_view(), name="my-quotes"),
    path("pending/", PendingQuotesView.as_view(), name="pending-quotes"),
    path("expiring/", ExpiringQuotesView.as_view(), name="expiring-quotes"),
    path("urgent/", UrgentQuotesView.as_view(), name="urgent-quotes"),
    path("ndis/", NDISQuotesView.as_view(), name="ndis-quotes"),
    path("high-value/", HighValueQuotesView.as_view(), name="high-value-quotes"),
    path("calculator/", QuoteCalculatorView.as_view(), name="quote-calculator"),
    path("analytics/", QuoteAnalyticsView.as_view(), name="quote-analytics"),
    path("reports/", QuoteReportView.as_view(), name="quote-reports"),
    path("export/", QuoteExportView.as_view(), name="quote-export"),
    path("notifications/", QuoteNotificationView.as_view(), name="quote-notifications"),
    path("by-service/<int:service_id>/", QuotesByServiceView.as_view(), name="quotes-by-service"),
    path("by-client/<int:client_id>/", QuotesByClientView.as_view(), name="quotes-by-client"),
    path("conversion-rate/", QuoteConversionRateView.as_view(), name="quote-conversion-rate"),
    path("status-distribution/", QuoteStatusDistributionView.as_view(), name="quote-status-distribution"),
    path("monthly-trends/", QuoteMonthlyTrendsView.as_view(), name="quote-monthly-trends"),
    
    # Main CRUD operations (list, create, retrieve, update, delete)
    path("", QuoteViewSet.as_view({"get": "list", "post": "create"}), name="quote-list"),
    path("<uuid:pk>/", QuoteViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}), name="quote-detail"),
    
    # Router URLs for other ViewSets
    path('', include(router.urls)),
]
