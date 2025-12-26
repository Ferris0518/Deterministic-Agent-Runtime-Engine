from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Iterable, Optional, TypeVar
from uuid import uuid4
import time

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class RuntimeState(Enum):
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CANCELLED = "cancelled"


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVE_REQUIRED = "approve_required"


class ToolType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class StepType(Enum):
    ATOMIC = "atomic"
    WORKUNIT = "workunit"


class RiskLevel(Enum):
    READ_ONLY = "read_only"
    IDEMPOTENT_WRITE = "idempotent_write"
    NON_IDEMPOTENT_EFFECT = "non_idempotent_effect"
    COMPENSATABLE = "compensatable"


ToolRiskLevel = RiskLevel


class ComponentType(Enum):
    VALIDATOR = "validator"
    MEMORY = "memory"
    MODEL_ADAPTER = "model_adapter"
    TOOL = "tool"
    SKILL = "skill"
    MCP = "mcp"
    HOOK = "hook"
    PROMPT = "prompt"


@dataclass(frozen=True)
class LLMConfig:
    """Connectivity settings for LLM backends."""

    endpoint: str | None = None
    api_key: str | None = None
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        endpoint = data.get("endpoint")
        api_key = data.get("api_key")
        model = data.get("model")
        extra = {key: value for key, value in data.items() if key not in {"endpoint", "api_key", "model"}}
        return cls(endpoint=endpoint, api_key=api_key, model=model, extra=extra)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.endpoint is not None:
            payload["endpoint"] = self.endpoint
        if self.api_key is not None:
            payload["api_key"] = self.api_key
        if self.model is not None:
            payload["model"] = self.model
        payload.update(self.extra)
        return payload


@dataclass(frozen=True)
class ComponentConfig:
    """Per-type component configuration with a disabled list and named entries."""

    disabled: list[str] = field(default_factory=list)
    entries: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComponentConfig":
        disabled_raw = data.get("disabled", [])
        disabled = [str(item) for item in disabled_raw] if isinstance(disabled_raw, list) else []
        entries = {key: value for key, value in data.items() if key != "disabled"}
        return cls(disabled=disabled, entries=entries)

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.entries)
        if self.disabled:
            payload["disabled"] = list(self.disabled)
        return payload


