from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
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

router = DefaultRouter()
router.register(r"quotes", QuoteViewSet, basename="quote")
router.register(r"quote-items", QuoteItemViewSet, basename="quoteitem")
router.register(
    r"quote-attachments", QuoteAttachmentViewSet, basename="quoteattachment"
)
router.register(r"quote-revisions", QuoteRevisionViewSet, basename="quoterevision")
router.register(r"quote-templates", QuoteTemplateViewSet, basename="quotetemplate")

urlpatterns = [
    path("", include(router.urls)),
    path("calculator/", QuoteCalculatorView.as_view(), name="quote-calculator"),
    path(
        "quotes/<uuid:pk>/submit/",
        QuoteViewSet.as_view({"post": "submit"}),
        name="quote-submit",
    ),
    path(
        "quotes/<uuid:pk>/approve/",
        QuoteViewSet.as_view({"post": "approve"}),
        name="quote-approve",
    ),
    path(
        "quotes/<uuid:pk>/reject/",
        QuoteViewSet.as_view({"post": "reject"}),
        name="quote-reject",
    ),
    path(
        "quotes/<uuid:pk>/cancel/",
        QuoteViewSet.as_view({"post": "cancel"}),
        name="quote-cancel",
    ),
    path(
        "quotes/<uuid:pk>/assign/",
        QuoteViewSet.as_view({"post": "assign"}),
        name="quote-assign",
    ),
    path(
        "quotes/<uuid:pk>/duplicate/",
        QuoteViewSet.as_view({"post": "duplicate"}),
        name="quote-duplicate",
    ),
    path(
        "quotes/<uuid:pk>/convert/",
        QuoteViewSet.as_view({"post": "convert"}),
        name="quote-convert",
    ),
    path(
        "quotes/<uuid:pk>/pdf/", QuoteViewSet.as_view({"get": "pdf"}), name="quote-pdf"
    ),
    path(
        "quotes/<uuid:pk>/recalculate-pricing/",
        QuoteViewSet.as_view({"post": "recalculate_pricing"}),
        name="quote-recalculate-pricing",
    ),
    path(
        "quotes/bulk-operations/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="quote-bulk-operations",
    ),
    path(
        "quotes/statistics/",
        QuoteViewSet.as_view({"get": "statistics"}),
        name="quote-statistics",
    ),
    path(
        "quotes/dashboard/",
        QuoteViewSet.as_view({"get": "dashboard"}),
        name="quote-dashboard",
    ),
    path(
        "quotes/search/", QuoteViewSet.as_view({"post": "search"}), name="quote-search"
    ),
    path(
        "quote-attachments/<int:pk>/download/",
        QuoteAttachmentViewSet.as_view({"get": "download"}),
        name="quote-attachment-download",
    ),
    path(
        "quote-templates/<int:pk>/use-template/",
        QuoteTemplateViewSet.as_view({"post": "use_template"}),
        name="quote-template-use",
    ),
    path("analytics/", QuoteAnalyticsView.as_view(), name="quote-analytics"),
    path("reports/", QuoteReportView.as_view(), name="quote-reports"),
    path("export/", QuoteExportView.as_view(), name="quote-export"),
    path("notifications/", QuoteNotificationView.as_view(), name="quote-notifications"),
    path("my-quotes/", MyQuotesView.as_view(), name="my-quotes"),
    path("pending/", PendingQuotesView.as_view(), name="pending-quotes"),
    path("expiring/", ExpiringQuotesView.as_view(), name="expiring-quotes"),
    path("urgent/", UrgentQuotesView.as_view(), name="urgent-quotes"),
    path("ndis/", NDISQuotesView.as_view(), name="ndis-quotes"),
    path("high-value/", HighValueQuotesView.as_view(), name="high-value-quotes"),
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
        "quotes/<uuid:quote_id>/items/",
        QuoteItemViewSet.as_view({"get": "list", "post": "create"}),
        name="quote-items-list",
    ),
    path(
        "quotes/<uuid:quote_id>/items/<int:pk>/",
        QuoteItemViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="quote-item-detail",
    ),
    path(
        "quotes/<uuid:quote_id>/attachments/",
        QuoteAttachmentViewSet.as_view({"get": "list", "post": "create"}),
        name="quote-attachments-list",
    ),
    path(
        "quotes/<uuid:quote_id>/attachments/<int:pk>/",
        QuoteAttachmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="quote-attachment-detail",
    ),
    path(
        "quotes/<uuid:quote_id>/revisions/",
        QuoteRevisionViewSet.as_view({"get": "list", "post": "create"}),
        name="quote-revisions-list",
    ),
    path(
        "quotes/<uuid:quote_id>/revisions/<int:pk>/",
        QuoteRevisionViewSet.as_view({"get": "retrieve"}),
        name="quote-revision-detail",
    ),
]

