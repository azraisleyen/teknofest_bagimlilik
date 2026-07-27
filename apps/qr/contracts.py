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
    filename = (
        "content-started.schema.json"
        if event_type == "CONTENT_STARTED"
        else "content-ended.schema.json"
    )
    path = files("apps.qr.schemas.v1").joinpath(filename)
    try:
        jsonschema.validate(payload, json.loads(path.read_text()))
    except jsonschema.ValidationError as exc:
        raise ContractError("INVALID_EVENT") from exc
    from django.utils.dateparse import parse_datetime

    for field in ["occurred_at", "animation_started_at", "animation_expected_end_at"]:
        if payload.get(field):
            value = parse_datetime(payload[field])
            if not value or value.utcoffset() != dt_timezone.utc.utcoffset(value):
                raise ContractError("TIMESTAMP_MUST_BE_UTC")
    return payload
