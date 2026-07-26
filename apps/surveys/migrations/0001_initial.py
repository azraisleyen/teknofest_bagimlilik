import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("qr", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="SurveyDefinition",
            fields=[
                (
                    "definition_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("version", models.PositiveIntegerField()),
                ("status", models.CharField(default="DRAFT_DEMO", max_length=20)),
                ("intro_text", models.TextField()),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("name", "version"), name="unique_survey_version"
                    )
                ]
            },
        ),
        migrations.CreateModel(
            name="SurveyQuestion",
            fields=[
                (
                    "question_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("position", models.PositiveIntegerField()),
                ("question_type", models.CharField(max_length=20)),
                ("text", models.TextField()),
                ("required", models.BooleanField(default=False)),
                ("max_length", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="questions",
                        to="surveys.surveydefinition",
                    ),
                ),
            ],
            options={"ordering": ["position"]},
        ),
        migrations.CreateModel(
            name="SurveyChoice",
            fields=[
                (
                    "choice_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("position", models.PositiveIntegerField()),
                ("label", models.CharField(max_length=250)),
                ("value", models.CharField(max_length=80)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="choices",
                        to="surveys.surveyquestion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SurveySession",
            fields=[
                (
                    "session_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("anonymous_session_id", models.UUIDField()),
                ("status", models.CharField(default="STARTED", max_length=16)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="surveys.surveydefinition"
                    ),
                ),
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
        ),
        migrations.CreateModel(
            name="SurveyResponse",
            fields=[
                (
                    "response_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("value", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="surveys.surveyquestion"
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="responses",
                        to="surveys.surveysession",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("session", "question"), name="one_response_per_question"
                    )
                ]
            },
        ),
    ]
