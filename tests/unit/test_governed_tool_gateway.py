from __future__ import annotations

from typing import Any

import pytest

from dare_framework.plan.types import Envelope
from dare_framework.tool._internal.control.approval_manager import (
    ApprovalEvaluation,
    ApprovalEvaluationStatus,
)
from dare_framework.tool._internal.governed_tool_gateway import (
    ApprovalInvokeContext,
    GovernedToolGateway,
)
from dare_framework.tool.types import CapabilityDescriptor, CapabilityType, ToolResult


class _RecordingDelegateGateway:
    def __init__(self, capability: CapabilityDescriptor) -> None:
        self._capability = capability
        self.invoke_calls: list[dict[str, Any]] = []

    def list_capabilities(self) -> list[CapabilityDescriptor]:
        return [self._capability]

    async def invoke(self, capability_id: str, *, envelope: Envelope, **params: Any) -> ToolResult:
        self.invoke_calls.append(
            {
                "capability_id": capability_id,
                "envelope": envelope,
                "params": dict(params),
            }
        )
        return ToolResult(success=True, output={"ok": True})


class _RecordingApprovalManager:
    def __init__(self) -> None:
        self.evaluate_calls: list[dict[str, Any]] = []

    async def evaluate(
        self,
        *,
        capability_id: str,
        params: dict[str, Any],
        session_id: str | None,
        reason: str,
    ) -> ApprovalEvaluation:
        self.evaluate_calls.append(
            {
                "capability_id": capability_id,
                "params": dict(params),
                "session_id": session_id,
                "reason": reason,
            }
        )
        return ApprovalEvaluation(status=ApprovalEvaluationStatus.ALLOW)


@pytest.mark.asyncio
async def test_governed_gateway_approval_uses_effective_params_with_context_collision() -> None:
    capability = CapabilityDescriptor(
        id="run_command",
        type=CapabilityType.TOOL,
        name="run_command",
        description="run command",
        input_schema={"type": "object", "properties": {}},
        metadata={"requires_approval": True},
    )
    delegate = _RecordingDelegateGateway(capability)
    approval_manager = _RecordingApprovalManager()
    gateway = GovernedToolGateway(delegate, approval_manager=approval_manager)

    runtime_context = object()
    envelope = Envelope()
    result = await gateway.invoke(
        capability.id,
        approval=ApprovalInvokeContext(runtime_context=runtime_context),
        envelope=envelope,
        command="echo hello",
        context="tool-arg-context",
    )

    assert result.success is True
    assert approval_manager.evaluate_calls
    assert approval_manager.evaluate_calls[0]["params"] == {
        "command": "echo hello",
        "context": "tool-arg-context",
    }

    assert delegate.invoke_calls
    delegate_params = delegate.invoke_calls[0]["params"]
    assert delegate_params["command"] == "echo hello"
    assert delegate_params["context"] == "tool-arg-context"
