from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceItemViewSet, NDISInvoiceViewSet

app_name = "invoices"

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoice")
router.register(r"invoice-items", InvoiceItemViewSet, basename="invoiceitem")
router.register(r"ndis-invoices", NDISInvoiceViewSet, basename="ndis-invoice")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/invoices/<uuid:pk>/download/",
        InvoiceViewSet.as_view({"get": "download_pdf"}),
        name="invoice-download",
    ),
    path(
        "api/invoices/<uuid:pk>/resend-email/",
        InvoiceViewSet.as_view({"post": "resend_email"}),
        name="invoice-resend-email",
    ),
    path(
        "api/invoices/<uuid:pk>/regenerate-pdf/",
        InvoiceViewSet.as_view({"post": "regenerate_pdf"}),
        name="invoice-regenerate-pdf",
    ),
    path(
        "api/invoices/my-invoices/",
        InvoiceViewSet.as_view({"get": "my_invoices"}),
        name="my-invoices",
    ),
    path(
        "api/invoices/ndis-invoices/",
        InvoiceViewSet.as_view({"get": "ndis_invoices"}),
        name="ndis-invoices",
    ),
    path(
        "api/invoices/dashboard-stats/",
        InvoiceViewSet.as_view({"get": "dashboard_stats"}),
        name="dashboard-stats",
    ),
    path(
        "api/ndis-invoices/<uuid:pk>/compliance-check/",
        NDISInvoiceViewSet.as_view({"get": "compliance_check"}),
        name="ndis-compliance-check",
    ),
]
