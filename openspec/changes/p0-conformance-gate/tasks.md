## 1. Define Gate Scope

- [ ] 1.1 定义 `p0-gate` 覆盖的三类不变量与验收阈值。
- [ ] 1.2 明确每类不变量对应的测试文件与责任模块。
- [ ] 1.3 定义标准失败标签与 CI summary 输出格式。

## 2. Build P0 Test Suite

- [ ] 2.1 新增集成测试覆盖安全门控主链路（allow/deny/approve_required）。
- [ ] 2.2 新增集成测试覆盖 `step_driven` 执行闭环。
- [ ] 2.3 新增集成测试覆盖默认 event log hash-chain/replay。
- [x] 2.4 增加关键单测确保契约字段与错误码稳定。  
  Evidence: `dare_framework/transport/_internal/adapters.py`，`tests/unit/test_transport_adapters.py`（新增 slash 命令到 `resource:action` 的标准化与审批参数提取断言）；`examples/05-dare-coding-agent-enhanced/cli.py`、`examples/06-dare-coding-agent-mcp/cli.py`（审批 action 调用统一为 `invoke(action, **params)`）  
  Commands: `.venv/bin/pytest -q tests/unit/test_transport_adapters.py::test_stdio_slash_command_maps_to_resource_action_id tests/unit/test_transport_adapters.py::test_stdio_slash_command_extracts_approval_action_params` => `2 passed`；`.venv/bin/pytest -q tests/unit/test_transport_adapters.py tests/unit/test_interaction_dispatcher.py tests/unit/test_transport_channel.py tests/integration/test_client_cli_flow.py` => `33 passed, 1 warning`；`.venv/bin/pytest -q tests/unit/test_examples_cli.py tests/unit/test_examples_cli_mcp.py` => `22 passed, 1 warning`  
  Last Updated: `2026-03-01`

## 3. CI Integration

- [ ] 3.1 在 CI workflow 增加 `p0-gate` job 与命令入口。
- [ ] 3.2 将 `p0-gate` 配置为主分支 required check。
- [ ] 3.3 输出标准化门禁报告（通过率、失败类型、建议排查点）。

## 4. Operationalization

- [ ] 4.1 更新开发文档，说明本地运行与故障排查流程。
- [ ] 4.2 在发布流程增加 `p0-gate` 结果归档步骤。
- [ ] 4.3 制定 flaky 用例处理规则与时限。

## 5. Baseline Recovery Evidence

- [x] 5.1 修复审批异常语义回归，恢复安全门控关键失败分支的结构化错误前缀契约。
  Evidence: `dare_framework/tool/_internal/governed_tool_gateway.py`
  Commands: `.venv/bin/pytest -q tests/unit/test_dare_agent_security_boundary.py::test_tool_loop_approval_evaluate_exception_returns_structured_failure tests/unit/test_dare_agent_security_boundary.py::test_tool_loop_approval_wait_exception_returns_structured_failure` => `2 passed`；`.venv/bin/pytest -q` => `504 passed, 12 skipped, 1 warning`
  Last Updated: `2026-03-01`
