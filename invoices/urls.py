from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceItemViewSet, NDISInvoiceViewSet

app_name = "invoices"

router = DefaultRouter()
router.register(r"", InvoiceViewSet, basename="invoice") 
router.register(r"items", InvoiceItemViewSet, basename="invoiceitem")  
router.register(r"ndis", NDISInvoiceViewSet, basename="ndis-invoice")  
urlpatterns = [
    path("", include(router.urls)),
    path(
        "<uuid:pk>/download/",
        InvoiceViewSet.as_view({"get": "download_pdf"}),
        name="invoice-download",
    ),
    path(
        "<uuid:pk>/resend-email/", 
        InvoiceViewSet.as_view({"post": "resend_email"}),
        name="invoice-resend-email",
    ),
    path(
        "<uuid:pk>/regenerate-pdf/",  
        InvoiceViewSet.as_view({"post": "regenerate_pdf"}),
        name="invoice-regenerate-pdf",
    ),
    path(
        "ndis/<uuid:pk>/compliance-check/",  
        NDISInvoiceViewSet.as_view({"get": "compliance_check"}),
        name="ndis-compliance-check",
    ),
]
