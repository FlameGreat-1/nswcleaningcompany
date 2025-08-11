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
    # Quote CRUD operations
    path(
        "", QuoteViewSet.as_view({"get": "list", "post": "create"}), name="quote-list"
    ),
    path(
        "<int:pk>/",
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
    # Quote custom actions
    path(
        "<int:pk>/submit/",
        QuoteViewSet.as_view({"post": "submit"}),
        name="quote-submit",
    ),
    path(
        "<int:pk>/approve/",
        QuoteViewSet.as_view({"post": "approve"}),
        name="quote-approve",
    ),
    path(
        "<int:pk>/reject/",
        QuoteViewSet.as_view({"post": "reject"}),
        name="quote-reject",
    ),
    path(
        "<int:pk>/cancel/",
        QuoteViewSet.as_view({"post": "cancel"}),
        name="quote-cancel",
    ),
    path(
        "<int:pk>/assign/",
        QuoteViewSet.as_view({"post": "assign"}),
        name="quote-assign",
    ),
    path(
        "<int:pk>/duplicate/",
        QuoteViewSet.as_view({"post": "duplicate"}),
        name="quote-duplicate",
    ),
    path(
        "<int:pk>/convert/",
        QuoteViewSet.as_view({"post": "convert"}),
        name="quote-convert",
    ),
    path("<int:pk>/pdf/", QuoteViewSet.as_view({"get": "pdf"}), name="quote-pdf"),
    path(
        "<int:pk>/recalculate-pricing/",
        QuoteViewSet.as_view({"post": "recalculate_pricing"}),
        name="quote-recalculate",
    ),
    path(
        "<int:pk>/update-status/",
        QuoteViewSet.as_view({"patch": "update_status"}),
        name="quote-update-status",
    ),
    # Quote list actions
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
    # Quote Templates - Full CRUD + Custom Actions
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
        "templates/<int:pk>/duplicate/",
        QuoteTemplateViewSet.as_view({"post": "duplicate"}),
        name="template-duplicate",
    ),
    path(
        "templates/<int:pk>/activate/",
        QuoteTemplateViewSet.as_view({"post": "activate"}),
        name="template-activate",
    ),
    path(
        "templates/<int:pk>/deactivate/",
        QuoteTemplateViewSet.as_view({"post": "deactivate"}),
        name="template-deactivate",
    ),
    path(
        "templates/active/",
        QuoteTemplateViewSet.as_view({"get": "active"}),
        name="template-active",
    ),
    path(
        "templates/by-service/<int:service_id>/",
        QuoteTemplateViewSet.as_view({"get": "by_service"}),
        name="template-by-service",
    ),
    # Quote Items - Full CRUD + Custom Actions
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
    path(
        "items/bulk-update/",
        QuoteItemViewSet.as_view({"post": "bulk_update"}),
        name="item-bulk-update",
    ),
    path(
        "items/bulk-delete/",
        QuoteItemViewSet.as_view({"post": "bulk_delete"}),
        name="item-bulk-delete",
    ),
    # Quote Attachments - Full CRUD + File Operations
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
    path(
        "attachments/bulk-upload/",
        QuoteAttachmentViewSet.as_view({"post": "bulk_upload"}),
        name="attachment-bulk-upload",
    ),
    # Quote Revisions - Full CRUD + Version Control
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
    path(
        "revisions/<int:pk>/restore/",
        QuoteRevisionViewSet.as_view({"post": "restore"}),
        name="revision-restore",
    ),
    path(
        "revisions/compare/",
        QuoteRevisionViewSet.as_view({"post": "compare"}),
        name="revision-compare",
    ),
    # Utility and Calculator Views
    path("calculator/", QuoteCalculatorView.as_view(), name="quote-calculator"),
    path("analytics/", QuoteAnalyticsView.as_view(), name="quote-analytics"),
    path("reports/", QuoteReportView.as_view(), name="quote-reports"),
    path("export/", QuoteExportView.as_view(), name="quote-export"),
    path("notifications/", QuoteNotificationView.as_view(), name="quote-notifications"),
    # Filtered Quote Views
    path("my-quotes/", MyQuotesView.as_view(), name="my-quotes"),
    path("pending/", PendingQuotesView.as_view(), name="pending-quotes"),
    path("expiring/", ExpiringQuotesView.as_view(), name="expiring-quotes"),
    path("urgent/", UrgentQuotesView.as_view(), name="urgent-quotes"),
    path("ndis/", NDISQuotesView.as_view(), name="ndis-quotes"),
    path("high-value/", HighValueQuotesView.as_view(), name="high-value-quotes"),
    # Relationship-based Views
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
    # Analytics and Reporting Views
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
