from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time

from dare_framework.components.layer2 import ICheckpoint
from dare_framework.core.models import MilestoneSummary, SessionSummary
from dare_framework.core.state import RuntimeState


@dataclass
class InMemoryCheckpoint(ICheckpoint):
    def __init__(self) -> None:
        self._states: dict[str, RuntimeState] = {}
        self._milestone_summaries: dict[str, MilestoneSummary] = {}
        self._session_summaries: dict[str, SessionSummary] = {}
        self._checkpoints: dict[str, RuntimeState] = {}

    async def save(
        self,
        task_id: str,
        state: RuntimeState,
        milestone_id: str | None = None,
    ) -> str:
        checkpoint_id = f"checkpoint_{task_id}_{len(self._checkpoints) + 1}"
        self._states[task_id] = state
        self._checkpoints[checkpoint_id] = state
        return checkpoint_id

    async def load(self, checkpoint_id: str) -> RuntimeState:
        return self._checkpoints.get(checkpoint_id, RuntimeState.READY)

    async def save_milestone_summary(self, milestone_id: str, summary: MilestoneSummary) -> None:
        self._milestone_summaries[milestone_id] = summary

    async def load_milestone_summary(self, milestone_id: str) -> MilestoneSummary:
        summary = self._milestone_summaries.get(milestone_id)
        if summary is None:
            raise KeyError(f"Milestone summary not found: {milestone_id}")
        return summary

    async def is_completed(self, milestone_id: str) -> bool:
        return milestone_id in self._milestone_summaries

    async def save_session_summary(self, summary: SessionSummary) -> None:
        self._session_summaries[summary.session_id] = summary

    async def load_session_summary(self, session_id: str) -> SessionSummary | None:
        return self._session_summaries.get(session_id)


class FileCheckpoint(ICheckpoint):
    def __init__(self, path: str = ".dare/checkpoints") -> None:
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)
        self._checkpoint_dir = self._path / "checkpoints"
        self._milestone_dir = self._path / "milestones"
        self._session_dir = self._path / "sessions"
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._milestone_dir.mkdir(parents=True, exist_ok=True)
        self._session_dir.mkdir(parents=True, exist_ok=True)

    async def save(
        self,
        task_id: str,
        state: RuntimeState,
        milestone_id: str | None = None,
    ) -> str:
        checkpoint_id = f"checkpoint_{int(time.time() * 1000)}"
        payload = {
            "task_id": task_id,
            "state": state.value,
            "milestone_id": milestone_id,
            "saved_at": time.time(),
        }
        file_path = self._checkpoint_dir / f"{checkpoint_id}.json"
        file_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        return checkpoint_id

    async def load(self, checkpoint_id: str) -> RuntimeState:
        file_path = self._checkpoint_dir / f"{checkpoint_id}.json"
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return RuntimeState(payload.get("state", RuntimeState.READY.value))

    async def save_milestone_summary(self, milestone_id: str, summary: MilestoneSummary) -> None:
        file_path = self._milestone_dir / f"{milestone_id}.json"
        file_path.write_text(json.dumps(asdict(summary), sort_keys=True), encoding="utf-8")

    async def load_milestone_summary(self, milestone_id: str) -> MilestoneSummary:
        file_path = self._milestone_dir / f"{milestone_id}.json"
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return MilestoneSummary(**payload)

    async def is_completed(self, milestone_id: str) -> bool:
        return (self._milestone_dir / f"{milestone_id}.json").exists()

    async def save_session_summary(self, summary: SessionSummary) -> None:
        file_path = self._session_dir / f"{summary.session_id}.json"
        file_path.write_text(json.dumps(asdict(summary), sort_keys=True), encoding="utf-8")

    async def load_session_summary(self, session_id: str) -> SessionSummary | None:
        file_path = self._session_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return SessionSummary(**payload)
