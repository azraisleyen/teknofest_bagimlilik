from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "actor", "action", "object_type", "object_reference")
    list_filter = ("action", "object_type")
    readonly_fields = (
        "audit_id",
        "actor",
        "action",
        "object_type",
        "object_reference",
        "metadata",
        "occurred_at",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: models.Model | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: models.Model | None = None) -> bool:
        return False
