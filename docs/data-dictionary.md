# Data dictionary
All IDs are UUIDs unless stated; timestamps are UTC. Event/token tables retain mappings 24 h and contexts per policy; survey retention requires approved research schedule; interaction/audit retention is configurable operational policy. No row contains direct person identity.

- **Device**: ID/name/location/version/status/last-seen support installation operations; credential hash/prefix/revocation authenticate devices; admins only; deletion protected where referenced.
- **QrEventContext**: external event/idempotency/content/version/category/modes/times/end/status/schema support lifecycle and aggregates; device operators/auditors; cascade only through controlled retention.
- **QrToken**: random record ID, SHA-256 token hash, event, key version, state/expiry/revocation support lookup/rotation; never plain token; admins read metadata; cascade with event.
- **QrDisplaySession**: event/device/mode/start/end/fallback/visual version measure technical display behavior; aggregate access; nullable event on retention.
- **YedamCenter**: verified public center name/geography/address/map/place/115/source/verifier/times/active; center managers; protected mappings.
- **LocationCenterMapping**: fixed installation ID, primary/backup, verification/active/times select referrals; center managers.
- **SurveyDefinition/Question/Choice**: centrally versioned text, ordering, type/options/status/times; survey managers; protected after responses.
- **SurveySession/Response**: short random browser session, optional token mapping, state/times, question and JSON answer; research managers; responses cascade with session.
- **QrInteraction**: random ID, optional token, allowlisted action, short anonymous session, time; aggregate analysts; token nullable.
- **AuditLog**: actor/action/object reference/non-sensitive metadata/time; read-only auditors; immutable.
