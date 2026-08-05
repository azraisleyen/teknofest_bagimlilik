import uuid
from datetime import timedelta
from io import BytesIO

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from apps.content.models import ContentPackage
from apps.devices.models import Device
from apps.qr.services import EventService
from apps.qr.token_resolution import TokenResolutionService


def _require_display():
    if not settings.ENABLE_DISPLAY_UI:
        raise Http404


def _demo_device():
    device, _ = Device.objects.get_or_create(
        device_name="SENTRA Display Simulator",
        defaults={"location_id": "campus-demo", "software_version": "1.1"},
    )
    return device


def _package():
    package = ContentPackage.objects.filter(active=True).order_by("priority").first()
    if package:
        return package
    return ContentPackage(
        content_id="heart-impact-young-adult",
        version=1,
        title="Kalp ve Dolaşım Üzerindeki Etkiler",
        age_band=ContentPackage.AgeBand.YOUNG_ADULT,
        video_asset="content/young_adult/heart_impact_v1.mp4",
        poster_asset="content/young_adult/heart_impact_v1.jpg",
        caption_asset="content/young_adult/heart_impact_v1.tr.vtt",
        duration_ms=10005,
        file_hash="demo",
    )


@ensure_csrf_cookie
@require_GET
def display_page(request):
    _require_display()
    package = _package()
    return render(
        request,
        "display/sentra_display.html",
        {
            "simulator_enabled": settings.ENABLE_DISPLAY_SIMULATOR,
            "content": package,
            "video_url": static(package.video_asset),
            "poster_url": static(package.poster_asset),
            "caption_url": static(package.caption_asset),
            "detection_video_url": static("display/media/detection_demo.mp4"),
            "general_qr_url": static("qr/general.svg"),
            "support_url": settings.GENERAL_SUPPORT_URL,
        },
    )


@require_POST
def simulate_start(request):
    _require_display()
    if not settings.ENABLE_DISPLAY_SIMULATOR:
        raise Http404
    device = _demo_device()
    package = _package()
    now = timezone.now()
    event_id = uuid.uuid4()
    key = f"display-{event_id}"
    payload = {
        "schema_version": "1.0",
        "event_id": str(event_id),
        "idempotency_key": key,
        "device_id": str(device.device_id),
        "location_id": device.location_id,
        "event_type": "CONTENT_STARTED",
        "content_id": str(package.content_id),
        "content_version": str(package.version),
        "content_age_band": package.age_band,
        "selection_mode": "MANUAL_TEST",
        "audience_mode": "SINGLE",
        "animation_started_at": now.isoformat().replace("+00:00", "Z"),
        "animation_expected_end_at": (now + timedelta(milliseconds=package.duration_ms))
        .isoformat()
        .replace("+00:00", "Z"),
        "occurred_at": now.isoformat().replace("+00:00", "Z"),
    }
    result = EventService.start(device, payload, key)
    token = result["public_url"].rsplit("/", 1)[-1]
    result.update(
        {
            "token": token,
            "qr_svg_url": f"/qr/image/{token}.svg",
            "duration_ms": package.duration_ms,
            "content_id": package.content_id,
        }
    )
    return JsonResponse(result)


@require_POST
def simulate_end(request, event_id):
    _require_display()
    if not settings.ENABLE_DISPLAY_SIMULATOR:
        raise Http404
    device = _demo_device()
    now = timezone.now()
    result = EventService.end(
        device,
        {
            "schema_version": "1.0",
            "event_id": str(event_id),
            "device_id": str(device.device_id),
            "event_type": "CONTENT_ENDED",
            "end_reason": "CONTENT_COMPLETED",
            "occurred_at": now.isoformat().replace("+00:00", "Z"),
        },
        str(event_id),
    )
    return JsonResponse(result)


@require_GET
def token_qr_image(request, token):
    resolution = TokenResolutionService.resolve(token)
    target = (
        f"{settings.PUBLIC_BASE_URL}/q/{token}"
        if resolution.token is not None
        else settings.GENERAL_SUPPORT_URL
    )
    qr = qrcode.QRCode(version=None, box_size=8, border=4)
    qr.add_data(target)
    qr.make(fit=True)
    image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    output = BytesIO()
    image.save(output)
    response = HttpResponse(output.getvalue(), content_type="image/svg+xml")
    response["Cache-Control"] = "no-store"
    return response
