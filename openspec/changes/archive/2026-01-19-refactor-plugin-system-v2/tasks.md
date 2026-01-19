## 1. Design + Contracts
- [x] 1.1 Add `IExecutionControl.wait_for_human(checkpoint_id, reason)` to the Kernel contract and define the WORM event requirements for “waiting”.
- [x] 1.2 Define v2 entrypoint groups (new names) and a v2 plugin loading contract (what is selectable vs multi-load).
- [x] 1.3 Define v2 runtime configuration keys for selecting/filtering components (especially model adapter selection by name and validator filtering).
- [x] 1.4 Define the migration map from legacy `dare_framework/core/*` types to v2-aligned modules (and enumerate which v1-only modules will be removed).

## 2. Core Flow Adjustments (v2)
- [x] 2.1 Update the orchestrator’s HITL paths to call `pause()` → `wait_for_human()` → `resume()` for `APPROVE_REQUIRED` decisions.
- [x] 2.2 Add/adjust tests to assert the `exec.waiting_human` event is recorded for approval-required paths.

## 3. Plugin System (Entrypoints + Managers)
- [x] 3.1 Define v2 entrypoint groups (new names) for all plugin-extensible categories (tools/model_adapters/validators/planners/remediators/protocol_adapters/hooks/config_providers and optional placeholders like memory/prompt_stores/skills).
- [x] 3.2 Define v2 component manager interfaces for each category, and ship no-op default implementations.
  - [x] Each interface MUST be documented with clear docstrings/comments describing its purpose, design goals, and intended selection/filtering semantics (even if the default behavior is no-op).
  - [x] model adapter: document “select by configured component name”.
  - [x] validators: document “load all enabled, filter by config, sort by `order`, return a collection”.
  - [x] other categories: document whether they are single-select or multi-load and how config filtering should apply.
- [x] 3.3 Wire v2 `AgentBuilder` to optionally assemble components via injected managers (entrypoints+config), while keeping explicit `.with_*()` overrides supported and sufficient for a working agent.

## 4. Legacy Migration + Deletion
- [x] 4.1 Migrate shared types out of `dare_framework/core/*` into v2-aligned modules and update Kernel/components to stop importing `dare_framework.core.*`.
- [x] 4.2 Remove v1-only contracts and implementations after the migration (including old composition managers if replaced).

## 5. Verification Updates (examples/tests/docs)
- [x] 5.1 Adapt `examples/coding-agent/openai_adapter.py` to the v2 contracts and plugin system (keep as verification).
- [x] 5.2 Adapt `examples/coding-agent/real_model_agent.py` and any referenced helpers to v2.
- [x] 5.3 Update unit/integration tests that currently depend on v1 composition/entrypoint group names.
- [x] 5.4 Update documentation references (developer docs + architecture overview) to point to the new plugin groups and v2 config keys.

## 6. Validation
- [x] 6.1 Run `openspec validate refactor-plugin-system-v2 --strict` and fix all issues.
- [x] 6.2 Run `pytest` (and `ruff`/`black`/`mypy` when available) and fix regressions introduced by the refactor.
