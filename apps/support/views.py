import uuid

from django.conf import settings
from django.shortcuts import render

from apps.interactions.models import QrInteraction
from apps.qr.models import DeviceSupportToken
from apps.qr.token_resolution import TokenResolutionService
from apps.qr.tokens import TokenService
from apps.yedam.services import build_map_url, center_for_location

from .text import SUPPORT_TEXT


def _session(request):
    value = request.COOKIES.get("sentra_session")
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError):
        return uuid.uuid4()


def support_page(request, token=None, installation_token=None):
    sid = _session(request)
    mapping = None
    dynamic = False
    device_token = None
    if token:
        resolution = TokenResolutionService.resolve(token)
        if resolution.token:
            mapping = resolution.token if resolution.context_available else None
            dynamic = resolution.context_available
            QrInteraction.objects.get_or_create(
                token=resolution.token,
                anonymous_session_id=sid,
                interaction_type="LANDING_VIEW",
            )
    elif installation_token:
        device_token = (
            DeviceSupportToken.objects.select_related("device")
            .filter(token_hash=TokenService.lookup_hash(installation_token), status="ACTIVE")
            .first()
        )
    location_id = (
        mapping.event.location_id
        if mapping
        else (device_token.device.location_id if device_token else None)
    )
    center = center_for_location(location_id) if location_id else None
    map_url = build_map_url(center) if center else ""
    from apps.surveys.models import SurveyDefinition
    from apps.yedam.models import YedamCenter

    survey_available = SurveyDefinition.objects.filter(active=True, status="PUBLISHED").exists()
    cities = list(
        YedamCenter.objects.filter(active=True, latitude__isnull=False, longitude__isnull=False)
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")
    )
    response = render(
        request,
        "support/page.html",
        {
            "text": SUPPORT_TEXT,
            "center": center,
            "map_available": bool(map_url),
            "map_url": map_url,
            "directory_url": settings.OFFICIAL_YEDAM_DIRECTORY_URL,
            "dynamic": dynamic,
            "token": token or "",
            "survey_available": survey_available,
            "cities": cities,
        },
    )
    response.set_cookie(
        "sentra_session",
        str(sid),
        max_age=settings.ANONYMOUS_SESSION_MINUTES * 60,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
    response["Cache-Control"] = "no-store"
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response
