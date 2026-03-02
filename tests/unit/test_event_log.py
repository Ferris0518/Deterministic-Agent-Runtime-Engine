from __future__ import annotations

import pytest

from dare_framework.event import SQLiteEventLog


@pytest.mark.asyncio
async def test_event_log_hash_chain(tmp_path):
    path = tmp_path / "events.db"
    event_log = SQLiteEventLog(path)

    await event_log.append("test.start", {"value": 1})
    await event_log.append("test.finish", {"value": 2})

    assert await event_log.verify_chain() is True

    events = await event_log.query(filter={"event_type": "test.start"})
    assert len(events) == 1
    assert events[0].payload["value"] == 1
