"""No-op trust verifier implementation."""

from __future__ import annotations

from dare_framework3._internal.security.components import ITrustVerifier
from dare_framework3._internal.security.types import TrustedInput
from dare_framework3._internal.tool.types import RiskLevel


class NoOpTrustVerifier(ITrustVerifier):
    """Trust verifier that forwards input unchanged."""

    async def derive_trusted_input(
        self,
        *,
        input: dict[str, object],
        context: dict[str, object],
    ) -> TrustedInput:
        _ = context
        return TrustedInput(params=dict(input), risk_level=RiskLevel.READ_ONLY, metadata={"trusted_by": "noop"})
