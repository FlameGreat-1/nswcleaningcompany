from django.urls import path
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

urlpatterns = [
    # Custom views FIRST (to avoid conflicts)
    path("my-quotes/", QuoteViewSet.as_view({"get": "list"}), name="my-quotes"),
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
    # Main quote CRUD operations
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
    # Quote actions
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
    # Templates
    path(
        "templates/",
        QuoteTemplateViewSet.as_view({"get": "list", "post": "create"}),
        name="template-list",
    ),
    path(
        "templates/<int:pk>/",
        QuoteTemplateViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="template-detail",
    ),
    path(
        "templates/<int:pk>/use-template/",
        QuoteTemplateViewSet.as_view({"post": "use_template"}),
        name="template-use",
    ),
    # Items
    path(
        "items/",
        QuoteItemViewSet.as_view({"get": "list", "post": "create"}),
        name="item-list",
    ),
    path(
        "items/<int:pk>/",
        QuoteItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="item-detail",
    ),
    # Attachments
    path(
        "attachments/",
        QuoteAttachmentViewSet.as_view({"get": "list", "post": "create"}),
        name="attachment-list",
    ),
    path(
        "attachments/<int:pk>/",
        QuoteAttachmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="attachment-detail",
    ),
    path(
        "attachments/<int:pk>/download/",
        QuoteAttachmentViewSet.as_view({"get": "download"}),
        name="attachment-download",
    ),
    # Revisions
    path(
        "revisions/",
        QuoteRevisionViewSet.as_view({"get": "list", "post": "create"}),
        name="revision-list",
    ),
    path(
        "revisions/<int:pk>/",
        QuoteRevisionViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="revision-detail",
    ),
]
