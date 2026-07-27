import uuid

from django.utils import timezone
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.qr.models import QrToken
from apps.qr.tokens import TokenService

from .models import QrInteraction


class InteractionSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100, required=False, allow_blank=True)
    interaction_type = serializers.ChoiceField(choices=[x[0] for x in QrInteraction.TYPES])


class InteractionView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes: list[type[BasePermission]] = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public"

    def post(self, request):
        s = InteractionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        sid = request.COOKIES.get("sentra_session")
        try:
            sid = uuid.UUID(sid)
        except (ValueError, TypeError):
            return Response(
                {
                    "error": {
                        "code": "SESSION_REQUIRED",
                        "message": "Oturum gerekli.",
                        "correlation_id": request.correlation_id,
                    }
                },
                status=400,
            )
        token_value = s.validated_data.get("token", "")
        token = (
            QrToken.objects.filter(
                token_hash=TokenService.lookup_hash(token_value),
                mapping_expires_at__gt=timezone.now(),
            ).first()
            if token_value
            else None
        )
        QrInteraction.objects.create(
            token=token,
            anonymous_session_id=sid,
            interaction_type=s.validated_data["interaction_type"],
        )
        return Response({"status": "recorded"}, status=201)
