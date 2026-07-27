import uuid

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler


def exception_handler(exc, context):
    response = drf_handler(exc, context)
    correlation_id = getattr(context.get("request"), "correlation_id", str(uuid.uuid4()))
    if response is None:
        return Response(
            {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "İstek işlenemedi.",
                    "correlation_id": correlation_id,
                }
            },
            status=500,
        )
    code = getattr(exc, "default_code", "REQUEST_ERROR")
    code = code if isinstance(code, str) else "REQUEST_ERROR"
    response.data = {
        "error": {
            "code": code.upper(),
            "message": "İstek doğrulanamadı.",
            "correlation_id": correlation_id,
        }
    }
    return response
