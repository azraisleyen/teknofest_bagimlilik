from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import YedamCenter
from .services import build_map_url


def _coordinate(value):
    if value is None:  # Defensive guard; queryset excludes null coordinates.
        raise ValueError("Center coordinate is required")
    return float(value)


@require_GET
def public_centers(request):
    cutoff = timezone.now() - timedelta(days=settings.YEDAM_STALE_DAYS)
    centers = YedamCenter.objects.filter(
        active=True,
        last_verified_at__gte=cutoff,
        latitude__isnull=False,
        longitude__isnull=False,
    )
    response = JsonResponse(
        {
            "centers": [
                {
                    "id": str(center.center_id),
                    "name": center.center_name,
                    "city": center.city,
                    "district": center.district,
                    "address": center.address,
                    "latitude": _coordinate(center.latitude),
                    "longitude": _coordinate(center.longitude),
                    "directions_url": build_map_url(center),
                    "official_source_url": center.official_source_url,
                    "last_verified_at": center.last_verified_at.isoformat(),
                }
                for center in centers
            ]
        }
    )
    response["Cache-Control"] = "public, max-age=3600"
    return response
