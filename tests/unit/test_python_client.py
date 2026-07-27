from typing import Any

import pytest

httpx = pytest.importorskip("httpx")

from sentra_qr_client import SentraQrClient  # noqa: E402


class StubResponse:
    status_code = 200

    def json(self) -> dict[str, str]:
        return {"status": "ok"}


def test_retry_uses_injected_secure_jitter_source(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0
    delays: list[float] = []
    jitter_bounds: list[tuple[float, float]] = []

    def post(*args: Any, **kwargs: Any) -> StubResponse:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise httpx.ConnectError("offline")
        return StubResponse()

    def jitter(low: float, high: float) -> float:
        jitter_bounds.append((low, high))
        return 0.025

    monkeypatch.setattr(httpx, "post", post)
    client = SentraQrClient(
        "https://example.invalid",
        "credential",
        sleeper=delays.append,
        jitter_sampler=jitter,
    )

    result = client.start_content_event({"idempotency_key": "stable-key"})

    assert result.data == {"status": "ok"}
    assert calls == 3
    assert delays == pytest.approx([0.125, 0.225])
    assert jitter_bounds == [(0.0, 0.05), (0.0, 0.05)]


def test_client_rejects_invalid_retry_configuration() -> None:
    with pytest.raises(ValueError, match="max_retries"):
        SentraQrClient("https://example.invalid", "credential", max_retries=-1)
