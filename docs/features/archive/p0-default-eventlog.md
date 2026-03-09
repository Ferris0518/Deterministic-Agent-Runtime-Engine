---
change_ids: ["p0-default-eventlog"]
doc_kind: feature
topics: ["event-log", "sqlite", "hash-chain", "builder-defaults"]
created: 2026-03-01
updated: 2026-03-01
status: archived
mode: openspec
---

# Feature: p0-default-eventlog

## Scope
提供 canonical `SQLiteEventLog` 的完整契约实现，并接入 builder/config 的默认装配路径，保证未显式注入 event log 时可按配置启用默认审计链。

## OpenSpec Artifacts
- Proposal: `openspec/changes/p0-default-eventlog/proposal.md`
- Design: `openspec/changes/p0-default-eventlog/design.md`
- Specs:
  - `openspec/changes/p0-default-eventlog/specs/default-event-log/spec.md`
  - `openspec/changes/p0-default-eventlog/specs/core-runtime/spec.md`
  - `openspec/changes/p0-default-eventlog/specs/session-loop/spec.md`
  - `openspec/changes/p0-default-eventlog/specs/observability/spec.md`
- Tasks: `openspec/changes/p0-default-eventlog/tasks.md`

## Progress
- 已完成：1.1~1.4、2.1~2.3、3.1~3.3、4.1~4.4
- 待完成：无（等待 review/merge gate）

## Evidence

### Commands
- `.venv/bin/pytest -q tests/unit/test_event_sqlite_event_log.py tests/unit/test_builder_security_boundary.py tests/unit/test_five_layer_agent.py`
- `.venv/bin/pytest -q`

### Results
- 定向验证：`43 passed`
- 全量回归：`504 passed, 12 skipped, 1 warning`

### Behavior Verification
- Happy path: 开启 `config.event_log.enabled=true` 时，未显式注入 event log 也会自动装配默认 `SQLiteEventLog`，并通过 trace-aware 包装接入运行时。
- Replay path: 默认装配路径下可从 `session.start` 回放有序事件窗口，且 payload 包含 `task_id/run_id/session_id` 最小会话字段。
- Trace path: trace-aware bridge 会将 trace 上下文写入 sqlite payload，并保留 `_trace` 与顶层 `trace_id/span_id/trace_flags` 可查询字段。
- Error/fallback path: event 写入失败会抛出带事件类型上下文的 `EventLogWriteError`，避免静默丢失；旧 sqlite 表缺失 `hash_version` 列时会自动兼容迁移并保持链路可验。
- Integrity path: 篡改持久化 `payload_json` 后，`verify_chain()` 返回 `False`。

### Risks and Rollback
- 风险：默认启用 event log 可能引入额外 I/O。
- 风险：`hash_version` 后续升级需要兼容老链路校验。
- 回滚：将 `config.event_log.enabled` 设置为 `false`，或显式 `with_event_log(...)` 注入替代实现。

### Review and Merge Gate Links
- Pending in current branch（待提交 PR 后补充链接）。
