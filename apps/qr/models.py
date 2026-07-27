import uuid

from django.db import models
from django.db.models import Q


class QrEventContext(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        ENDED = "ENDED"
        EXPIRED = "EXPIRED"

    event_id = models.UUIDField(primary_key=True)
    idempotency_key = models.CharField(max_length=128)
    device = models.ForeignKey("devices.Device", models.PROTECT, related_name="qr_events")
    location_id = models.CharField(max_length=120)
    content_id = models.CharField(max_length=160)
    content_version = models.CharField(max_length=80)
    content_age_band = models.CharField(max_length=20)
    selection_mode = models.CharField(max_length=40)
    audience_mode = models.CharField(max_length=32)
    started_at = models.DateTimeField()
    expected_end_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    end_reason = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.ACTIVE)
    schema_version = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["device", "idempotency_key"], name="unique_device_idempotency"
            ),
            models.UniqueConstraint(
                fields=["device"], condition=Q(status="ACTIVE"), name="one_active_event_per_device"
            ),
        ]


class QrToken(models.Model):
    token_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_hash = models.CharField(max_length=64, unique=True)
    event = models.OneToOneField(QrEventContext, models.CASCADE, related_name="token")
    key_version = models.CharField(max_length=20)
    status = models.CharField(max_length=12, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    context_expires_at = models.DateTimeField()
    mapping_expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)


class QrDisplaySession(models.Model):
    display_session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(QrEventContext, models.SET_NULL, null=True, blank=True)
    device = models.ForeignKey("devices.Device", models.PROTECT)
    qr_mode = models.CharField(max_length=16)
    display_started_at = models.DateTimeField()
    display_ended_at = models.DateTimeField(null=True, blank=True)
    fallback_reason = models.CharField(max_length=40, blank=True)
    qr_visual_version = models.CharField(max_length=20, default="v1")
    created_at = models.DateTimeField(auto_now_add=True)
    idempotency_key = models.CharField(max_length=128, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["device", "idempotency_key"], name="unique_display_idempotency"
            )
        ]


class DeviceSupportToken(models.Model):
    token_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey("devices.Device", models.PROTECT, related_name="support_tokens")
    token_hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=12, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
