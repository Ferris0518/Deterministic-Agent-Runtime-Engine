## 1. Canonical EventLog Implementation

- [x] 1.1 新增 `SQLiteEventLog` 并实现 `append/query/replay/verify_chain`。
- [x] 1.2 定义并落地事件表结构与 hash-chain 字段。
- [x] 1.3 固定 payload 序列化口径（稳定排序 JSON）。
- [x] 1.4 增加 hash 版本字段以支持后续兼容迁移。

## 2. Builder and Config Wiring

- [x] 2.1 在 builder 中增加默认 event log 自动装配逻辑。
- [x] 2.2 在 config 中增加 event log 开关与路径配置项。
- [x] 2.3 保持显式 `with_event_log` 注入优先级高于默认装配。

## 3. Observability and Runtime Compatibility

- [x] 3.1 验证 trace-aware event bridge 与默认实现协同工作。
- [x] 3.2 统一关键会话事件写入字段，确保 query/replay 可消费。
- [x] 3.3 补充运行时错误处理，确保 event 写入失败不导致静默丢失。

## 4. Tests and Migration

- [x] 4.1 迁移并启用 canonical `test_event_log`，移除 skip 依赖。
- [x] 4.2 新增单测验证 hash-chain 篡改检测。
- [x] 4.3 新增集成测试验证 replay 最小快照行为。
- [x] 4.4 增加兼容测试覆盖 builder 默认装配与显式注入两路径。

## Evidence

- Runtime:
  - `dare_framework/event/_internal/sqlite_event_log.py`
  - `dare_framework/event/types.py`
  - `dare_framework/observability/_internal/event_trace_bridge.py`
  - `dare_framework/agent/dare_agent.py`
  - `dare_framework/agent/_internal/session_orchestrator.py`
  - `dare_framework/agent/builder.py`
  - `dare_framework/config/types.py`
  - `dare_framework/config/__init__.py`
- Tests:
  - `tests/unit/test_event_sqlite_event_log.py`
  - `tests/unit/test_event_log.py`
  - `tests/unit/test_builder_security_boundary.py`
  - `tests/unit/test_five_layer_agent.py`
- Commands:
  - `.venv/bin/pytest -q tests/unit/test_event_sqlite_event_log.py tests/unit/test_builder_security_boundary.py tests/unit/test_five_layer_agent.py` => `43 passed`
  - `.venv/bin/pytest -q` => `504 passed, 12 skipped, 1 warning`
- Last Updated: `2026-03-01`
