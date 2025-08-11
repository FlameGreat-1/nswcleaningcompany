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

# Create router ONLY for secondary ViewSets
router = DefaultRouter()
router.register(r"templates", QuoteTemplateViewSet, basename="template")
router.register(r"items", QuoteItemViewSet, basename="item")
router.register(r"attachments", QuoteAttachmentViewSet, basename="attachment")
router.register(r"revisions", QuoteRevisionViewSet, basename="revision")

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
    # Main QuoteViewSet URLs - Manual configuration
    path(
        "", QuoteViewSet.as_view({"get": "list", "post": "create"}), name="quote-list"
    ),
    path(
        "<uuid:pk>/",
        QuoteViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="quote-detail",
    ),
    path(
        "<uuid:pk>/submit/",
        QuoteViewSet.as_view({"post": "submit"}),
        name="quote-submit",
    ),
    path(
        "<uuid:pk>/approve/",
        QuoteViewSet.as_view({"post": "approve"}),
        name="quote-approve",
    ),
    path(
        "<uuid:pk>/reject/",
        QuoteViewSet.as_view({"post": "reject"}),
        name="quote-reject",
    ),
    path(
        "<uuid:pk>/cancel/",
        QuoteViewSet.as_view({"post": "cancel"}),
        name="quote-cancel",
    ),
    path(
        "<uuid:pk>/assign/",
        QuoteViewSet.as_view({"post": "assign"}),
        name="quote-assign",
    ),
    path(
        "<uuid:pk>/duplicate/",
        QuoteViewSet.as_view({"post": "duplicate"}),
        name="quote-duplicate",
    ),
    path(
        "<uuid:pk>/convert/",
        QuoteViewSet.as_view({"post": "convert"}),
        name="quote-convert",
    ),
    path("<uuid:pk>/pdf/", QuoteViewSet.as_view({"get": "pdf"}), name="quote-pdf"),
    path(
        "<uuid:pk>/recalculate-pricing/",
        QuoteViewSet.as_view({"post": "recalculate_pricing"}),
        name="quote-recalculate",
    ),
    path(
        "bulk-operations/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="quote-bulk-operations",
    ),
    path(
        "statistics/",
        QuoteViewSet.as_view({"get": "statistics"}),
        name="quote-statistics",
    ),
    path(
        "dashboard/", QuoteViewSet.as_view({"get": "dashboard"}), name="quote-dashboard"
    ),
    path("search/", QuoteViewSet.as_view({"post": "search"}), name="quote-search"),
    # Include router URLs for other ViewSets
    path("", include(router.urls)),
]