api_v1_patterns = [
    path("v1/quotes/", include(urlpatterns)),
]

public_patterns = [
    path("calculator/", QuoteCalculatorView.as_view(), name="public-quote-calculator"),
]

admin_patterns = [
    path(
        "admin/quotes/analytics/",
        QuoteAnalyticsView.as_view(),
        name="admin-quote-analytics",
    ),
    path(
        "admin/quotes/reports/", QuoteReportView.as_view(), name="admin-quote-reports"
    ),
    path("admin/quotes/export/", QuoteExportView.as_view(), name="admin-quote-export"),
    path(
        "admin/quotes/bulk-operations/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="admin-quote-bulk-operations",
    ),
    path(
        "admin/quotes/statistics/",
        QuoteViewSet.as_view({"get": "statistics"}),
        name="admin-quote-statistics",
    ),
    path(
        "admin/quotes/pending/",
        PendingQuotesView.as_view(),
        name="admin-pending-quotes",
    ),
    path(
        "admin/quotes/expiring/",
        ExpiringQuotesView.as_view(),
        name="admin-expiring-quotes",
    ),
    path(
        "admin/quotes/urgent/", UrgentQuotesView.as_view(), name="admin-urgent-quotes"
    ),
    path(
        "admin/quotes/high-value/",
        HighValueQuotesView.as_view(),
        name="admin-high-value-quotes",
    ),
    path(
        "admin/quotes/conversion-rate/",
        QuoteConversionRateView.as_view(),
        name="admin-quote-conversion-rate",
    ),
    path(
        "admin/quotes/status-distribution/",
        QuoteStatusDistributionView.as_view(),
        name="admin-quote-status-distribution",
    ),
    path(
        "admin/quotes/monthly-trends/",
        QuoteMonthlyTrendsView.as_view(),
        name="admin-quote-monthly-trends",
    ),
]

client_patterns = [
    path("client/quotes/", MyQuotesView.as_view(), name="client-my-quotes"),
    path(
        "client/quotes/<uuid:pk>/",
        QuoteViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update"}
        ),
        name="client-quote-detail",
    ),
    path(
        "client/quotes/<uuid:pk>/submit/",
        QuoteViewSet.as_view({"post": "submit"}),
        name="client-quote-submit",
    ),
    path(
        "client/quotes/<uuid:pk>/cancel/",
        QuoteViewSet.as_view({"post": "cancel"}),
        name="client-quote-cancel",
    ),
    path(
        "client/quotes/<uuid:pk>/duplicate/",
        QuoteViewSet.as_view({"post": "duplicate"}),
        name="client-quote-duplicate",
    ),
    path(
        "client/quotes/<uuid:pk>/pdf/",
        QuoteViewSet.as_view({"get": "pdf"}),
        name="client-quote-pdf",
    ),
    path(
        "client/quotes/create/",
        QuoteViewSet.as_view({"post": "create"}),
        name="client-quote-create",
    ),
]

