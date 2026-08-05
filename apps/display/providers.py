from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class NormalizedDetectionSignal:
    signal_id: str
    source_id: str
    event_type: str
    occurred_at: datetime
    confidence: float
    candidate_age_band: str | None
    model_id: str
    model_version: str
    # focus_roi is intentionally excluded from persisted/server contracts.


class DetectionProvider(Protocol):
    def next_signal(self) -> NormalizedDetectionSignal | None: ...


class SignalNormalizer(Protocol):
    def normalize(self, raw: object) -> NormalizedDetectionSignal: ...


class DecisionEngine:
    """Small, model-independent stability policy for normalized signals."""

    def __init__(self, minimum_confidence=0.75, required_hits=3):
        self.minimum_confidence = minimum_confidence
        self.required_hits = required_hits

    def confirmed(self, signals: list[NormalizedDetectionSignal]) -> bool:
        eligible = [item for item in signals if item.confidence >= self.minimum_confidence]
        return len(eligible) >= self.required_hits
