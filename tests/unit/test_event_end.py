import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.devices.models import Device
from apps.qr.contracts import ContractError
from apps.qr.models import QrEventContext, QrToken
from apps.qr.services import DomainError, EventService
from apps.qr.tokens import TokenService

pytestmark = pytest.mark.django_db


def setup_event():
    device = Device.objects.create(device_name="Device", location_id="location")
    event = QrEventContext.objects.create(
        event_id=uuid.uuid4(),
        idempotency_key="start-key",
        device=device,
        location_id=device.location_id,
        content_id="content",
        content_version="1",
        content_age_band="GENERAL",
        selection_mode="MANUAL_TEST",
        audience_mode="UNKNOWN",
        started_at=timezone.now() - timedelta(seconds=10),
        status="ACTIVE",
        schema_version="1.0",
    )
    token, version = TokenService.create(device.device_id, event.event_id)
    QrToken.objects.create(
        event=event,
        token_hash=TokenService.lookup_hash(token),
        key_version=version,
        context_expires_at=timezone.now() + timedelta(minutes=15),
        mapping_expires_at=timezone.now() + timedelta(hours=24),
    )
    return device, event


def end_payload(device, event, occurred):
    return {
        "schema_version": "1.0",
        "event_id": str(event.event_id),
        "device_id": str(device.device_id),
        "event_type": "CONTENT_ENDED",
        "end_reason": "CONTENT_COMPLETED",
        "occurred_at": occurred,
    }


def stamp(value):
    return value.isoformat().replace("+00:00", "Z")


def test_valid_end_and_repeated_end_are_idempotent():
    device, event = setup_event()
    payload = end_payload(device, event, stamp(timezone.now()))
    first = EventService.end(device, payload, str(event.event_id))
    second = EventService.end(device, payload, str(event.event_id))
    assert first == second
    assert first["qr_mode"] == "GENERAL"


def test_end_before_start_is_rejected():
    device, event = setup_event()
    occurred = event.started_at - timedelta(seconds=1)
    with pytest.raises(DomainError, match="END_BEFORE_START") as error:
        EventService.end(device, end_payload(device, event, stamp(occurred)), str(event.event_id))
    assert error.value.code == "END_BEFORE_START"


@pytest.mark.parametrize("occurred", ["invalid", "2026-01-01T00:00:00"])
def test_invalid_or_naive_end_is_a_controlled_contract_error(occurred):
    device, event = setup_event()
    with pytest.raises(ContractError):
        EventService.end(device, end_payload(device, event, occurred), str(event.event_id))
