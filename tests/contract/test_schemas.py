import json
from importlib.resources import files

import pytest

try:
    import jsonschema
except ImportError:
    jsonschema = None
pytestmark = pytest.mark.skipif(jsonschema is None, reason="jsonschema dependency unavailable")


def schema(name):
    resource = files("apps.qr").joinpath("schemas", "v1", name)
    return json.loads(resource.read_text(encoding="utf-8"))


def test_unknown_and_sensitive_fields_rejected():
    payload = {
        "schema_version": "1.0",
        "event_id": "3f15a042-daa9-449d-bfa6-7f36e05fa0b1",
        "idempotency_key": "key-12345",
        "device_id": "device",
        "location_id": "location",
        "event_type": "CONTENT_STARTED",
        "content_id": "content",
        "content_version": "1",
        "content_age_band": "GENERAL",
        "selection_mode": "MANUAL_TEST",
        "audience_mode": "UNKNOWN",
        "animation_started_at": "2026-01-01T00:00:00Z",
        "animation_expected_end_at": None,
        "occurred_at": "2026-01-01T00:00:00Z",
    }
    jsonschema.validate(payload, schema("content-started.schema.json"))
    payload["face_image"] = "base64"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema("content-started.schema.json"))
