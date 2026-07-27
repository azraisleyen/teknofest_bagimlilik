from urllib.parse import urlparse

ALLOWED_MAP_HOSTS = {"www.google.com", "google.com", "maps.google.com"}


def safe_map_url(url):
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_MAP_HOSTS and not parsed.username


def center_for_location(location_id):
    from .models import LocationCenterMapping

    mapping = (
        LocationCenterMapping.objects.select_related("primary_center", "backup_center")
        .filter(location_id=location_id, active=True)
        .first()
    )
    if not mapping:
        return None
    if mapping.primary_center.active:
        return mapping.primary_center
    if mapping.backup_center and mapping.backup_center.active:
        return mapping.backup_center
    return None
