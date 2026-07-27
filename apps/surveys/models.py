import uuid

from django.db import models


class SurveyDefinition(models.Model):
    definition_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default="DRAFT_DEMO")
    intro_text = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "version"], name="unique_survey_version")
        ]


class SurveyQuestion(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(SurveyDefinition, models.PROTECT, related_name="questions")
    position = models.PositiveIntegerField()
    question_type = models.CharField(max_length=20)
    text = models.TextField()
    required = models.BooleanField(default=False)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    metric_key = models.CharField(max_length=80, blank=True)
    reverse_scored = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]


class SurveyChoice(models.Model):
    choice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(SurveyQuestion, models.PROTECT, related_name="choices")
    position = models.PositiveIntegerField()
    label = models.CharField(max_length=250)
    value = models.CharField(max_length=80)


class SurveySession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(SurveyDefinition, models.PROTECT)
    token = models.ForeignKey("qr.QrToken", models.SET_NULL, null=True, blank=True)
    anonymous_session_id = models.UUIDField()
    status = models.CharField(max_length=16, default="STARTED")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    consent_version = models.CharField(max_length=40, blank=True)
    consent_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_notice_version = models.CharField(max_length=40, blank=True)
    survey_version = models.PositiveIntegerField(default=1)
    context_mode = models.CharField(max_length=20, default="GLOBAL_GENERAL")
    context_snapshot = models.JSONField(default=dict)


class SurveyResponse(models.Model):
    response_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(SurveySession, models.CASCADE, related_name="responses")
    question = models.ForeignKey(SurveyQuestion, models.PROTECT)
    value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session", "question"], name="one_response_per_question"
            )
        ]
