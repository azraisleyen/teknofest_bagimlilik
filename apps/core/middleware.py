import uuid

from django.conf import settings
from django.http import JsonResponse


class RequestSafetyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))[:64]
        if (
            request.method in {"POST", "PUT", "PATCH"}
            and int(request.META.get("CONTENT_LENGTH") or 0) > settings.MAX_REQUEST_BODY
        ):
            return JsonResponse(
                {
                    "error": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": "İstek çok büyük.",
                        "correlation_id": request.correlation_id,
                    }
                },
                status=413,
            )
        response = self.get_response(request)
        response["X-Correlation-ID"] = request.correlation_id
        response["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        response["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        return response
