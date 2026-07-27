import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    return env(name, str(default)).lower() in {"1", "true", "yes", "on"}


SECRET_KEY = env("DJANGO_SECRET_KEY", "development-only-secret-key-change-me")
DEBUG = False
ALLOWED_HOSTS = [
    x.strip() for x in env("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "apps.core",
    "apps.devices",
    "apps.qr",
    "apps.support",
    "apps.yedam",
    "apps.surveys",
    "apps.interactions",
    "apps.audit",
]
MIDDLEWARE = [
    "apps.core.middleware.RequestSafetyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "apps.core.middleware.AdminMfaMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
LANGUAGE_CODE = "tr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PUBLIC_BASE_URL = env("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
GENERAL_SUPPORT_URL = env("GENERAL_SUPPORT_URL", PUBLIC_BASE_URL + "/support/")
OFFICIAL_YEDAM_DIRECTORY_URL = env(
    "OFFICIAL_YEDAM_DIRECTORY_URL", "https://www.yedam.org.tr/yesilay-danismanlik-merkezi"
)
TOKEN_KEYS = {
    env("TOKEN_KEY_VERSION", "v1"): env(
        "TOKEN_KEY_V1", "development-token-key-change-me-at-least-32-bytes"
    )
}
TOKEN_KEY_VERSION = env("TOKEN_KEY_VERSION", "v1")
QR_CONTEXT_MINUTES = int(env("QR_CONTEXT_MINUTES", "15"))
QR_MAPPING_HOURS = int(env("QR_MAPPING_HOURS", "24"))
ANONYMOUS_SESSION_MINUTES = int(env("ANONYMOUS_SESSION_MINUTES", "30"))
MAX_REQUEST_BODY = int(env("MAX_REQUEST_BODY", "32768"))
SURVEY_COMMENT_MAX = int(env("SURVEY_COMMENT_MAX", "500"))
YEDAM_STALE_DAYS = int(env("YEDAM_STALE_DAYS", "180"))
QR_ERROR_CORRECTION = env("QR_ERROR_CORRECTION", "M")
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.errors.exception_handler",
    "DEFAULT_THROTTLE_RATES": {"public": "60/min", "edge": "120/min"},
}
SPECTACULAR_SETTINGS = {"TITLE": "SENTRA QR API", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False}
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "no-referrer"
ENABLE_DEMO_UI = env_bool("ENABLE_DEMO_UI", False)
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
