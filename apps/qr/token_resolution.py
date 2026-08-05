from dataclasses import dataclass

from django.utils import timezone

from .models import QrToken
from .tokens import TokenService


@dataclass(frozen=True)
class TokenResolution:
    token: QrToken | None
    context_available: bool


class TokenResolutionService:
    """Resolve opaque QR tokens without ever returning an error-only destination."""

    @staticmethod
    def resolve(raw_token: str) -> TokenResolution:
        token = (
            QrToken.objects.select_related("event")
            .filter(
                token_hash=TokenService.lookup_hash(raw_token),
                status="ACTIVE",
                mapping_expires_at__gt=timezone.now(),
            )
            .first()
        )
        return TokenResolution(
            token=token,
            context_available=bool(token and token.context_expires_at > timezone.now()),
        )
