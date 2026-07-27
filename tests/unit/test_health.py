from unittest.mock import patch

import pytest
from django.db import DatabaseError
from redis.exceptions import ConnectionError as RedisConnectionError

pytestmark = pytest.mark.django_db


def test_readiness_success(client):
    response = client.get("/api/v1/qr/health/ready")
    assert response.status_code == 200
    assert response.json()["dependencies"] == {"database": True, "cache": True}


def test_database_failure_does_not_hide_cache_result(client):
    with patch("apps.qr.views.connection.cursor", side_effect=DatabaseError("secret db details")):
        response = client.get("/api/v1/qr/health/ready")
    assert response.status_code == 503
    assert response.json()["dependencies"] == {"database": False, "cache": True}
    assert "secret" not in response.content.decode()


def test_cache_failure_does_not_hide_database_result(client):
    with patch("apps.qr.views.cache.set", side_effect=RedisConnectionError("secret cache details")):
        response = client.get("/api/v1/qr/health/ready")
    assert response.status_code == 503
    assert response.json()["dependencies"] == {"database": True, "cache": False}
    assert "secret" not in response.content.decode()


def test_both_dependencies_can_fail_and_liveness_remains_healthy(client):
    with (
        patch("apps.qr.views.connection.cursor", side_effect=DatabaseError("db")),
        patch("apps.qr.views.cache.set", side_effect=RedisConnectionError("cache")),
    ):
        ready = client.get("/api/v1/qr/health/ready")
        live = client.get("/api/v1/qr/health/live")
    assert ready.status_code == 503
    assert live.status_code == 200
    assert "traceback" not in ready.content.decode().lower()
