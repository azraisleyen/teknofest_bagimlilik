import uuid
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.qr.contracts import ContractError, validate_event


def payload(now=None):
    now = now or timezone.now()
    stamp = now.isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0",
        "event_id": str(uuid.uuid4()),
        "idempotency_key": "test-key-123",
        "device_id": str(uuid.uuid4()),
        "location_id": "location",
        "event_type": "CONTENT_STARTED",
        "content_id": "content",
        "content_version": "1",
        "content_age_band": "GENERAL",
        "selection_mode": "MANUAL_TEST",
        "audience_mode": "UNKNOWN",
        "animation_started_at": stamp,
        "animation_expected_end_at": (now + timedelta(seconds=30))
        .isoformat()
        .replace("+00:00", "Z"),
        "occurred_at": stamp,
    }


def test_valid_utc_timestamp_is_accepted():
    assert validate_event(payload())["event_type"] == "CONTENT_STARTED"


@pytest.mark.parametrize("value", ["not-a-date", "2026-01-01T12:00:00"])
def test_invalid_or_naive_timestamp_is_controlled(value):
    data = payload()
    data["occurred_at"] = value
    with pytest.raises(ContractError):
        validate_event(data)


@pytest.mark.parametrize("offset", [timedelta(hours=-1), timedelta(hours=1)])
def test_timestamp_outside_clock_skew_is_rejected(offset):
    with pytest.raises(ContractError, match="EVENT_TIME_OUT_OF_RANGE"):
        validate_event(payload(timezone.now() + offset))


def test_expected_end_before_start_is_rejected():
    data = payload()
    data["animation_expected_end_at"] = (
        (timezone.now() - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
    )
    with pytest.raises(ContractError, match="EXPECTED_END_BEFORE_START"):
        validate_event(data)


def test_none_parse_result_is_controlled_after_schema_validation():
    data = payload()
    with (
        patch("jsonschema.validate"),
        patch("django.utils.dateparse.parse_datetime", return_value=None),
    ):
        with pytest.raises(ContractError, match="TIMESTAMP_MUST_BE_UTC"):
            validate_event(data)
