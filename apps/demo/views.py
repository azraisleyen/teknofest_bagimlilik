import uuid
from datetime import timedelta

from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.devices.models import Device
from apps.qr.services import DomainError, EventService


def index(request):
    return render(
        request,
        "demo/index.html",
        {"devices": Device.objects.all(), "events": request.session.get("demo_events", [])},
    )


@require_POST
def simulate(request):
    device = Device.objects.get(device_id=request.POST["device"])
    action = request.POST["action"]
    now = timezone.now()
    event_id = request.session.get("demo_event_id") or str(uuid.uuid4())
    key = request.session.get("demo_key") or str(uuid.uuid4())
    try:
        if action == "start":
            payload = {
                "schema_version": "1.0",
                "event_id": event_id,
                "idempotency_key": key,
                "device_id": str(device.device_id),
                "location_id": device.location_id,
                "event_type": "CONTENT_STARTED",
                "content_id": request.POST.get("content_id", "demo-content"),
                "content_version": "1",
                "content_age_band": "GENERAL",
                "selection_mode": "MANUAL_TEST",
                "audience_mode": "UNKNOWN",
                "animation_started_at": now.isoformat().replace("+00:00", "Z"),
                "animation_expected_end_at": (now + timedelta(seconds=30))
                .isoformat()
                .replace("+00:00", "Z"),
                "occurred_at": now.isoformat().replace("+00:00", "Z"),
            }
            result = EventService.start(device, payload, key)
            request.session["demo_event_id"] = event_id
            request.session["demo_key"] = key
        elif action == "end":
            result = EventService.end(
                device,
                {
                    "schema_version": "1.0",
                    "event_id": event_id,
                    "device_id": str(device.device_id),
                    "event_type": "CONTENT_ENDED",
                    "end_reason": "MANUAL_TEST",
                    "occurred_at": now.isoformat().replace("+00:00", "Z"),
                },
                event_id,
            )
        else:
            result = {"qr_mode": "GENERAL", "message": "Simulated safe fallback"}
    except (DomainError, ValueError) as exc:
        result = {"qr_mode": "GENERAL", "message": getattr(exc, "code", str(exc))}
    request.session["demo_events"] = [str(result)] + request.session.get("demo_events", [])[:9]
    return redirect("/demo/")
