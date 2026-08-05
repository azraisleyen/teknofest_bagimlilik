import pytest
from django.test import override_settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@override_settings(ENABLE_DISPLAY_UI=True, ENABLE_DISPLAY_SIMULATOR=True)
def test_sentra_display_is_desktop_experience(client):
    response = client.get(reverse("display:screen"))
    assert response.status_code == 200
    assert b"SENTRA" in response.content
    assert b"SmokeVision" not in response.content
    assert b"qr-strip" in response.content


@override_settings(
    ENABLE_DISPLAY_UI=True,
    ENABLE_DISPLAY_SIMULATOR=True,
    PUBLIC_BASE_URL="https://sentra.test",
)
def test_simulator_creates_opaque_dynamic_qr_and_svg(client):
    start = client.post(reverse("display:simulate-start"))
    assert start.status_code == 200
    body = start.json()
    assert body["qr_mode"] == "DYNAMIC"
    assert body["content_id"] == "heart-impact-young-adult"
    assert "YOUNG_ADULT" not in body["public_url"]
    svg = client.get(body["qr_svg_url"])
    assert svg.status_code == 200
    assert svg["Content-Type"] == "image/svg+xml"
