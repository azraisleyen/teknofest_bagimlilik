import json
from datetime import timedelta
from datetime import timezone as dt_timezone
from importlib.resources import files

import jsonschema
from django.conf import settings
from django.utils import timezone


class ContractError(ValueError):
    pass


def validate_event(payload):
    event_type = payload.get("event_type")
    if event_type not in {"CONTENT_STARTED", "CONTENT_ENDED"}:
        raise ContractError("UNSUPPORTED_EVENT_TYPE")
    schema = files("apps.qr").joinpath(
        "schemas",
        "v1",
        (
            "content-started.schema.json"
            if event_type == "CONTENT_STARTED"
            else "content-ended.schema.json"
        ),
    )
    try:
        jsonschema.validate(
            payload,
            json.loads(schema.read_text(encoding="utf-8")),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as exc:
        raise ContractError("INVALID_EVENT") from exc
    from django.utils.dateparse import parse_datetime

    for field in ["occurred_at", "animation_started_at", "animation_expected_end_at"]:
        if payload.get(field):
            value = parse_datetime(payload[field])
            if not value or value.utcoffset() != dt_timezone.utc.utcoffset(value):
                raise ContractError("TIMESTAMP_MUST_BE_UTC")
    occurred = parse_datetime(payload.get("occurred_at", ""))
    if occurred is None:
        raise ContractError("INVALID_EVENT")
    now = timezone.now()
    skew = timedelta(seconds=settings.QR_EVENT_CLOCK_SKEW_SECONDS)
    if occurred < now - skew or occurred > now + skew:
        raise ContractError("EVENT_TIME_OUT_OF_RANGE")
    started = parse_datetime(payload.get("animation_started_at", ""))
    expected = parse_datetime(payload.get("animation_expected_end_at", ""))
    if started and expected and expected < started:
        raise ContractError("EXPECTED_END_BEFORE_START")
    return payload
