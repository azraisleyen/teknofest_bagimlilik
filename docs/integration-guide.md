# Integration guide
The external content orchestrator alone selects content/age band/modes and lifecycle timestamps. SENTRA validates, authenticates, persists event context, creates URLs, and returns general/dynamic results. Use `clients/python/SentraQrClient`: start with a stable body/header idempotency key, report technical display state, then end with the same event ID. Use `clients/web/qr-controller.js` for atomic, generation-safe rendering; keep credentials server-side. On timeout/render/conflict call `general(reason)` and retain 115.

Never send camera media, face/person/tracker IDs, exact ages, gender, phones, GPS, boxes, embeddings, model tensors, or inference detail. The QR system is not an AI decision maker.
