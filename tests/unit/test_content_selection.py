import pytest

from apps.content.models import ContentPackage
from apps.content.selectors import AudienceResolver, ContentSelector

pytestmark = pytest.mark.django_db


def package(content_id, band, priority=10):
    return ContentPackage.objects.create(
        content_id=content_id,
        version=1,
        title=content_id,
        age_band=band,
        video_asset="video.mp4",
        duration_ms=1000,
        file_hash="a" * 64,
        active=True,
        priority=priority,
    )


def test_unstable_or_mixed_audience_uses_general_content():
    general = package("general", ContentPackage.AgeBand.GENERAL)
    package("young", ContentPackage.AgeBand.YOUNG_ADULT)
    decision = AudienceResolver.resolve(["YOUNG_ADULT", "OLDER_ADULT"])
    assert decision.age_band == "GENERAL"
    assert ContentSelector.select(decision) == general


def test_missing_band_falls_back_to_general():
    general = package("general", ContentPackage.AgeBand.GENERAL)
    decision = AudienceResolver.resolve(["MIDDLE_AGE"])
    assert ContentSelector.select(decision) == general
