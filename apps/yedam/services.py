from urllib.parse import urlencode, urlparse

from django.conf import settings
from django.utils import timezone

ALLOWED_MAP_HOSTS = {"www.google.com", "google.com", "maps.google.com"}


def safe_map_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_MAP_HOSTS and not parsed.username


def build_map_url(center):
    """Build a directions URL only from administrator-verified center data."""
    destination = f"{center.center_name}, {center.address}"
    query = {"api": "1", "destination": destination}
    if center.map_place_id:
        query["destination_place_id"] = center.map_place_id
    url = f"https://www.google.com/maps/dir/?{urlencode(query)}"
    if not safe_map_url(url):
        raise ValueError("Unsafe map URL")
    return url


def center_for_location(location_id):
    from .models import LocationCenterMapping

    mapping = (
        LocationCenterMapping.objects.select_related("primary_center", "backup_center")
        .filter(location_id=location_id, active=True)
        .first()
    )
    if not mapping or mapping.mapping_verified_at < timezone.now() - timezone.timedelta(
        days=settings.YEDAM_STALE_DAYS
    ):
        return None
    cutoff = timezone.now() - timezone.timedelta(days=settings.YEDAM_STALE_DAYS)
    if mapping.primary_center.active and mapping.primary_center.last_verified_at >= cutoff:
        return mapping.primary_center
    if (
        mapping.backup_center
        and mapping.backup_center.active
        and mapping.backup_center.last_verified_at >= cutoff
    ):
        return mapping.backup_center
    return None
