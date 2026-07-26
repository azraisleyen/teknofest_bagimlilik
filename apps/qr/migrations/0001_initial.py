import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("devices", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="QrEventContext",
            fields=[
                ("event_id", models.UUIDField(primary_key=True, serialize=False)),
                ("idempotency_key", models.CharField(max_length=128)),
                ("location_id", models.CharField(max_length=120)),
                ("content_id", models.CharField(max_length=160)),
                ("content_version", models.CharField(max_length=80)),
                ("content_age_band", models.CharField(max_length=20)),
                ("selection_mode", models.CharField(max_length=40)),
                ("audience_mode", models.CharField(max_length=32)),
                ("started_at", models.DateTimeField()),
                ("expected_end_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("end_reason", models.CharField(blank=True, max_length=40)),
                ("status", models.CharField(default="ACTIVE", max_length=12)),
                ("schema_version", models.CharField(max_length=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="qr_events",
                        to="devices.device",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("device", "idempotency_key"), name="unique_device_idempotency"
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("status", "ACTIVE")),
                        fields=("device",),
                        name="one_active_event_per_device",
                    ),
                ]
            },
        ),
        migrations.CreateModel(
            name="QrToken",
            fields=[
                (
                    "token_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("token_hash", models.CharField(max_length=64, unique=True)),
                ("key_version", models.CharField(max_length=20)),
                ("status", models.CharField(default="ACTIVE", max_length=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("context_expires_at", models.DateTimeField()),
                ("mapping_expires_at", models.DateTimeField()),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                (
                    "event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="token",
                        to="qr.qreventcontext",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QrDisplaySession",
            fields=[
                (
                    "display_session_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("qr_mode", models.CharField(max_length=16)),
                ("display_started_at", models.DateTimeField()),
                ("display_ended_at", models.DateTimeField(blank=True, null=True)),
                ("fallback_reason", models.CharField(blank=True, max_length=40)),
                ("qr_visual_version", models.CharField(default="v1", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="devices.device"
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="qr.qreventcontext",
                    ),
                ),
            ],
        ),
    ]
