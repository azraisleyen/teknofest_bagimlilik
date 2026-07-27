from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.http import HttpRequest


class SentraAdminSite(AdminSite):
    def has_permission(self, request: HttpRequest) -> bool:
        basic_permission = super().has_permission(request)
        if settings.DEBUG:
            return basic_permission
        is_verified = getattr(request.user, "is_verified", lambda: False)
        return basic_permission and bool(is_verified())


class SentraAdminConfig(AdminConfig):
    default_site = "config.admin.SentraAdminSite"
