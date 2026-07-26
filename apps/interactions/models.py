import uuid

from django.db import models


class QrInteraction(models.Model):
    TYPES = [
        (x, x)
        for x in [
            "LANDING_VIEW",
            "CALL_115_CLICK",
            "DIRECTIONS_CLICK",
            "ALL_CENTERS_CLICK",
            "SURVEY_START",
            "SURVEY_COMPLETE",
            "SURVEY_DECLINED",
        ]
    ]
    interaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.ForeignKey("qr.QrToken", models.SET_NULL, null=True, blank=True)
    interaction_type = models.CharField(max_length=24, choices=TYPES)
    anonymous_session_id = models.UUIDField()
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["token", "anonymous_session_id", "interaction_type"])]
