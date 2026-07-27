import hashlib
import hmac
import secrets
import uuid

from django.db import models


class Device(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        DISABLED = "DISABLED"

    device_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_name = models.CharField(max_length=120)
    location_id = models.CharField(max_length=120, db_index=True)
    software_version = models.CharField(max_length=40, blank=True)
    qr_module_version = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.ACTIVE)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    credential_hash = models.CharField(max_length=64, blank=True)
    credential_prefix = models.CharField(max_length=12, blank=True)
    credential_revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def issue_credential(self):
        secret = secrets.token_urlsafe(32)
        self.credential_prefix = secret[:8]
        self.credential_hash = hashlib.sha256(secret.encode()).hexdigest()
        self.credential_revoked_at = None
        self.save(
            update_fields=[
                "credential_prefix",
                "credential_hash",
                "credential_revoked_at",
                "updated_at",
            ]
        )
        return f"{self.device_id}.{secret}"

    def verify(self, secret):
        return (
            self.status == self.Status.ACTIVE
            and not self.credential_revoked_at
            and hmac.compare_digest(
                self.credential_hash, hashlib.sha256(secret.encode()).hexdigest()
            )
        )
