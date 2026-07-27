from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Device


class DeviceAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.devices.authentication.DeviceAuthentication"
    name = "deviceBearerAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer"}


class DeviceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        value = request.headers.get("Authorization", "")
        if not value.startswith("Bearer "):
            raise AuthenticationFailed(
                "Device authentication required", code="DEVICE_AUTH_REQUIRED"
            )
        raw = value[7:]
        try:
            device_id, secret = raw.split(".", 1)
            device = Device.objects.get(device_id=device_id)
        except (ValueError, Device.DoesNotExist):
            raise AuthenticationFailed(
                "Invalid device credential", code="INVALID_DEVICE_CREDENTIAL"
            ) from None
        if not device.verify(secret):
            raise AuthenticationFailed(
                "Invalid device credential", code="INVALID_DEVICE_CREDENTIAL"
            )
        return device, None