staff_patterns = [
    path(
        "staff/quotes/", QuoteViewSet.as_view({"get": "list"}), name="staff-quotes-list"
    ),
    path(
        "staff/quotes/<uuid:pk>/",
        QuoteViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="staff-quote-detail",
    ),
    path(
        "staff/quotes/<uuid:pk>/approve/",
        QuoteViewSet.as_view({"post": "approve"}),
        name="staff-quote-approve",
    ),
    path(
        "staff/quotes/<uuid:pk>/reject/",
        QuoteViewSet.as_view({"post": "reject"}),
        name="staff-quote-reject",
    ),
    path(
        "staff/quotes/<uuid:pk>/assign/",
        QuoteViewSet.as_view({"post": "assign"}),
        name="staff-quote-assign",
    ),
    path(
        "staff/quotes/<uuid:pk>/convert/",
        QuoteViewSet.as_view({"post": "convert"}),
        name="staff-quote-convert",
    ),
    path(
        "staff/quotes/pending/",
        PendingQuotesView.as_view(),
        name="staff-pending-quotes",
    ),
    path(
        "staff/quotes/expiring/",
        ExpiringQuotesView.as_view(),
        name="staff-expiring-quotes",
    ),
    path(
        "staff/quotes/urgent/", UrgentQuotesView.as_view(), name="staff-urgent-quotes"
    ),
    path("staff/quotes/ndis/", NDISQuotesView.as_view(), name="staff-ndis-quotes"),
    path(
        "staff/quotes/dashboard/",
        QuoteViewSet.as_view({"get": "dashboard"}),
        name="staff-quote-dashboard",
    ),
]

mobile_patterns = [
    path(
        "mobile/quotes/calculator/",
        QuoteCalculatorView.as_view(),
        name="mobile-quote-calculator",
    ),
    path("mobile/quotes/my-quotes/", MyQuotesView.as_view(), name="mobile-my-quotes"),
    path(
        "mobile/quotes/<uuid:pk>/",
        QuoteViewSet.as_view({"get": "retrieve"}),
        name="mobile-quote-detail",
    ),
    path(
        "mobile/quotes/<uuid:pk>/submit/",
        QuoteViewSet.as_view({"post": "submit"}),
        name="mobile-quote-submit",
    ),
    path(
        "mobile/quotes/<uuid:pk>/attachments/",
        QuoteAttachmentViewSet.as_view({"get": "list", "post": "create"}),
        name="mobile-quote-attachments",
    ),
    path(
        "mobile/quotes/create/",
        QuoteViewSet.as_view({"post": "create"}),
        name="mobile-quote-create",
    ),
    path(
        "mobile/quotes/templates/",
        QuoteTemplateViewSet.as_view({"get": "list"}),
        name="mobile-quote-templates",
    ),
]

webhook_patterns = [
    path(
        "webhooks/quote-status-changed/",
        QuoteNotificationView.as_view(),
        name="webhook-quote-status-changed",
    ),
    path(
        "webhooks/quote-approved/",
        QuoteNotificationView.as_view(),
        name="webhook-quote-approved",
    ),
    path(
        "webhooks/quote-rejected/",
        QuoteNotificationView.as_view(),
        name="webhook-quote-rejected",
    ),
    path(
        "webhooks/quote-expired/",
        QuoteNotificationView.as_view(),
        name="webhook-quote-expired",
    ),
]

integration_patterns = [
    path(
        "integrations/accounting/quotes/",
        QuoteExportView.as_view(),
        name="integration-accounting-quotes",
    ),
    path(
        "integrations/crm/quotes/",
        QuoteExportView.as_view(),
        name="integration-crm-quotes",
    ),
    path(
        "integrations/calendar/quotes/",
        QuoteViewSet.as_view({"get": "list"}),
        name="integration-calendar-quotes",
    ),
]

