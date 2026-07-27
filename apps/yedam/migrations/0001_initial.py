import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="YedamCenter",
            fields=[
                (
                    "center_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("center_name", models.CharField(max_length=200)),
                ("city", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("address", models.TextField()),
                ("map_place_id", models.CharField(blank=True, max_length=255)),
                ("map_url", models.URLField(blank=True)),
                ("appointment_number", models.CharField(default="115", max_length=30)),
                ("official_source_url", models.URLField()),
                ("last_verified_at", models.DateTimeField()),
                ("verified_by", models.CharField(max_length=120)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="LocationCenterMapping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("location_id", models.CharField(max_length=120, unique=True)),
                ("mapping_verified_at", models.DateTimeField()),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "backup_center",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="backup_mappings",
                        to="yedam.yedamcenter",
                    ),
                ),
                (
                    "primary_center",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="primary_mappings",
                        to="yedam.yedamcenter",
                    ),
                ),
            ],
        ),
    ]
