from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.yedam.models import YedamCenter
from apps.yedam.services import haversine_km

pytestmark = pytest.mark.django_db


def center():
    return YedamCenter.objects.create(
        center_name="Doğrulanmış Test Merkezi",
        city="Ankara",
        district="Çankaya",
        address="Test adresi",
        latitude=Decimal("39.920770"),
        longitude=Decimal("32.854110"),
        coordinate_source="Test fixture",
        official_source_url="https://www.yedam.org.tr/iletisim",
        last_verified_at=timezone.now(),
        verified_by="test",
    )


def test_public_catalog_exposes_centers_but_never_user_coordinates(client):
    center()
    response = client.get(reverse("yedam-centers"))
    assert response.status_code == 200
    assert response.json()["centers"][0]["name"] == "Doğrulanmış Test Merkezi"
    assert "user_location" not in response.json()


def test_haversine_helper_returns_zero_for_center_point():
    item = center()
    assert haversine_km(item.latitude, item.longitude, item) == pytest.approx(0)
