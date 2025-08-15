import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "django_extensions",
    "accounts",
    "services",
    "quotes",
    "invoices",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "quotes.middleware.quote_middleware.QuoteDebugMiddleware",  
    "quotes.middleware.quote_middleware.DatabaseConsistencyMiddleware",  
]

ROOT_URLCONF = "cleaning_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cleaning_service.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3")
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-AU"
TIME_ZONE = "Australia/Sydney"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = (
    [
        BASE_DIR / "static",
    ]
    if (BASE_DIR / "static").exists()
    else []
)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
SITE_ID = 1

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
}

EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@nswcc.com.au")
SERVER_EMAIL = config("SERVER_EMAIL", default="server@nswcc.com.au")
SUPPORT_EMAIL = config("SUPPORT_EMAIL", default="support@nswcc.com.au")

GOOGLE_OAUTH2_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")
GOOGLE_OAUTH2_REDIRECT_URI = config("GOOGLE_OAUTH2_REDIRECT_URI", default="")

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
BACKEND_URL = config("BACKEND_URL", default="http://localhost:8000")
SITE_NAME = config("SITE_NAME", default="NSWCC")
COMPANY_NAME = config("COMPANY_NAME", default="NSWCC")

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CACHES = {
    "default": {
        "BACKEND": config(
            "CACHE_BACKEND", default="django.core.cache.backends.locmem.LocMemCache"
        ),
        "LOCATION": config("CACHE_LOCATION", default="unique-snowflake"),
        "TIMEOUT": config("CACHE_TIMEOUT", default=300, cast=int),
        "OPTIONS": {
            "MAX_ENTRIES": config("CACHE_MAX_ENTRIES", default=1000, cast=int),
        },
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}

ADMINS = [
    ("Admin", config("ADMIN_EMAIL", default="admin@nswcleaningcompany.com.au")),
]
MANAGERS = ADMINS

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

DEFAULT_ADMIN_EMAIL = config(
    "DEFAULT_ADMIN_EMAIL", default="admin@nswcleaningcompany.com.au"
)
DEFAULT_ADMIN_PASSWORD = config("DEFAULT_ADMIN_PASSWORD", default="admin123")

MAX_USER_SESSIONS = config("MAX_USER_SESSIONS", default=5, cast=int)
PASSWORD_RESET_TIMEOUT = config("PASSWORD_RESET_TIMEOUT", default=3600, cast=int)
EMAIL_VERIFICATION_TIMEOUT = config(
    "EMAIL_VERIFICATION_TIMEOUT", default=86400, cast=int
)

NDIS_COMPLIANCE_ENABLED = config("NDIS_COMPLIANCE_ENABLED", default=True, cast=bool)
ACCESSIBILITY_FEATURES_ENABLED = config(
    "ACCESSIBILITY_FEATURES_ENABLED", default=True, cast=bool
)
SOCIAL_AUTH_ENABLED = config("SOCIAL_AUTH_ENABLED", default=True, cast=bool)
GOOGLE_AUTH_ENABLED = config("GOOGLE_AUTH_ENABLED", default=True, cast=bool)
GDPR_COMPLIANCE_ENABLED = config("GDPR_COMPLIANCE_ENABLED", default=True, cast=bool)
AUDIT_LOG_ENABLED = config("AUDIT_LOG_ENABLED", default=True, cast=bool)
USER_ACTIVITY_TRACKING = config("USER_ACTIVITY_TRACKING", default=True, cast=bool)
MAINTENANCE_MODE = config("MAINTENANCE_MODE", default=False, cast=bool)

DATA_RETENTION_DAYS = config("DATA_RETENTION_DAYS", default=2555, cast=int)

API_RATE_LIMIT_ENABLED = config("API_RATE_LIMIT_ENABLED", default=True, cast=bool)
API_RATE_LIMIT_PER_HOUR = config("API_RATE_LIMIT_PER_HOUR", default=1000, cast=int)

FEATURE_FLAGS = {
    "google_auth": config("FEATURE_GOOGLE_AUTH", default=True, cast=bool),
    "email_notifications": config(
        "FEATURE_EMAIL_NOTIFICATIONS", default=True, cast=bool
    ),
    "sms_notifications": config("FEATURE_SMS_NOTIFICATIONS", default=False, cast=bool),
    "advanced_search": config("FEATURE_ADVANCED_SEARCH", default=True, cast=bool),
    "bulk_operations": config("FEATURE_BULK_OPERATIONS", default=True, cast=bool),
}

os.makedirs(BASE_DIR / "media", exist_ok=True)
os.makedirs(BASE_DIR / "staticfiles", exist_ok=True)

APPEND_SLASH = True
PREPEND_WWW = False
USE_THOUSAND_SEPARATOR = True
NUMBER_GROUPING = 3
FIRST_DAY_OF_WEEK = 1
SHORT_DATE_FORMAT = "d/m/Y"
SHORT_DATETIME_FORMAT = "d/m/Y H:i"
DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","
DEFAULT_CHARSET = "utf-8"
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND", default="redis://localhost:6379/0"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
