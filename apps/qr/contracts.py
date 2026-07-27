import json
from datetime import timezone as dt_timezone
from importlib.resources import files

import jsonschema


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
        jsonschema.validate(payload, json.loads(schema.read_text(encoding="utf-8")))
    except jsonschema.ValidationError as exc:
        raise ContractError("INVALID_EVENT") from exc
    from django.utils.dateparse import parse_datetime

    for field in ["occurred_at", "animation_started_at", "animation_expected_end_at"]:
        if payload.get(field):
            value = parse_datetime(payload[field])
            if not value or value.utcoffset() != dt_timezone.utc.utcoffset(value):
                raise ContractError("TIMESTAMP_MUST_BE_UTC")
    return payload