ndis_patterns = [
    path("ndis/quotes/", NDISQuotesView.as_view(), name="ndis-quotes-list"),
    path(
        "ndis/quotes/<uuid:pk>/",
        QuoteViewSet.as_view({"get": "retrieve"}),
        name="ndis-quote-detail",
    ),
    path(
        "ndis/quotes/<uuid:pk>/approve/",
        QuoteViewSet.as_view({"post": "approve"}),
        name="ndis-quote-approve",
    ),
    path(
        "ndis/quotes/analytics/",
        QuoteAnalyticsView.as_view(),
        name="ndis-quote-analytics",
    ),
    path("ndis/quotes/reports/", QuoteReportView.as_view(), name="ndis-quote-reports"),
]

bulk_patterns = [
    path(
        "bulk/quotes/approve/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="bulk-quotes-approve",
    ),
    path(
        "bulk/quotes/reject/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="bulk-quotes-reject",
    ),
    path(
        "bulk/quotes/assign/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="bulk-quotes-assign",
    ),
    path(
        "bulk/quotes/export/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="bulk-quotes-export",
    ),
    path(
        "bulk/quotes/cancel/",
        QuoteViewSet.as_view({"post": "bulk_operations"}),
        name="bulk-quotes-cancel",
    ),
]

reporting_patterns = [
    path(
        "reports/quotes/summary/",
        QuoteReportView.as_view(),
        name="quote-summary-report",
    ),
    path(
        "reports/quotes/detailed/",
        QuoteReportView.as_view(),
        name="quote-detailed-report",
    ),
    path(
        "reports/quotes/analytics/",
        QuoteAnalyticsView.as_view(),
        name="quote-analytics-report",
    ),
    path(
        "reports/quotes/conversion/",
        QuoteConversionRateView.as_view(),
        name="quote-conversion-report",
    ),
    path(
        "reports/quotes/monthly/",
        QuoteMonthlyTrendsView.as_view(),
        name="quote-monthly-report",
    ),
    path(
        "reports/quotes/status/",
        QuoteStatusDistributionView.as_view(),
        name="quote-status-report",
    ),
]

template_patterns = [
    path(
        "templates/",
        QuoteTemplateViewSet.as_view({"get": "list"}),
        name="quote-templates-list",
    ),
    path(
        "templates/<int:pk>/",
        QuoteTemplateViewSet.as_view({"get": "retrieve"}),
        name="quote-template-detail",
    ),
    path(
        "templates/<int:pk>/use/",
        QuoteTemplateViewSet.as_view({"post": "use_template"}),
        name="quote-template-use",
    ),
    path(
        "templates/create/",
        QuoteTemplateViewSet.as_view({"post": "create"}),
        name="quote-template-create",
    ),
    path(
        "templates/<int:pk>/update/",
        QuoteTemplateViewSet.as_view({"put": "update", "patch": "partial_update"}),
        name="quote-template-update",
    ),
    path(
        "templates/<int:pk>/delete/",
        QuoteTemplateViewSet.as_view({"delete": "destroy"}),
        name="quote-template-delete",
    ),
]

search_patterns = [
    path(
        "search/quotes/", QuoteViewSet.as_view({"post": "search"}), name="search-quotes"
    ),
    path(
        "search/quotes/advanced/",
        QuoteViewSet.as_view({"post": "search"}),
        name="advanced-search-quotes",
    ),
    path(
        "search/quotes/by-client/",
        QuotesByClientView.as_view(),
        name="search-quotes-by-client",
    ),
    path(
        "search/quotes/by-service/",
        QuotesByServiceView.as_view(),
        name="search-quotes-by-service",
    ),
]

