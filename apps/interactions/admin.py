from django.contrib import admin

from .models import QrInteraction


@admin.register(QrInteraction)
class QrInteractionAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "interaction_type", "anonymous_session_id")
    list_filter = ("interaction_type",)
    readonly_fields = (
        "interaction_id",
        "token",
        "interaction_type",
        "anonymous_session_id",
        "occurred_at",
    )
