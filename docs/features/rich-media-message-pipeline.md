---
change_ids: ["agentscope-d1-d3-message-pipeline", "transport-typed-payload-cutover", "message-input-boundary-cleanup"]
doc_kind: feature
topics: ["message-schema", "rich-media", "transport", "agent-input", "a2a"]
created: 2026-03-09
updated: 2026-03-09
status: active
mode: openspec
---

# Feature: rich-media-message-pipeline

## Scope

Land the rich-media message pipeline as a single governed delivery topic: canonical `Message`
schema cutover, typed transport payloads, public agent input normalization, and A2A/example
entrypoint migration to `text + attachments + data`.

This topic intentionally excludes the later runtime-lifecycle redesign for message delivery,
caching, compression, resume, and dispatch orchestration.

## OpenSpec Artifacts

- Proposal:
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/proposal.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/proposal.md`
  - `openspec/changes/archive/2026-03-09-message-input-boundary-cleanup/proposal.md`
- Design:
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/design.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/design.md`
  - `openspec/changes/archive/2026-03-09-message-input-boundary-cleanup/design.md`
- Specs:
  - `openspec/specs/rich-media-message-schema/spec.md`
  - `openspec/specs/transport-channel/spec.md`
  - `openspec/specs/interaction-dispatch/spec.md`
  - `openspec/specs/chat-runtime/spec.md`
  - `openspec/specs/typed-transport-replies/spec.md`
- Tasks:
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/tasks.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/tasks.md`
  - `openspec/changes/archive/2026-03-09-message-input-boundary-cleanup/tasks.md`

## Governance Anchors

- `docs/guides/Development_Constraints.md`
- `docs/guides/Documentation_First_Development_SOP.md`
- `docs/design/Interfaces.md`
- `docs/design/modules/context/README.md`
- `docs/design/modules/transport/README.md`
- `docs/design/modules/model/README.md`
- `docs/design/modules/agent/README.md`

## Evidence

### Commands

- `openspec validate --spec-dir openspec/specs`
- `git diff --check`

### Results

- `openspec validate --spec-dir openspec/specs`: baseline spec tree is valid before the
  implementation PR updates runtime code and evidence.
- `git diff --check`: docs-only intent branch stays formatting-clean and preserves the governed
  feature-doc template contract.

### Behavior Verification

- Happy path: this intent record establishes the active governed feature topic that the later
  implementation PR will update while landing the message-schema cutover.
- Error/fallback path: runtime delivery/caching/resume redesign remains explicitly out of scope for
  this feature topic and must land through a separate follow-up intent/change.

### Risks and Rollback

- Risk: the implementation PR still needs to append concrete runtime verification evidence and
  update the active feature record before merge.
- Rollback: if the topic scope changes materially, replace this intent record before merging the
  implementation PR instead of silently repurposing it.

### Review and Merge Gate Links

- Intent PR: `TBD`
- Implementation PR: `https://github.com/zts212653/Deterministic-Agent-Runtime-Engine/pull/204`
- Review request: `TBD`
