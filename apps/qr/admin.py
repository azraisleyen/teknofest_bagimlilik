from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from .models import QrDisplaySession, QrEventContext, QrToken


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: models.Model | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: models.Model | None = None) -> bool:
        return False


@admin.register(QrEventContext)
class QrEventContextAdmin(ReadOnlyAdmin):
    list_display = ("event_id", "device", "status", "started_at", "ended_at")
    list_filter = ("status", "content_age_band", "selection_mode")


@admin.register(QrToken)
class QrTokenAdmin(ReadOnlyAdmin):
    list_display = ("token_id", "event", "key_version", "status", "mapping_expires_at")
    exclude = ("token_hash",)


@admin.register(QrDisplaySession)
class QrDisplaySessionAdmin(ReadOnlyAdmin):
    list_display = (
        "display_session_id",
        "device",
        "qr_mode",
        "display_started_at",
        "display_ended_at",
    )
    list_filter = ("qr_mode", "fallback_reason")
