import base64
import hashlib
import hmac
from pathlib import Path


def token(key, device, event):
    return (
        base64.urlsafe_b64encode(
            hmac.new(
                key.encode(), f"sentra-qr|1|{device}|{event}".encode(), hashlib.sha256
            ).digest()
        )
        .rstrip(b"=")
        .decode()
    )


def test_token_properties():
    first = token("k" * 32, "device", "event-a")
    assert first == token("k" * 32, "device", "event-a")
    assert first != token("k" * 32, "device", "event-b")
    assert len(first) >= 22
    assert "device" not in first


def test_web_controller_has_race_guards():
    text = Path("clients/web/qr-controller.js").read_text()
    assert "this.generation!==generation" in text
    assert "this.eventId!==eventId" in text
    assert "replaceChildren" in text
