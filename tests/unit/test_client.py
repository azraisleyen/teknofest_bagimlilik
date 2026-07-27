from unittest.mock import Mock, call

import httpx
import pytest
from sentra_qr_client import SentraQrClient


def test_retry_backoff_uses_exponential_delay_and_jitter(monkeypatch):
    post = Mock(
        side_effect=[
            httpx.ConnectError("offline"),
            httpx.ReadTimeout("slow"),
            Mock(status_code=201, json=Mock(return_value={"status": "accepted"})),
        ]
    )
    sleep = Mock()
    monkeypatch.setattr("sentra_qr_client.client.httpx.post", post)
    monkeypatch.setattr("sentra_qr_client.client.time.sleep", sleep)
    monkeypatch.setattr("sentra_qr_client.client._retry_jitter", lambda: 0.025)

    result = SentraQrClient("https://sentra.example", "credential").report_display_event(
        {"event_type": "DISPLAY_STARTED"}, "event-key"
    )

    assert result.status_code == 201
    assert post.call_count == 3
    assert sleep.call_args_list == [call(0.125), call(0.225)]


def test_retry_exhaustion_preserves_error_semantics(monkeypatch):
    monkeypatch.setattr(
        "sentra_qr_client.client.httpx.post",
        Mock(side_effect=httpx.ConnectError("offline")),
    )
    monkeypatch.setattr("sentra_qr_client.client.time.sleep", Mock())
    monkeypatch.setattr("sentra_qr_client.client._retry_jitter", lambda: 0.0)

    with pytest.raises(RuntimeError, match="SENTRA QR endpoint unavailable"):
        SentraQrClient("https://sentra.example", "credential").start_content_event(
            {"idempotency_key": "event-key"}
        )
