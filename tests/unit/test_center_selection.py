from datetime import timedelta

import pytest
from django.utils import timezone

from apps.yedam.models import LocationCenterMapping, YedamCenter
from apps.yedam.services import center_for_location

pytestmark = pytest.mark.django_db


def center(name, *, active=True, age=0):
    return YedamCenter.objects.create(
        center_name=name,
        city="Ankara",
        district="Çankaya",
        address="Adres",
        official_source_url="https://www.yedam.org.tr/iletisim",
        last_verified_at=timezone.now() - timedelta(days=age),
        verified_by="test",
        active=active,
    )


def mapping(primary, backup=None, *, age=0):
    return LocationCenterMapping.objects.create(
        location_id="location",
        primary_center=primary,
        backup_center=backup,
        mapping_verified_at=timezone.now() - timedelta(days=age),
        active=True,
    )


def test_current_primary_is_selected():
    primary = center("Primary")
    mapping(primary)
    assert center_for_location("location") == primary


def test_inactive_primary_uses_current_backup():
    primary, backup = center("Primary", active=False), center("Backup")
    mapping(primary, backup)
    assert center_for_location("location") == backup


def test_stale_mapping_or_missing_mapping_returns_none(settings):
    primary = center("Primary")
    mapping(primary, age=settings.YEDAM_STALE_DAYS + 1)
    assert center_for_location("location") is None
    assert center_for_location("missing") is None


def test_stale_primary_uses_current_backup(settings):
    primary = center("Primary", age=settings.YEDAM_STALE_DAYS + 1)
    backup = center("Backup")
    mapping(primary, backup)
    assert center_for_location("location") == backup


def test_unusable_centers_return_none(settings):
    primary = center("Primary", age=settings.YEDAM_STALE_DAYS + 1)
    backup = center("Backup", active=False)
    mapping(primary, backup)
    assert center_for_location("location") is None
