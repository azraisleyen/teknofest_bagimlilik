from django.contrib import admin

from .models import LocationCenterMapping, YedamCenter


@admin.register(YedamCenter)
class YedamCenterAdmin(admin.ModelAdmin):
    list_display = ("center_name", "city", "district", "last_verified_at", "active")
    list_filter = ("active", "city")
    search_fields = ("center_name", "city", "district", "address")


@admin.register(LocationCenterMapping)
class LocationCenterMappingAdmin(admin.ModelAdmin):
    list_display = (
        "location_id",
        "primary_center",
        "backup_center",
        "mapping_verified_at",
        "active",
    )
    list_filter = ("active",)
