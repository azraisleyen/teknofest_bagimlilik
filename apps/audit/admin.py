from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "action", "object_type", "object_reference", "actor")
    readonly_fields = (
        "audit_id",
        "actor",
        "action",
        "object_type",
        "object_reference",
        "metadata",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("audit.view_auditlog") if obj is None else False

    def has_delete_permission(self, request, obj=None):
        return False
