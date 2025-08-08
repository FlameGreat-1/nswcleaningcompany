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

# Router automatically handles all CRUD operations and custom actions
router = DefaultRouter()
router.register(r"quotes", QuoteViewSet, basename="quote")
router.register(r"items", QuoteItemViewSet, basename="quoteitem")
router.register(r"attachments", QuoteAttachmentViewSet, basename="quoteattachment")
router.register(r"revisions", QuoteRevisionViewSet, basename="quoterevision")
router.register(r"templates", QuoteTemplateViewSet, basename="quotetemplate")

urlpatterns = [
    # Router URLs (handles all ViewSet CRUD + custom actions automatically)
    # This includes: /quotes/, /quotes/{id}/, /quotes/{id}/submit/, /quotes/{id}/approve/, etc.
    path("", include(router.urls)),
    # Public calculator (no auth required)
    path("calculator/", QuoteCalculatorView.as_view(), name="quote-calculator"),
    # Analytics and reporting
    path("analytics/", QuoteAnalyticsView.as_view(), name="quote-analytics"),
    path("reports/", QuoteReportView.as_view(), name="quote-reports"),
    path("export/", QuoteExportView.as_view(), name="quote-export"),
    path("notifications/", QuoteNotificationView.as_view(), name="quote-notifications"),
    # Filtered quote lists
    path("my-quotes/", MyQuotesView.as_view(), name="my-quotes"),
    path("pending/", PendingQuotesView.as_view(), name="pending-quotes"),
    path("expiring/", ExpiringQuotesView.as_view(), name="expiring-quotes"),
    path("urgent/", UrgentQuotesView.as_view(), name="urgent-quotes"),
    path("ndis/", NDISQuotesView.as_view(), name="ndis-quotes"),
    path("high-value/", HighValueQuotesView.as_view(), name="high-value-quotes"),
    # Filtered by relationships
    path(
        "by-service/<int:service_id>/",
        QuotesByServiceView.as_view(),
        name="quotes-by-service",
    ),
    path(
        "by-client/<int:client_id>/",
        QuotesByClientView.as_view(),
        name="quotes-by-client",
    ),
    # Analytics endpoints
    path(
        "conversion-rate/",
        QuoteConversionRateView.as_view(),
        name="quote-conversion-rate",
    ),
    path(
        "status-distribution/",
        QuoteStatusDistributionView.as_view(),
        name="quote-status-distribution",
    ),
    path(
        "monthly-trends/", QuoteMonthlyTrendsView.as_view(), name="quote-monthly-trends"
    ),
]