@dataclass(frozen=True)
class Config:
    """Effective configuration resolved from layered JSON sources."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    mcp: dict[str, dict[str, Any]] = field(default_factory=dict)
    tools: dict[str, dict[str, Any]] = field(default_factory=dict)
    allowtools: list[str] = field(default_factory=list)
    allowmcps: list[str] = field(default_factory=list)
    components: dict[str, ComponentConfig] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        llm_data = data.get("llm")
        llm = LLMConfig.from_dict(llm_data) if isinstance(llm_data, dict) else LLMConfig()
        mcp = data.get("mcp") if isinstance(data.get("mcp"), dict) else {}
        tools = data.get("tools") if isinstance(data.get("tools"), dict) else {}
        allowtools = data.get("allowtools") if isinstance(data.get("allowtools"), list) else []
        allowmcps = data.get("allowmcps") if isinstance(data.get("allowmcps"), list) else []
        components_raw = data.get("components") if isinstance(data.get("components"), dict) else {}
        components = {
            key: ComponentConfig.from_dict(value)
            for key, value in components_raw.items()
            if isinstance(value, dict)
        }
        return cls(
            llm=llm,
            mcp=mcp,
            tools=tools,
            allowtools=allowtools,
            allowmcps=allowmcps,
            components=components,
        )

    def component_settings(self, component_type: ComponentType) -> ComponentConfig:
        return self.components.get(component_type.value, ComponentConfig())

    def is_component_enabled(self, component_type: ComponentType, name: str) -> bool:
        settings = self.component_settings(component_type)
        return name not in settings.disabled

    def component_config(self, component_type: ComponentType, name: str) -> Any | None:
        settings = self.component_settings(component_type)
        return settings.entries.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "llm": self.llm.to_dict(),
            "mcp": dict(self.mcp),
            "tools": dict(self.tools),
            "allowtools": list(self.allowtools),
            "allowmcps": list(self.allowmcps),
            "components": {key: value.to_dict() for key, value in self.components.items()},
        }


@dataclass(frozen=True)
class VerificationSpec:
    type: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Expectation:
    description: str
    priority: str = "MUST"
    verification_spec: Optional[VerificationSpec] = None


@dataclass
class Task:
    description: str
    task_id: str = field(default_factory=lambda: new_id("task"))
    expectations: list[Expectation] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    milestones: list["Milestone"] | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_milestones(self) -> list["Milestone"]:
        if self.milestones:
            return self.milestones
        return [
            Milestone(
                milestone_id=new_id("milestone"),
                description=self.description,
                user_input=self.description,
                expectations=self.expectations,
            )
        ]


@dataclass
class Milestone:
    milestone_id: str
    description: str
    user_input: str
    order: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    expectations: list[Expectation] = field(default_factory=list)


@dataclass
class RunContext(Generic[DepsT]):
    deps: DepsT | None
    run_id: str
    task_id: str | None = None
    milestone_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    user_input: str
    previous_session_summary: "SessionSummary | None"
    config: Config
    milestone_summaries: list["MilestoneSummary"] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)


@dataclass
class ToolErrorRecord:
    error_type: str
    tool_name: str
    message: str
    user_hint: str | None = None


@dataclass
class MilestoneContext:
    user_input: str
    milestone_description: str
    reflections: list[str] = field(default_factory=list)
    tool_errors: list[ToolErrorRecord] = field(default_factory=list)
    evidence_collected: list["Evidence"] = field(default_factory=list)
    attempted_plans: list[dict[str, Any]] = field(default_factory=list)

    def add_reflection(self, reflection: str) -> "MilestoneContext":
        self.reflections.append(reflection)
        return self

    def add_error(self, error: ToolErrorRecord) -> "MilestoneContext":
        self.tool_errors.append(error)
        return self

    def add_evidence(self, evidence: "Evidence") -> "MilestoneContext":
        self.evidence_collected.append(evidence)
        return self

    def add_attempt(self, attempt: dict[str, Any]) -> "MilestoneContext":
        self.attempted_plans.append(attempt)
        return self


@dataclass(frozen=True)
class PlanBudget:
    max_attempts: int = 3


@dataclass
class EnvelopeBudget:
    max_tool_calls: int = 30
    max_tokens: int = 50000
    max_wall_time_seconds: int = 180
    max_stagnant_iterations: int = 3
    current_tool_calls: int = 0
    current_attempts: int = 0
    stagnant_iterations: int = 0
    start_time: float = field(default_factory=time.time)

    def exceeded(self) -> bool:
        if self.current_tool_calls >= self.max_tool_calls:
            return True
        if time.time() - self.start_time >= self.max_wall_time_seconds:
            return True
        if self.stagnant_iterations >= self.max_stagnant_iterations:
            return True
        return False

    def record_attempt(self) -> None:
        self.current_attempts += 1

    def record_tool_call(self) -> None:
        self.current_tool_calls += 1

    def record_stagnation(self) -> None:
        self.stagnant_iterations += 1

    def record_progress(self) -> None:
        self.stagnant_iterations = 0


@dataclass
class Evidence:
    evidence_id: str
    kind: str
    payload: Any
    created_at: float = field(default_factory=time.time)


@dataclass
class EvidenceCondition:
    condition_type: str
    params: dict[str, Any]

    def check(self, evidence: Iterable[Evidence]) -> bool:
        if self.condition_type == "always":
            return True
        if self.condition_type == "evidence_kind":
            kind = self.params.get("kind")
            return any(item.kind == kind for item in evidence)
        return False


@dataclass(frozen=True)
class DonePredicate:
    required_keys: list[str] = field(default_factory=list)
    evidence_conditions: list[EvidenceCondition] = field(default_factory=list)
    require_all: bool = True
    description: str | None = None


@dataclass(frozen=True)
class Envelope:
    allowed_tools: list[str] = field(default_factory=list)
    required_evidence: list[EvidenceCondition] = field(default_factory=list)
    budget: EnvelopeBudget = field(default_factory=EnvelopeBudget)
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class ProposedStep:
    step_id: str
    tool_name: str
    tool_input: dict[str, Any]
    description: str = ""
    envelope: Envelope | None = None
    done_predicate: DonePredicate | None = None


PlanStep = ProposedStep


@dataclass(frozen=True)
class ProposedPlan:
    plan_description: str
    proposed_steps: list[ProposedStep]
    attempt: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidatedStep:
    step_id: str
    step_type: StepType
    tool_name: str
    risk_level: RiskLevel
    tool_input: dict[str, Any]
    description: str = ""
    envelope: Envelope | None = None
    done_predicate: DonePredicate | None = None


@dataclass(frozen=True)
class ValidatedPlan:
    plan_description: str
    steps: list[ValidatedStep]
    metadata: dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class VerifyResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tool_type: ToolType = ToolType.ATOMIC
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_approval: bool = False
    timeout_seconds: int = 30
    produces_assertions: list[dict[str, Any]] = field(default_factory=list)
    is_work_unit: bool = False


@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    evidence: list[Evidence] = field(default_factory=list)


@dataclass(frozen=True)
class Resource:
    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = None


@dataclass(frozen=True)
class ResourceContent:
    uri: str
    text: str | None
    mime_type: str | None


@dataclass(frozen=True)
class ExecuteResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    encountered_plan_tool: bool = False
    plan_tool_name: str | None = None


@dataclass(frozen=True)
class MilestoneSummary:
    milestone_id: str
    description: str
    success: bool
    attempt_count: int
    evidence_count: int


@dataclass(frozen=True)
class SessionSummary:
    session_id: str
    milestone_count: int
    success: bool
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class MilestoneResult:
    success: bool
    outputs: list[ToolResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verify_result: VerifyResult | None = None
    summary: MilestoneSummary | None = None


@dataclass(frozen=True)
class RunResult(Generic[OutputT]):
    success: bool
    output: OutputT | None = None
    milestone_results: list[MilestoneResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    session_summary: SessionSummary | None = None


@dataclass(frozen=True)
class Event:
    event_type: str
    payload: dict[str, Any]
    event_id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prev_hash: str | None = None
    event_hash: str | None = None


@dataclass(frozen=True)
class EventFilter:
    event_type: str | None = None
    milestone_id: str | None = None
    checkpoint_id: str | None = None
    run_id: str | None = None


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class ModelResponse:
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class GenerateOptions:
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass(frozen=True)
class MemoryItem:
    key: str
    value: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssembledContext:
    messages: list[Message]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeSnapshot:
    state: RuntimeState
    task_id: str
    milestone_id: str | None
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
