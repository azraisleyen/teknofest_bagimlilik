from urllib.parse import urlparse

ALLOWED = {"www.google.com", "google.com", "maps.google.com"}


def safe(url):
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in ALLOWED and not p.username


def test_allowlist():
    assert safe("https://www.google.com/maps?api=1&query=x")
    assert not safe("file:///etc/passwd")
    assert not safe("https://127.0.0.1/x")
    assert not safe("https://google.com@evil.example/x")
