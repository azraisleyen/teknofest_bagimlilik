from django.core.cache import cache
from django.db import DatabaseError, connection
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from redis.exceptions import RedisError
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.devices.authentication import DeviceAuthentication

from .models import QrDisplaySession, QrEventContext
from .serializers import DisplayEventSerializer, EventSerializer
from .services import DomainError, EventService


class HealthView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes: list[type[BasePermission]] = []

    @extend_schema(request=None, responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return ReadyHealthView().get(request)


class LiveHealthView(HealthView):
    @extend_schema(request=None, responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response({"status": "ok", "version": "1.0.0"})


class ReadyHealthView(HealthView):
    @extend_schema(request=None, responses=OpenApiTypes.OBJECT)
    def get(self, request):
        dependencies = {"database": False, "cache": False}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                dependencies["database"] = cursor.fetchone() == (1,)
        except DatabaseError:
            pass
        try:
            cache.set("sentra-readiness", "ok", 5)
            dependencies["cache"] = cache.get("sentra-readiness") == "ok"
        except (ConnectionError, OSError, RedisError, TimeoutError):
            pass
        ready = all(dependencies.values())
        return Response(
            {"status": "ready" if ready else "unavailable", "dependencies": dependencies},
            status=200 if ready else 503,
        )


class EventView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = [DeviceAuthentication]
    permission_classes: list[type[BasePermission]] = [IsAuthenticated]
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
    authentication_classes: list[type[BaseAuthentication]] = [DeviceAuthentication]
    permission_classes: list[type[BasePermission]] = [IsAuthenticated]

    @extend_schema(request=DisplayEventSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = DisplayEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        key = request.headers.get("Idempotency-Key", "")
        if len(key) < 8 or len(key) > 128:
            return Response({"error": {"code": "INVALID_IDEMPOTENCY_KEY"}}, status=400)
        event = (
            QrEventContext.objects.filter(
                event_id=data.get("event_id"), device=request.user
            ).first()
            if data.get("event_id")
            else None
        )
        if data["qr_mode"] == "DYNAMIC" and not event:
            return Response({"error": {"code": "DYNAMIC_EVENT_REQUIRED"}}, status=400)
        existing = QrDisplaySession.objects.filter(device=request.user, idempotency_key=key).first()
        if existing:
            return Response(
                {"display_session_id": existing.display_session_id, "status": "accepted"}
            )
        if data["event_type"] == "DISPLAY_STARTED":
            session = QrDisplaySession.objects.create(
                event=event,
                device=request.user,
                qr_mode=data["qr_mode"],
                display_started_at=timezone.now(),
                fallback_reason=data.get("fallback_reason", ""),
                idempotency_key=key,
            )
            return Response({"display_session_id": session.display_session_id}, status=201)
        active_session = (
            QrDisplaySession.objects.filter(
                event=event, device=request.user, display_ended_at__isnull=True
            )
            .order_by("-created_at")
            .first()
        )
        if active_session:
            active_session.display_ended_at = timezone.now()
            active_session.save(update_fields=["display_ended_at"])
        return Response({"status": "accepted"})
