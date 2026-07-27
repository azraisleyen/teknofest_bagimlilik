import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.qr.models import QrToken
from apps.qr.tokens import TokenService

from .models import SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession


class StartSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True, max_length=100)
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)
    consent = serializers.ChoiceField(choices=["yes"])


class SurveyStartView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes: list[type[BasePermission]] = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "survey"

    @extend_schema(request=StartSerializer, responses={201: OpenApiTypes.OBJECT})
    def post(self, request):
        s = StartSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if s.validated_data.get("honeypot"):
            return Response({"status": "accepted"}, status=202)
        try:
            sid = uuid.UUID(request.COOKIES.get("sentra_session"))
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
        survey = (
            SurveyDefinition.objects.filter(active=True, status="PUBLISHED")
            .order_by("-version")
            .first()
        )
        if not survey:
            return Response(
                {
                    "error": {
                        "code": "SURVEY_UNAVAILABLE",
                        "message": "Anket kullanılamıyor.",
                        "correlation_id": request.correlation_id,
                    }
                },
                status=503,
            )
        raw = s.validated_data.get("token", "")
        token = (
            QrToken.objects.filter(
                token_hash=TokenService.lookup_hash(raw), context_expires_at__gt=timezone.now()
            ).first()
            if raw
            else None
        )
        context = {}
        mode = "GLOBAL_GENERAL"
        if token:
            event = token.event
            mode = "DYNAMIC_EVENT"
            context = {
                "event_id": str(event.event_id),
                "device_id": str(event.device_id),
                "location_id": event.location_id,
                "content_id": event.content_id,
                "content_version": event.content_version,
                "content_age_band": event.content_age_band,
                "selection_mode": event.selection_mode,
                "audience_mode": event.audience_mode,
            }
        session = SurveySession.objects.create(
            survey=survey,
            token=token,
            anonymous_session_id=sid,
            consent_version="1.0",
            consent_accepted_at=timezone.now(),
            privacy_notice_version="1.0",
            survey_version=survey.version,
            context_mode=mode,
            context_snapshot=context,
        )
        from apps.interactions.models import QrInteraction

        QrInteraction.objects.get_or_create(
            token=token, anonymous_session_id=sid, interaction_type="SURVEY_START"
        )
        return Response(
            {
                "session_id": session.session_id,
                "survey": {
                    "name": survey.name,
                    "version": survey.version,
                    "label": "DRAFT/DEMO",
                    "questions": [
                        {
                            "id": q.question_id,
                            "text": q.text,
                            "type": q.question_type,
                            "required": q.required,
                            "choices": [
                                {"value": c.value, "label": c.label} for c in q.choices.all()
                            ],
                        }
                        for q in survey.questions.prefetch_related("choices")
                    ],
                },
            },
            status=201,
        )


class ResponseSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    value = serializers.JSONField()


class SurveyResponseView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes: list[type[BasePermission]] = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "survey"

    @extend_schema(request=ResponseSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request, session_id):
        session = self._owned_session(request, session_id)
        s = ResponseSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        q = get_object_or_404(
            SurveyQuestion, question_id=s.validated_data["question_id"], survey=session.survey
        )
        value = s.validated_data["value"]
        if q.question_type == "LIKERT":
            allowed = set(q.choices.values_list("value", flat=True))
            if not isinstance(value, str) or value not in allowed:
                raise serializers.ValidationError("Geçersiz seçenek")
        elif q.question_type == "TEXT":
            if not isinstance(value, str):
                raise serializers.ValidationError("Metin yanıtı gerekli")
        else:
            raise serializers.ValidationError("Desteklenmeyen soru türü")
        if isinstance(value, str) and len(value) > min(
            q.max_length or settings.SURVEY_COMMENT_MAX, settings.SURVEY_COMMENT_MAX
        ):
            raise serializers.ValidationError("Yanıt çok uzun")
        SurveyResponse.objects.update_or_create(
            session=session, question=q, defaults={"value": value}
        )
        return Response({"status": "saved"})

    @staticmethod
    def _owned_session(request, session_id):
        try:
            sid = uuid.UUID(request.COOKIES.get("sentra_session"))
        except (ValueError, TypeError):
            sid = None
        return get_object_or_404(
            SurveySession, session_id=session_id, status="STARTED", anonymous_session_id=sid
        )


class SurveyFinishView(APIView):
    authentication_classes: list[type[BaseAuthentication]] = []
    permission_classes: list[type[BasePermission]] = []
    status_value = "COMPLETED"

    @extend_schema(request=None, responses=OpenApiTypes.OBJECT)
    def post(self, request, session_id):
        session = SurveyResponseView._owned_session(request, session_id)
        if self.status_value == "COMPLETED":
            required = session.survey.questions.filter(required=True).count()
            answered = session.responses.filter(question__required=True).count()
            if answered != required:
                return Response({"error": {"code": "REQUIRED_ANSWERS_MISSING"}}, status=400)
        session.status = self.status_value
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at"])
        from apps.interactions.models import QrInteraction

        QrInteraction.objects.get_or_create(
            token=session.token,
            anonymous_session_id=session.anonymous_session_id,
            interaction_type=f"SURVEY_{self.status_value[:-1] if self.status_value == 'COMPLETED' else 'DECLINED'}",
        )
        return Response({"status": self.status_value})


class SurveyDeclineView(SurveyFinishView):
    status_value = "DECLINED"
