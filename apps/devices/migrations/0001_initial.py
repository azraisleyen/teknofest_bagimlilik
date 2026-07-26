import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "device_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("device_name", models.CharField(max_length=120)),
                ("location_id", models.CharField(db_index=True, max_length=120)),
                ("software_version", models.CharField(blank=True, max_length=40)),
                ("qr_module_version", models.CharField(blank=True, max_length=40)),
                ("status", models.CharField(default="ACTIVE", max_length=12)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("credential_hash", models.CharField(blank=True, max_length=64)),
                ("credential_prefix", models.CharField(blank=True, max_length=12)),
                ("credential_revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        )
    ]
