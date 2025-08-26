from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    return JsonResponse(
        {
            "status": "healthy",
            "service": "cleaning_service",
            "version": "1.0.0",
            "environment": "production" if not settings.DEBUG else "development",
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def api_root(request):
    return JsonResponse(
        {
            "message": "Welcome to Professional Cleaning Service API",
            "version": "v1",
            "endpoints": {
                "accounts": "/api/v1/accounts/",
                "health": "/api/health/",
                "admin": "/admin/",
                "docs": "/api/docs/",
            },
        }
    )


admin.site.site_header = "Professional Cleaning Service Admin"
admin.site.site_title = "Cleaning Service Admin Portal"
admin.site.index_title = "Welcome to Cleaning Service Administration"

api_urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", api_health_check, name="api_health_check"),
    path("api/", api_root, name="api_root"),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/services/", include("services.urls")),
    path("api/v1/quotes/", include("quotes.urls")),
    path("api/v1/invoices/", include("invoices.urls")),
]

urlpatterns = api_urlpatterns

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# This catch-all route must be last
urlpatterns.append(re_path(r".*", TemplateView.as_view(template_name="index.html")))

handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
handler403 = "django.views.defaults.permission_denied"
handler400 = "django.views.defaults.bad_request"
