import secrets
import time
from dataclasses import dataclass

import httpx


def _retry_jitter():
    return secrets.randbelow(5_000_000) / 100_000_000


@dataclass(frozen=True)
class ClientResult:
    status_code: int
    data: dict


class SentraQrClient:
    def __init__(self, base_url, credential, connect_timeout=2, read_timeout=5, max_retries=2):
        self.base_url = base_url.rstrip("/")
        self._credential = credential
        self.timeout = httpx.Timeout(read_timeout, connect=connect_timeout)
        self.max_retries = max_retries

    def _post(self, path, payload, key, retry_safe=True):
        headers = {"Authorization": f"Bearer {self._credential}", "Idempotency-Key": key}
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.post(
                    self.base_url + path, json=payload, headers=headers, timeout=self.timeout
                )
                return ClientResult(response.status_code, response.json())
            except (httpx.TimeoutException, httpx.NetworkError):
                if not retry_safe or attempt == self.max_retries:
                    raise RuntimeError("SENTRA QR endpoint unavailable") from None
                time.sleep((2**attempt) * 0.1 + _retry_jitter())

    def start_content_event(self, payload):
        return self._post("/api/v1/qr/events", payload, payload["idempotency_key"])

    def end_content_event(self, payload):
        return self._post("/api/v1/qr/events", payload, payload["event_id"])

    def report_display_event(self, payload, idempotency_key):
        return self._post("/api/v1/qr/display-events", payload, idempotency_key)

    def health_check(self):
        r = httpx.get(self.base_url + "/api/v1/qr/health", timeout=self.timeout)
        return ClientResult(r.status_code, r.json())
