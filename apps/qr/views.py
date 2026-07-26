from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.devices.authentication import DeviceAuthentication

from .models import QrDisplaySession, QrEventContext
from .serializers import DisplayEventSerializer, EventSerializer
from .services import DomainError, EventService


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "database": "available", "version": "1.0.0"})


class EventView(APIView):
    authentication_classes = [DeviceAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "edge"

    @extend_schema(request=EventSerializer, responses=EventSerializer)
    def post(self, request):
        try:
            data = dict(request.data)
            result = (
                EventService.start(request.user, data, request.headers.get("Idempotency-Key", ""))
                if data.get("event_type") == "CONTENT_STARTED"
                else EventService.end(
                    request.user, data, request.headers.get("Idempotency-Key", "")
                )
            )
        except DomainError as exc:
            return Response(
                {
                    "error": {
                        "code": exc.code,
                        "message": "İstek işlenemedi.",
                        "correlation_id": request.correlation_id,
                    }
                },
                status=exc.status,
            )
        except ValueError as exc:
            return Response(
                {
                    "error": {
                        "code": str(exc),
                        "message": "Geçersiz olay.",
                        "correlation_id": request.correlation_id,
                    }
                },
                status=400,
            )
        return Response(result)


class DisplayEventView(APIView):
    authentication_classes = [DeviceAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DisplayEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        event = (
            QrEventContext.objects.filter(
                event_id=data.get("event_id"), device=request.user
            ).first()
            if data.get("event_id")
            else None
        )
        if data["event_type"] == "DISPLAY_STARTED":
            session = QrDisplaySession.objects.create(
                event=event,
                device=request.user,
                qr_mode=data["qr_mode"],
                display_started_at=timezone.now(),
                fallback_reason=data.get("fallback_reason", ""),
            )
            return Response({"display_session_id": session.display_session_id}, status=201)
        session = (
            QrDisplaySession.objects.filter(
                event=event, device=request.user, display_ended_at__isnull=True
            )
            .order_by("-created_at")
            .first()
        )
        if session:
            session.display_ended_at = timezone.now()
            session.save(update_fields=["display_ended_at"])
        return Response({"status": "accepted"})
