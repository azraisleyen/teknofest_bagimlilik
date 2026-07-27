import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80)
    object_reference = models.CharField(max_length=120)
    metadata = models.JSONField(default=dict)
    occurred_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("Audit records are immutable")
        return super().save(*args, **kwargs)
