import uuid

from django.db import models


class YedamCenter(models.Model):
    center_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    center_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    map_place_id = models.CharField(max_length=255, blank=True)
    map_url = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    coordinate_source = models.CharField(max_length=200, blank=True)
    appointment_number = models.CharField(max_length=30, default="115")
    official_source_url = models.URLField()
    last_verified_at = models.DateTimeField()
    verified_by = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["city", "district", "center_name"]


class LocationCenterMapping(models.Model):
    location_id = models.CharField(max_length=120, unique=True)
    primary_center = models.ForeignKey(YedamCenter, models.PROTECT, related_name="primary_mappings")
    backup_center = models.ForeignKey(
        YedamCenter, models.PROTECT, null=True, blank=True, related_name="backup_mappings"
    )
    mapping_verified_at = models.DateTimeField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
