import base64
import hashlib
import hmac

from django.conf import settings


class TokenService:
    @staticmethod
    def create(device_id, event_id, key_version=None):
        version = key_version or settings.TOKEN_KEY_VERSION
        key = settings.TOKEN_KEYS[version].encode()
        message = f"sentra-qr|1|{device_id}|{event_id}".encode()
        digest = hmac.new(key, message, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode(), version

    @staticmethod
    def lookup_hash(token):
        return hashlib.sha256(token.encode()).hexdigest()