filter_patterns = [
    path(
        "filter/quotes/status/<str:status>/",
        QuoteViewSet.as_view({"get": "list"}),
        name="filter-quotes-by-status",
    ),
    path(
        "filter/quotes/cleaning-type/<str:cleaning_type>/",
        QuoteViewSet.as_view({"get": "list"}),
        name="filter-quotes-by-cleaning-type",
    ),
    path(
        "filter/quotes/urgency/<int:urgency_level>/",
        QuoteViewSet.as_view({"get": "list"}),
        name="filter-quotes-by-urgency",
    ),
    path(
        "filter/quotes/postcode/<str:postcode>/",
        QuoteViewSet.as_view({"get": "list"}),
        name="filter-quotes-by-postcode",
    ),
    path(
        "filter/quotes/state/<str:state>/",
        QuoteViewSet.as_view({"get": "list"}),
        name="filter-quotes-by-state",
    ),
]

export_patterns = [
    path("export/quotes/csv/", QuoteExportView.as_view(), name="export-quotes-csv"),
    path("export/quotes/excel/", QuoteExportView.as_view(), name="export-quotes-excel"),
    path("export/quotes/pdf/", QuoteExportView.as_view(), name="export-quotes-pdf"),
    path(
        "export/quotes/<uuid:pk>/pdf/",
        QuoteViewSet.as_view({"get": "pdf"}),
        name="export-quote-pdf",
    ),
]

notification_patterns = [
    path(
        "notifications/quotes/send/",
        QuoteNotificationView.as_view(),
        name="send-quote-notification",
    ),
    path(
        "notifications/quotes/status-change/",
        QuoteNotificationView.as_view(),
        name="quote-status-change-notification",
    ),
    path(
        "notifications/quotes/expiry-reminder/",
        QuoteNotificationView.as_view(),
        name="quote-expiry-reminder-notification",
    ),
]

dashboard_patterns = [
    path(
        "dashboard/quotes/overview/",
        QuoteViewSet.as_view({"get": "dashboard"}),
        name="quote-dashboard-overview",
    ),
    path(
        "dashboard/quotes/statistics/",
        QuoteViewSet.as_view({"get": "statistics"}),
        name="quote-dashboard-statistics",
    ),
    path(
        "dashboard/quotes/recent/",
        QuoteViewSet.as_view({"get": "list"}),
        name="quote-dashboard-recent",
    ),
    path(
        "dashboard/quotes/pending/",
        PendingQuotesView.as_view(),
        name="quote-dashboard-pending",
    ),
    path(
        "dashboard/quotes/expiring/",
        ExpiringQuotesView.as_view(),
        name="quote-dashboard-expiring",
    ),
    path(
        "dashboard/quotes/urgent/",
        UrgentQuotesView.as_view(),
        name="quote-dashboard-urgent",
    ),
]

archive_patterns = [
    path(
        "archive/quotes/", QuoteViewSet.as_view({"get": "list"}), name="archived-quotes"
    ),
    path(
        "archive/quotes/<uuid:pk>/",
        QuoteViewSet.as_view({"get": "retrieve"}),
        name="archived-quote-detail",
    ),
]

all_patterns = [
    path("api/", include(urlpatterns)),
    path("api/", include(api_v1_patterns)),
    path("public/", include(public_patterns)),
    path("", include(admin_patterns)),
    path("", include(client_patterns)),
    path("", include(staff_patterns)),
    path("", include(mobile_patterns)),
    path("", include(webhook_patterns)),
    path("", include(integration_patterns)),
    path("", include(ndis_patterns)),
    path("", include(bulk_patterns)),
    path("", include(reporting_patterns)),
    path("", include(template_patterns)),
    path("", include(search_patterns)),
    path("", include(filter_patterns)),
    path("", include(export_patterns)),
    path("", include(notification_patterns)),
    path("", include(dashboard_patterns)),
    path("", include(archive_patterns)),
]

urlpatterns = format_suffix_patterns(all_patterns)

quote_api_patterns = [
    path("quotes/", include((urlpatterns, "quotes"), namespace="quotes")),
]

quote_public_api_patterns = [
    path("calculator/", QuoteCalculatorView.as_view(), name="quote-calculator"),
]

