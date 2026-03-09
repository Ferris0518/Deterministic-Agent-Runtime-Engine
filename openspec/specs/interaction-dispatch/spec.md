# interaction-dispatch Specification

## Purpose
Define deterministic interaction dispatch boundaries so action and control routing stays isolated from prompt execution.

## Requirements

### Requirement: Action dispatch is isolated from control and prompt execution
The system SHALL provide an `ActionHandlerDispatcher` dedicated to deterministic action routing only.

- `ActionHandlerDispatcher` MUST route only `resource:action` requests.
- `ActionHandlerDispatcher` MUST NOT parse prompt messages or handle runtime control signals.
- Action dispatch MUST be driven by stable `ResourceAction` identifiers.

#### Scenario: Action dispatcher ignores control responsibility
- **GIVEN** a runtime control signal such as `interrupt`
- **WHEN** the interaction layer handles the signal
- **THEN** the control path does not call `ActionHandlerDispatcher`
- **AND** action dispatcher remains responsible only for action ids

### Requirement: Action handlers are discoverable and dispatch deterministically
The system SHALL provide a registry that allows domains to register deterministic handlers for `action` inputs.

- Each handler MUST declare which `(resource, action)` pairs it supports.
- For a given `(resource, action)` request, the dispatch MUST select exactly one handler or return a clear error response.

#### Scenario: Resource action routes to a single handler
- **GIVEN** two registered handlers where only one supports `(resource="tools", action="list")`
- **WHEN** an action request for `tools:list` is received
- **THEN** the dispatcher invokes the matching handler
- **AND** it does not invoke non-matching handlers

### Requirement: Deterministic action/control responses are correlated to requests
For deterministic action/control handling, the system SHALL emit responses correlated to the originating request.

- The response `TransportEnvelope.reply_to` MUST be set to the request envelope `id` when available.

#### Scenario: Response sets reply_to
- **GIVEN** an action/control request envelope with `id="req-123"`
- **WHEN** the handler completes successfully
- **THEN** the system sends a response envelope with `reply_to="req-123"`

### Requirement: Deterministic handler errors use typed payload replies
The system SHALL return deterministic action/control/message errors using typed payload replies aligned with `TransportEnvelope.kind`.

- Successful action results MUST populate `ActionPayload.ok=True` and `ActionPayload.result`.
- Failed action results MUST populate `ActionPayload.ok=False` with deterministic `code` and `reason`.
- Successful control results MUST populate `ControlPayload.ok=True` and `ControlPayload.result`.
- Failed control results MUST populate `ControlPayload.ok=False` with deterministic `code` and `reason`.
- Unsupported action operations MUST use `code="UNSUPPORTED_OPERATION"`.

#### Scenario: Action timeout returns typed error
- **GIVEN** an action request exceeds configured timeout
- **WHEN** the runtime returns an error response
- **THEN** the payload is an `ActionPayload`
- **AND** it includes `code="ACTION_TIMEOUT"`
- **AND** `reply_to` points to the request id

### Requirement: Standard runtime control signals are provided and dispatchable
The system SHALL provide a stable set of runtime control signals (`AgentControl`) for deterministic interaction handling:
- `interrupt`
- `pause`
- `retry`
- `reverse`

The interaction layer MUST NOT invoke the agent LLM execution path for control signals.
Runtime control signals MUST be routed to a deterministic control handling path (e.g. `ControlHandler`).

#### Scenario: Pause is not executed as a prompt
- **GIVEN** an inbound control envelope with `kind="control"` and `payload=<ControlPayload control_id="pause">`
- **WHEN** the interaction layer processes the envelope
- **THEN** it does not invoke the LLM-driven agent execution path

### Requirement: Control handling is performed by a dedicated control handler
The system SHALL provide a dedicated `AgentControlHandler` for runtime controls.

- `AgentControlHandler` MUST map `AgentControl` values to agent control methods.
- Control handling MUST NOT require registering control handlers in `ActionHandlerDispatcher`.
- `interrupt` MUST cancel the current execution operation owned by agent runtime.

#### Scenario: Interrupt maps to agent control path
- **GIVEN** an inbound control envelope with `payload=<ControlPayload control_id="interrupt">`
- **WHEN** control handling executes
- **THEN** the runtime invokes the agent interrupt method
- **AND** the current execution operation is cancelled

### Requirement: Action handling has bounded execution time
The system SHALL enforce a timeout for action handler execution in a single session runtime.

- Action execution timeout MUST be configurable.
- On timeout, runtime MUST terminate the action attempt and return structured error payload.

#### Scenario: Long action is terminated by timeout
- **GIVEN** an action handler execution exceeds timeout
- **WHEN** timeout is reached
- **THEN** runtime terminates the action attempt
- **AND** runtime returns `ActionPayload(ok=False, code="ACTION_TIMEOUT")`

### Requirement: Standard action identifiers are provided for core interaction domains
The system SHALL provide a stable set of standard action identifiers for deterministic interaction handling in the following initial domains:
- `config`
- `tools`
- `mcp`
- `skills`
- `model`
- `actions`

Action identifiers MUST be expressible as `(resource, action)` pairs and SHOULD be representable as a stable enum or registry so handlers and clients can avoid free-form string drift.

#### Scenario: Tools list action uses a stable identifier
- **GIVEN** a client wants to request tool introspection without invoking the agent LLM path
- **WHEN** it sends an action request for `tools:list`
- **THEN** the dispatcher routes the request through the deterministic action handling path
- **AND** the request can be matched by handlers without relying on parsing natural language

### Requirement: Registered actions are discoverable for clients
The system SHALL provide a deterministic action discovery operation.

- `actions:list` MUST return all currently registered action identifiers for the active channel/dispatcher.
- Client adapters MAY map `/` to `actions:list` for command discovery.

#### Scenario: Slash root returns available actions
- **GIVEN** a stdio client sends `/`
- **WHEN** adapter maps it to action `actions:list`
- **THEN** the runtime returns a deterministic list of supported action ids

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

### Requirement: Select dispatch is isolated from action, control, and prompt execution
The system SHALL provide a deterministic dispatch path for `select` envelopes that is separate from prompt execution, action dispatch, and runtime control handling.

- `select` dispatch MUST NOT enter the LLM prompt execution path.
- `select` dispatch MUST NOT be routed through `ActionHandlerDispatcher`.
- `select` dispatch MUST preserve `reply_to` correlation semantics for answered selections.

#### Scenario: Select answer does not execute as a prompt
- **GIVEN** an inbound `TransportEnvelope(kind="select")`
- **WHEN** the interaction layer processes the envelope
- **THEN** it does not invoke the LLM-driven agent execution path
- **AND** it does not route the envelope through `ActionHandlerDispatcher`

### Requirement: Approval interactions use select ask and answered semantics
The deterministic interaction layer SHALL represent approval interactions as `select` payloads.

- Pending approval MUST use `SelectPayload(select_domain="approval", select_kind="ask")`.
- Resolved approval MUST use `SelectPayload(select_domain="approval", select_kind="answered")`.
- The runtime MUST NOT rely on message event aliases such as `approval.pending` or `approval.resolved` as the primary approval contract.

#### Scenario: Approval resolution replies to the pending request
- **GIVEN** an approval request was emitted as `kind="select"` with `select_kind="ask"`
- **WHEN** the user resolves the approval
- **THEN** the resolution is expressed as `kind="select"` with `select_kind="answered"`
- **AND** the reply references the originating request envelope when available
