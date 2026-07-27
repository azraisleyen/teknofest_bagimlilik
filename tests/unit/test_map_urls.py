from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

from apps.yedam.services import build_map_url, safe_map_url


def test_map_builder_uses_verified_fields_without_origin():
    center = SimpleNamespace(center_name="YEDAM Test", address="Ankara", map_place_id="place-1")
    url = build_map_url(center)
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    assert safe_map_url(url)
    assert query["destination_place_id"] == ["place-1"]
    assert "origin" not in query
    assert not safe_map_url("https://google.com@evil.example/x")
