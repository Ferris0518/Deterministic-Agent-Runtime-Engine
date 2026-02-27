"""Transport action/control client helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dare_framework.transport import (
    DirectClientChannel,
    EnvelopeKind,
    TransportEnvelope,
    new_envelope_id,
)
from dare_framework.transport.interaction.controls import AgentControl
from dare_framework.transport.interaction.resource_action import ResourceAction


@dataclass(frozen=True)
class ActionClientError(Exception):
    """Raised when transport action/control returns an error payload."""

    code: str
    reason: str
    target: str

    def __str__(self) -> str:
        return f"{self.code}: {self.reason} (target={self.target})"


class TransportActionClient:
    """Thin wrapper around DirectClientChannel ask() for action/control calls."""

    def __init__(self, channel: DirectClientChannel, *, timeout_seconds: float = 30.0) -> None:
        self._channel = channel
        self._timeout = timeout_seconds

    async def invoke_action(
        self,
        action: ResourceAction | str,
        **params: Any,
    ) -> Any:
        action_id = action.value if isinstance(action, ResourceAction) else str(action)
        envelope = TransportEnvelope(
            id=new_envelope_id(),
            kind=EnvelopeKind.ACTION,
            payload=action_id,
            meta=dict(params),
        )
        response = await self._channel.ask(envelope, timeout=self._timeout)
        return _parse_action_response(response.payload, expected_kind="action")

    async def invoke_control(
        self,
        control: AgentControl | str,
        **params: Any,
    ) -> Any:
        control_id = control.value if isinstance(control, AgentControl) else str(control)
        envelope = TransportEnvelope(
            id=new_envelope_id(),
            kind=EnvelopeKind.CONTROL,
            payload=control_id,
            meta=dict(params),
        )
        response = await self._channel.ask(envelope, timeout=self._timeout)
        return _parse_action_response(response.payload, expected_kind="control")


def _parse_action_response(payload: Any, *, expected_kind: str) -> Any:
    if not isinstance(payload, dict):
        raise ActionClientError(
            code="INVALID_RESPONSE",
            reason="transport response is not a JSON object",
            target=expected_kind,
        )
    payload_type = payload.get("type")
    if payload_type == "error":
        raise ActionClientError(
            code=str(payload.get("code", "UNKNOWN_ERROR")),
            reason=str(payload.get("reason", payload.get("error", "unknown transport error"))),
            target=str(payload.get("target", expected_kind)),
        )
    if payload_type != "result":
        raise ActionClientError(
            code="INVALID_RESPONSE_TYPE",
            reason=f"unexpected payload type: {payload_type!r}",
            target=str(payload.get("target", expected_kind)),
        )
    if payload.get("kind") != expected_kind:
        raise ActionClientError(
            code="KIND_MISMATCH",
            reason=f"expected response kind={expected_kind!r}, got {payload.get('kind')!r}",
            target=str(payload.get("target", expected_kind)),
        )
    resp = payload.get("resp")
    if not isinstance(resp, dict):
        return resp
    # Dispatcher wraps handler output under {"result": ...}.
    if "result" in resp:
        return resp["result"]
    return resp