quote_authenticated_api_patterns = [
    path("quotes/", include(router.urls)),
    path("quotes/my/", MyQuotesView.as_view(), name="my-quotes"),
    path("quotes/analytics/", QuoteAnalyticsView.as_view(), name="analytics"),
    path("quotes/export/", QuoteExportView.as_view(), name="export"),
]

quote_staff_api_patterns = [
    path("quotes/admin/", include(admin_patterns)),
    path("quotes/staff/", include(staff_patterns)),
    path("quotes/bulk/", include(bulk_patterns)),
    path("quotes/reports/", include(reporting_patterns)),
]

quote_mobile_api_patterns = [
    path("mobile/", include(mobile_patterns)),
]

quote_webhook_patterns = [
    path("webhooks/", include(webhook_patterns)),
]

quote_integration_patterns = [
    path("integrations/", include(integration_patterns)),
]

final_urlpatterns = [
    path("", include(quote_public_api_patterns)),
    path("", include(quote_authenticated_api_patterns)),
    path("", include(quote_staff_api_patterns)),
    path("", include(quote_mobile_api_patterns)),
    path("", include(quote_webhook_patterns)),
    path("", include(quote_integration_patterns)),
]

urlpatterns = final_urlpatterns


def get_quote_urls():
    return urlpatterns


def get_quote_api_urls():
    return quote_api_patterns


def get_quote_public_urls():
    return quote_public_api_patterns


def get_quote_staff_urls():
    return quote_staff_api_patterns


def get_quote_mobile_urls():
    return quote_mobile_api_patterns


quote_url_registry = {
    "public": quote_public_api_patterns,
    "authenticated": quote_authenticated_api_patterns,
    "staff": quote_staff_api_patterns,
    "mobile": quote_mobile_api_patterns,
    "webhooks": quote_webhook_patterns,
    "integrations": quote_integration_patterns,
}


def register_quote_urls(url_type="all"):
    if url_type == "all":
        return final_urlpatterns
    elif url_type in quote_url_registry:
        return quote_url_registry[url_type]
    else:
        return []


quote_url_names = [
    "quote-list",
    "quote-detail",
    "quote-create",
    "quote-update",
    "quote-delete",
    "quote-submit",
    "quote-approve",
    "quote-reject",
    "quote-cancel",
    "quote-assign",
    "quote-duplicate",
    "quote-convert",
    "quote-pdf",
    "quote-recalculate-pricing",
    "quote-bulk-operations",
    "quote-statistics",
    "quote-dashboard",
    "quote-search",
    "quote-calculator",
    "quote-analytics",
    "quote-reports",
    "quote-export",
    "quote-notifications",
    "my-quotes",
    "pending-quotes",
    "expiring-quotes",
    "urgent-quotes",
    "ndis-quotes",
    "high-value-quotes",
    "quotes-by-service",
    "quotes-by-client",
    "quote-conversion-rate",
    "quote-status-distribution",
    "quote-monthly-trends",
    "quoteitem-list",
    "quoteitem-detail",
    "quoteattachment-list",
    "quoteattachment-detail",
    "quoteattachment-download",
    "quoterevision-list",
    "quoterevision-detail",
    "quotetemplate-list",
    "quotetemplate-detail",
    "quotetemplate-use",
]


def get_quote_url_names():
    return quote_url_names


def validate_quote_urls():
    required_patterns = [
        "quote-calculator",
        "quote-list",
        "quote-detail",
        "quote-create",
        "quote-submit",
        "quote-approve",
        "quote-reject",
        "my-quotes",
    ]

    available_names = [
        pattern.name for pattern in final_urlpatterns if hasattr(pattern, "name")
    ]

    missing_patterns = [
        name for name in required_patterns if name not in available_names
    ]

    return {
        "valid": len(missing_patterns) == 0,
        "missing_patterns": missing_patterns,
        "total_patterns": len(available_names),
    }
