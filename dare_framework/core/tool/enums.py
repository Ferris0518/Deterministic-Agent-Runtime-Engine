from __future__ import annotations

from enum import Enum


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVE_REQUIRED = "approve_required"


class StepType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class ToolType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"
