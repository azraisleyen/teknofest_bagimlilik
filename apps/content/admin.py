from django.contrib import admin

from .models import ContentPackage


@admin.register(ContentPackage)
class ContentPackageAdmin(admin.ModelAdmin):
    list_display = (
        "content_id",
        "version",
        "age_band",
        "active",
        "psychologist_review_status",
        "health_review_status",
    )
    list_filter = ("age_band", "active", "psychologist_review_status", "health_review_status")
    search_fields = ("content_id", "title")
