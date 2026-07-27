import os
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
import django

django.setup()
from django.test import override_settings  # noqa: E402

from apps.qr.tokens import TokenService  # noqa: E402


@override_settings(TOKEN_KEYS={"old": "o" * 32, "new": "n" * 32}, TOKEN_KEY_VERSION="new")  # noqa: S106
def test_token_properties_and_rotation():
    first, version = TokenService.create("device", "event-a")
    old, old_version = TokenService.create("device", "event-a", "old")
    assert version == "new" and old_version == "old"
    assert first != old and "device" not in first
    assert TokenService.lookup_hash(first) != first


def test_web_controller_has_race_guards():
    text = Path("clients/web/qr-controller.js").read_text()
    assert "this.generation!==generation" in text
    assert "this.eventId!==eventId" in text
    assert "replaceChildren" in text
