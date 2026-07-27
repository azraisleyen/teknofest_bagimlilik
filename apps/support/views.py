import secrets
import uuid

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

from apps.interactions.models import QrInteraction
from apps.qr.models import DeviceSupportToken, QrToken
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
        record = (
            QrToken.objects.select_related("event")
            .filter(
                token_hash=TokenService.lookup_hash(token),
                status="ACTIVE",
                mapping_expires_at__gt=timezone.now(),
            )
            .first()
        )
        if (
            record
            and secrets.compare_digest(record.token_hash, TokenService.lookup_hash(token))
            and record.context_expires_at > timezone.now()
        ):
            dynamic = True
            mapping = record
            QrInteraction.objects.get_or_create(
                token=record, anonymous_session_id=sid, interaction_type="LANDING_VIEW"
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

    survey_available = SurveyDefinition.objects.filter(active=True, status="PUBLISHED").exists()
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
