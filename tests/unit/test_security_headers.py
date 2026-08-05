import pytest

pytestmark = pytest.mark.django_db


def test_location_is_limited_to_support_and_survey_pages(client):
    support = client.get("/support/")
    assert "geolocation=(self)" in support["Permissions-Policy"]
    survey = client.get("/survey/")
    assert "geolocation=(self)" in survey["Permissions-Policy"]
    api = client.get("/api/v1/qr/health/live")
    assert "geolocation=()" in api["Permissions-Policy"]


def test_camera_and_microphone_are_disabled_everywhere(client):
    response = client.get("/support/")
    assert "camera=()" in response["Permissions-Policy"]
    assert "microphone=()" in response["Permissions-Policy"]
