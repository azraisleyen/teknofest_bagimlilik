from dataclasses import dataclass

from .models import ContentPackage


@dataclass(frozen=True)
class AudienceDecision:
    age_band: str
    audience_mode: str


class AudienceResolver:
    """Converts stabilized model output into a non-identifying content category."""

    @staticmethod
    def resolve(candidate_bands: list[str], stable: bool = True) -> AudienceDecision:
        normalized = {band for band in candidate_bands if band in ContentPackage.AgeBand.values}
        if not stable or len(normalized) != 1:
            return AudienceDecision(ContentPackage.AgeBand.GENERAL, "GENERAL_FALLBACK")
        band = normalized.pop()
        if band == ContentPackage.AgeBand.GENERAL:
            return AudienceDecision(band, "GENERAL_FALLBACK")
        return AudienceDecision(band, "STABILIZED_BAND")


class ContentSelector:
    @staticmethod
    def select(decision: AudienceDecision) -> ContentPackage | None:
        package = (
            ContentPackage.objects.filter(active=True, age_band=decision.age_band)
            .order_by("priority", "content_id")
            .first()
        )
        if package is not None:
            return package
        return (
            ContentPackage.objects.filter(active=True, age_band=ContentPackage.AgeBand.GENERAL)
            .order_by("priority", "content_id")
            .first()
        )
