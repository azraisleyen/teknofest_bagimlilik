import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qr.models import QrToken
from apps.qr.tokens import TokenService

from .models import SurveyDefinition, SurveyQuestion, SurveyResponse, SurveySession


class StartSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True, max_length=100)
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)


class SurveyStartView(APIView):
    authentication_classes = []
    permission_classes = []

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
        session = SurveySession.objects.create(survey=survey, token=token, anonymous_session_id=sid)
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
    authentication_classes = []
    permission_classes = []

    def post(self, request, session_id):
        session = SurveySession.objects.get(session_id=session_id, status="STARTED")
        s = ResponseSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        q = SurveyQuestion.objects.get(
            question_id=s.validated_data["question_id"], survey=session.survey
        )
        value = s.validated_data["value"]
        if isinstance(value, str) and len(value) > min(
            q.max_length or settings.SURVEY_COMMENT_MAX, settings.SURVEY_COMMENT_MAX
        ):
            raise serializers.ValidationError("Yanıt çok uzun")
        SurveyResponse.objects.update_or_create(
            session=session, question=q, defaults={"value": value}
        )
        return Response({"status": "saved"})


class SurveyFinishView(APIView):
    authentication_classes = []
    permission_classes = []
    status_value = "COMPLETED"

    def post(self, request, session_id):
        session = SurveySession.objects.get(session_id=session_id, status="STARTED")
        session.status = self.status_value
        session.completed_at = timezone.now()
        session.save(update_fields=["status", "completed_at"])
        return Response({"status": self.status_value})


class SurveyDeclineView(SurveyFinishView):
    status_value = "DECLINED"
