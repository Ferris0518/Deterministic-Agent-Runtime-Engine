import pytest

from dare_framework.components import FileCheckpoint, FileEventLog
from dare_framework.core.events import Event
from dare_framework.core.models import MilestoneSummary, SessionSummary
from dare_framework.core.state import RuntimeState


@pytest.mark.asyncio
async def test_file_event_log_chain(tmp_path):
    path = tmp_path / "events.jsonl"
    event_log = FileEventLog(path=str(path))

    await event_log.append(Event(event_type="alpha", payload={"milestone_id": "m1"}))
    await event_log.append(Event(event_type="beta", payload={"milestone_id": "m2"}))

    events = await event_log.query()
    assert [event.event_type for event in events] == ["alpha", "beta"]
    assert await event_log.verify_chain() is True


@pytest.mark.asyncio
async def test_file_checkpoint_roundtrip(tmp_path):
    checkpoint = FileCheckpoint(path=str(tmp_path / "checkpoints"))

    checkpoint_id = await checkpoint.save(
        task_id="task_1",
        state=RuntimeState.RUNNING,
        milestone_id="m1",
    )
    assert await checkpoint.load(checkpoint_id) == RuntimeState.RUNNING

    summary = MilestoneSummary(
        milestone_id="m1",
        milestone_description="desc",
        deliverables=[],
        what_worked="",
        what_failed="",
        key_insight="",
        completeness=0.0,
        termination_reason="",
        attempts=0,
        duration_seconds=0.0,
    )
    await checkpoint.save_milestone_summary("m1", summary)
    loaded = await checkpoint.load_milestone_summary("m1")
    assert loaded.milestone_id == "m1"

    session_summary = SessionSummary(
        session_id="s1",
        user_input="u",
        what_was_accomplished="done",
        key_deliverables=[],
        important_decisions=[],
        lessons_learned=[],
        pending_tasks=[],
        milestone_count=0,
        total_attempts=0,
        duration_seconds=0.0,
    )
    await checkpoint.save_session_summary(session_summary)
    loaded_session = await checkpoint.load_session_summary("s1")
    assert loaded_session is not None
    assert loaded_session.session_id == "s1"
