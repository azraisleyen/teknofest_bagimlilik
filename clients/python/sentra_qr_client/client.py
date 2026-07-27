import secrets
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx

JsonObject = dict[str, Any]
Sleep = Callable[[float], None]
UniformSampler = Callable[[float, float], float]


@dataclass(frozen=True)
class ClientResult:
    status_code: int
    data: JsonObject


class SentraQrClient:
    def __init__(
        self,
        base_url: str,
        credential: str,
        connect_timeout: float = 2,
        read_timeout: float = 5,
        max_retries: int = 2,
        *,
        sleeper: Sleep = time.sleep,
        jitter_sampler: UniformSampler | None = None,
    ) -> None:
        if connect_timeout <= 0 or read_timeout <= 0:
            raise ValueError("HTTP timeouts must be positive")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.base_url = base_url.rstrip("/")
        self._credential = credential
        self.timeout = httpx.Timeout(read_timeout, connect=connect_timeout)
        self.max_retries = max_retries
        self._sleep = sleeper
        # SystemRandom obtains entropy from the operating system rather than the
        # deterministic PRNG flagged by Bandit B311. Injection keeps retry tests deterministic.
        self._sample_jitter = jitter_sampler or secrets.SystemRandom().uniform

    def _post(
        self,
        path: str,
        payload: Mapping[str, Any],
        key: str,
        retry_safe: bool = True,
    ) -> ClientResult:
        headers = {"Authorization": f"Bearer {self._credential}", "Idempotency-Key": key}
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    self.base_url + path,
                    json=dict(payload),
                    headers=headers,
                    timeout=self.timeout,
                )
                data = response.json()
                if not isinstance(data, dict):
                    raise RuntimeError("SENTRA QR endpoint returned a non-object JSON response")
                return ClientResult(response.status_code, data)
            except (httpx.TimeoutException, httpx.NetworkError):
                if not retry_safe or attempt == self.max_retries:
                    raise RuntimeError("SENTRA QR endpoint unavailable") from None
                exponential_delay = (2**attempt) * 0.1
                self._sleep(exponential_delay + self._sample_jitter(0.0, 0.05))
        raise RuntimeError("SENTRA QR retry loop exhausted unexpectedly")

    def start_content_event(self, payload: Mapping[str, Any]) -> ClientResult:
        return self._post("/api/v1/qr/events", payload, str(payload["idempotency_key"]))

    def end_content_event(self, payload: Mapping[str, Any]) -> ClientResult:
        return self._post("/api/v1/qr/events", payload, str(payload["event_id"]))

    def report_display_event(
        self, payload: Mapping[str, Any], idempotency_key: str
    ) -> ClientResult:
        return self._post("/api/v1/qr/display-events", payload, idempotency_key)

    def health_check(self) -> ClientResult:
        response = httpx.get(self.base_url + "/api/v1/qr/health", timeout=self.timeout)
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("SENTRA QR endpoint returned a non-object JSON response")
        return ClientResult(response.status_code, data)
