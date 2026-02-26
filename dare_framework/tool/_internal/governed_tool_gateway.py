"""Gateway-level tool invocation governance (approval + execution).

This module keeps policy/approval decisions at the tool invocation boundary so
agent orchestration can focus on the loop itself.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from dare_framework.tool._internal.control.approval_manager import (
    ApprovalDecision,
    ApprovalEvaluationStatus,
    ToolApprovalManager,
)
from dare_framework.tool.kernel import IToolGateway
from dare_framework.tool.types import CapabilityDescriptor, ToolResult
from dare_framework.transport.interaction.payloads import build_approval_pending_payload
from dare_framework.transport.types import (
    EnvelopeKind,
    TransportEnvelope,
    TransportEventType,
    new_envelope_id,
)

if TYPE_CHECKING:
    from dare_framework.context import Context
    from dare_framework.plan.types import Envelope
    from dare_framework.transport.kernel import AgentChannel


class GovernedToolGateway(IToolGateway):
    """IToolGateway wrapper that applies approval memory before tool execution."""

    def __init__(
        self,
        delegate: IToolGateway,
        *,
        approval_manager: ToolApprovalManager | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._delegate = delegate
        self._approval_manager = approval_manager
        self._logger = logger or logging.getLogger("dare.tool.governed_gateway")

    def list_capabilities(self) -> list[CapabilityDescriptor]:
        return self._delegate.list_capabilities()

    async def invoke(
        self,
        capability_id: str,
        *,
        envelope: Envelope,
        context: Context | None = None,
        session_id: str | None = None,
        transport: AgentChannel | None = None,
        tool_name: str | None = None,
        tool_call_id: str | None = None,
        **params: Any,
    ) -> ToolResult:
        requires_approval = self._requires_approval(capability_id)
        if requires_approval:
            decision_error = await self._resolve_approval(
                capability_id=capability_id,
                params=params,
                session_id=session_id,
                transport=transport,
                tool_name=tool_name or capability_id,
                tool_call_id=tool_call_id or "unknown",
            )
            if decision_error is not None:
                # Return a deterministic denied result so orchestrators can treat
                # it as a normal tool outcome instead of a special side channel.
                return ToolResult(
                    success=False,
                    output={"status": "not_allow"},
                    error=decision_error,
                )

        result = await self._delegate.invoke(
            capability_id,
            envelope=envelope,
            context=context,
            **params,
        )
        return result

    def _requires_approval(self, capability_id: str) -> bool:
        descriptor = self._find_capability(capability_id)
        if descriptor is None:
            return False
        metadata = descriptor.metadata
        return bool(metadata and metadata.get("requires_approval", False))

    def _find_capability(self, capability_id: str) -> CapabilityDescriptor | None:
        for descriptor in self._delegate.list_capabilities():
            if descriptor.id == capability_id:
                return descriptor
        return None

    async def _resolve_approval(
        self,
        *,
        capability_id: str,
        params: dict[str, Any],
        session_id: str | None,
        transport: AgentChannel | None,
        tool_name: str,
        tool_call_id: str,
    ) -> str | None:
        if self._approval_manager is None:
            return "tool requires approval but no approval manager is configured"

        evaluation = await self._approval_manager.evaluate(
            capability_id=capability_id,
            params=params,
            session_id=session_id,
            reason=f"Tool {capability_id} requires approval",
        )
        if evaluation.status == ApprovalEvaluationStatus.ALLOW:
            return None
        if evaluation.status == ApprovalEvaluationStatus.DENY:
            return "tool invocation denied by approval rule"
        if evaluation.request is None:
            return "tool invocation requires approval"

        await self._emit_approval_pending_message(
            request=evaluation.request.to_dict(),
            transport=transport,
            capability_id=capability_id,
            tool_name=tool_name,
            tool_call_id=tool_call_id,
        )
        decision = await self._approval_manager.wait_for_resolution(evaluation.request.request_id)
        if decision == ApprovalDecision.ALLOW:
            return None
        return "tool invocation denied by human approval"

    async def _emit_approval_pending_message(
        self,
        *,
        request: dict[str, Any],
        transport: AgentChannel | None,
        capability_id: str,
        tool_name: str,
        tool_call_id: str,
    ) -> None:
        if transport is None:
            return
        payload = build_approval_pending_payload(
            request=request,
            capability_id=capability_id,
            tool_name=tool_name,
            tool_call_id=tool_call_id,
        )
        # Approval pending is an explicit user-choice interaction shape.
        resp = payload.get("resp")
        if isinstance(resp, dict):
            resp.setdefault(
                "options",
                [
                    {"label": "allow", "description": "Approve this tool invocation."},
                    {"label": "deny", "description": "Deny this tool invocation."},
                ],
            )

        envelope = TransportEnvelope(
            id=new_envelope_id(),
            kind=EnvelopeKind.SELECT,
            event_type=TransportEventType.APPROVAL_PENDING.value,
            payload=payload,
        )
        try:
            await transport.send(envelope)
        except Exception:
            self._logger.exception("approval pending transport send failed")


__all__ = ["GovernedToolGateway"]
