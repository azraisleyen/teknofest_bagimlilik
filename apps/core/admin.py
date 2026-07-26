from django.conf import settings
from django.contrib import admin

_original_has_permission = admin.site.has_permission


def _mfa_permission(request):
    basic = _original_has_permission(request)
    if settings.DEBUG:
        return basic
    return basic and bool(getattr(request.user, "is_verified", lambda: False)())


admin.site.has_permission = _mfa_permission
