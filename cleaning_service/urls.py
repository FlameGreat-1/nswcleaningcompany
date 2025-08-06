from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", api_health_check, name="api_health_check"),
    path("api/", api_root, name="api_root"),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/services/", include("services.urls")),
    path("api/v1/quotes/", include("quotes.urls")),
    path("", RedirectView.as_view(url="/api/", permanent=False), name="root_redirect"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
handler403 = "django.views.defaults.permission_denied"
handler400 = "django.views.defaults.bad_request"
