# Threat model
| Threat / asset / actor / path | Mitigation | Residual risk / operational control |
|---|---|---|
| Token prediction/replay/photo sharing; context; observer | 256-bit HMAC opaque token, expiry/revoke, no-store | Shared photos work until expiry; shorten/revoke and disclose |
| Forged event/credential leak; lifecycle; attacker | hashed per-device secret, TLS, constant-time check, rotation, idempotency | endpoint compromise; monitor/revoke |
| Bots/rate abuse; survey | cookie grouping, honeypot, minimum-time policy, cache/Redis rate controls, DB uniqueness | distributed bots; monitor aggregates |
| XSS/CSRF/open redirect/SSRF; browser/server | template escaping, CSRF, CSP, fixed external links, HTTPS host allowlist, no URL fetch | admin content error; review imports |
| Admin compromise; all metadata | Django RBAC, mandatory production TOTP, immutable audit | phishing/session theft; enrolment review and alerting |
| Logs leak tokens/secrets/comments | no bodies, correlation IDs, authorization/cookie redaction policy | operator errors; access/retention controls |
| Race/DB outage | atomic/row locks/partial unique constraint; static general fallback | SQLite differs; PostgreSQL concurrency tests before launch |
| Wrong/stale center | verified import, stale command, primary/backup, official directory/115 fallback | human source error; dual review |
| Malicious extra fields | JSON Schema `additionalProperties:false`, body limit | novel encodings; fuzz and dependency updates |
| Expired QR enumeration | identical HTTP 200 general page | timing differences; monitor and normalize infrastructure |
