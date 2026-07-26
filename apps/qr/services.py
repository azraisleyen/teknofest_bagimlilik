from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from .contracts import validate_event
from .models import QrEventContext, QrToken
from .tokens import TokenService


class DomainError(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status


class EventService:
    @staticmethod
    @transaction.atomic
    def start(device, payload, header_key):
        validate_event(payload)
        if (
            payload["device_id"] != str(device.device_id)
            or payload["idempotency_key"] != header_key
        ):
            raise DomainError("IDEMPOTENCY_MISMATCH")
        existing = (
            QrEventContext.objects.select_for_update().filter(event_id=payload["event_id"]).first()
        )
        if existing:
            if existing.device_id != device.device_id or existing.idempotency_key != header_key:
                raise DomainError("IDEMPOTENCY_CONFLICT", 409)
            return EventService._result(existing)
        if (
            QrEventContext.objects.select_for_update()
            .filter(device=device, status="ACTIVE")
            .exists()
        ):
            raise DomainError("ACTIVE_EVENT_CONFLICT", 409)
        try:
            event = QrEventContext.objects.create(
                event_id=payload["event_id"],
                idempotency_key=header_key,
                device=device,
                location_id=payload["location_id"],
                content_id=payload["content_id"],
                content_version=payload["content_version"],
                content_age_band=payload["content_age_band"],
                selection_mode=payload["selection_mode"],
                audience_mode=payload["audience_mode"],
                started_at=payload["animation_started_at"],
                expected_end_at=payload.get("animation_expected_end_at"),
                schema_version=payload["schema_version"],
            )
        except IntegrityError as exc:
            raise DomainError("ACTIVE_EVENT_CONFLICT", 409) from exc
        now = timezone.now()
        token, version = TokenService.create(device.device_id, event.event_id)
        QrToken.objects.create(
            event=event,
            token_hash=TokenService.lookup_hash(token),
            key_version=version,
            context_expires_at=now + timedelta(minutes=settings.QR_CONTEXT_MINUTES),
            mapping_expires_at=now + timedelta(hours=settings.QR_MAPPING_HOURS),
        )
        return EventService._result(event, token)

    @staticmethod
    def _result(event, token=None):
        token = (
            token
            or TokenService.create(event.device_id, event.event_id, event.token.key_version)[0]
        )
        return {
            "schema_version": "1.0",
            "event_id": str(event.event_id),
            "qr_mode": "DYNAMIC",
            "public_url": f"{settings.PUBLIC_BASE_URL}/q/{token}",
            "context_expires_at": event.token.context_expires_at,
            "display_until": event.expected_end_at,
        }

    @staticmethod
    @transaction.atomic
    def end(device, payload, header_key):
        validate_event(payload)
        if payload["device_id"] != str(device.device_id) or header_key != str(payload["event_id"]):
            raise DomainError("IDEMPOTENCY_MISMATCH")
        event = (
            QrEventContext.objects.select_for_update()
            .filter(event_id=payload["event_id"], device=device)
            .first()
        )
        if not event:
            raise DomainError("START_EVENT_NOT_FOUND", 409)
        if event.status == "ENDED":
            return {
                "schema_version": "1.0",
                "event_id": str(event.event_id),
                "qr_mode": "GENERAL",
                "general_url": settings.GENERAL_SUPPORT_URL,
            }
        active = QrEventContext.objects.filter(device=device, status="ACTIVE").first()
        if not active or active.event_id != event.event_id:
            raise DomainError("MISMATCHED_END_EVENT", 409)
        event.status = "ENDED"
        event.ended_at = payload["occurred_at"]
        event.end_reason = payload["end_reason"]
        event.save(update_fields=["status", "ended_at", "end_reason", "updated_at"])
        event.token.status = "REVOKED"
        event.token.revoked_at = timezone.now()
        event.token.save(update_fields=["status", "revoked_at"])
        return {
            "schema_version": "1.0",
            "event_id": str(event.event_id),
            "qr_mode": "GENERAL",
            "general_url": settings.GENERAL_SUPPORT_URL,
        }
