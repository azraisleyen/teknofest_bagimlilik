from django.contrib import admin

from .models import LocationCenterMapping, YedamCenter


class NoBulkDeleteAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(YedamCenter)
class YedamCenterAdmin(NoBulkDeleteAdmin):
    list_display = ("center_name", "city", "district", "active", "last_verified_at")
    list_filter = ("active", "city", "district")
    search_fields = ("center_name", "address", "city", "district")


@admin.register(LocationCenterMapping)
class LocationCenterMappingAdmin(NoBulkDeleteAdmin):
    list_display = (
        "location_id",
        "primary_center",
        "backup_center",
        "active",
        "mapping_verified_at",
    )
    list_filter = ("active", "primary_center__city", "primary_center__district")
    search_fields = ("location_id", "primary_center__center_name", "backup_center__center_name")
