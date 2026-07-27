import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("qr", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="QrInteraction",
            fields=[
                (
                    "interaction_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("interaction_type", models.CharField(max_length=24)),
                ("anonymous_session_id", models.UUIDField()),
                ("occurred_at", models.DateTimeField(auto_now_add=True)),
                (
                    "token",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="qr.qrtoken",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["token", "anonymous_session_id", "interaction_type"],
                        name="interactions_token_i_42aa5f_idx",
                    )
                ]
            },
        )
    ]
