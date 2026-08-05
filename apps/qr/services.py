from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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
        if payload["location_id"] != device.location_id:
            raise DomainError("LOCATION_MISMATCH")
        EventService.expire_for_device(device)
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
        display_until = event.expected_end_at
        if event.ended_at:
            display_until = event.ended_at + timedelta(seconds=settings.QR_DISPLAY_GRACE_SECONDS)
        return {
            "schema_version": "1.0",
            "event_id": str(event.event_id),
            "qr_mode": "DYNAMIC",
            "public_url": f"{settings.PUBLIC_BASE_URL}/q/{token}",
            "context_expires_at": event.token.context_expires_at,
            "display_until": display_until,
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
            return EventService._result(event)
        active = QrEventContext.objects.filter(device=device, status="ACTIVE").first()
        if not active or active.event_id != event.event_id:
            raise DomainError("MISMATCHED_END_EVENT", 409)
        ended_at = parse_datetime(payload.get("occurred_at", ""))
        if ended_at is None or timezone.is_naive(ended_at):
            raise DomainError("INVALID_EVENT")
        if ended_at < event.started_at:
            raise DomainError("END_BEFORE_START")
        event.status = "ENDED"
        event.ended_at = ended_at
        event.end_reason = payload["end_reason"]
        event.save(update_fields=["status", "ended_at", "end_reason", "updated_at"])
        # Normal content completion ends the display event but deliberately keeps
        # the opaque support token valid until context_expires_at. This allows a
        # person to scan during the post-animation grace period without exposing
        # model output in the QR value.
        return EventService._result(event)

    @staticmethod
    @transaction.atomic
    def expire_for_device(device=None):
        cutoff = timezone.now() - timedelta(minutes=settings.QR_EVENT_HARD_TIMEOUT_MINUTES)
        events = QrEventContext.objects.select_for_update().filter(
            status="ACTIVE", started_at__lt=cutoff
        )
        if device is not None:
            events = events.filter(device=device)
        count = 0
        for event in events:
            event.status = "EXPIRED"
            event.ended_at = timezone.now()
            event.end_reason = "HARD_TIMEOUT"
            event.save(update_fields=["status", "ended_at", "end_reason", "updated_at"])
            QrToken.objects.filter(event=event).update(status="REVOKED", revoked_at=timezone.now())
            count += 1
        return count
