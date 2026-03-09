## MODIFIED Requirements

### Requirement: Action dispatcher routes only typed action payloads
The action dispatch subsystem SHALL route only `ActionPayload` requests and SHALL return structured action results using typed payloads.

- `ActionHandlerDispatcher.handle_action()` MUST read `resource_action` from `ActionPayload`.
- The dispatcher MUST NOT accept raw string action ids as request payloads.
- Successful action results MUST populate `ActionPayload.ok=True` and `ActionPayload.result`.
- Failed action results MUST populate `ActionPayload.ok=False` with deterministic `code/reason`.

#### Scenario: Dispatcher routes supported action payload
- **WHEN** `handle_action()` receives `TransportEnvelope(kind="action", payload=<ActionPayload resource_action="tools:list">)`
- **THEN** the matching handler is invoked
- **AND** the result is returned as a typed action payload

#### Scenario: Dispatcher rejects unsupported action id
- **WHEN** `handle_action()` receives `ActionPayload` with an unknown `resource_action`
- **THEN** the dispatcher returns `ok=False`
- **AND** the error response includes a deterministic `code` and `reason`
