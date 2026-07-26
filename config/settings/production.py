from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403,F401

DEBUG = False
if ENABLE_DEMO_UI:
    raise ImproperlyConfigured("ENABLE_DEMO_UI must be false in production")
if SECRET_KEY.startswith("development-"):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required")
if any("development-token" in value for value in TOKEN_KEYS.values()):
    raise ImproperlyConfigured("production token key required")
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
if not env_bool("ADMIN_MFA_REQUIRED", True):
    raise ImproperlyConfigured("Admin MFA is mandatory")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", "db"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
    }
}
if env("REDIS_URL"):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("REDIS_URL"),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
