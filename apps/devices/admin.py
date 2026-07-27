from django.contrib import admin

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_name", "device_id", "location_id", "status", "credential_prefix")
    list_filter = ("status",)
    search_fields = ("device_name", "device_id", "location_id", "credential_prefix")
    readonly_fields = (
        "device_id",
        "credential_hash",
        "credential_prefix",
        "created_at",
        "updated_at",
    )
