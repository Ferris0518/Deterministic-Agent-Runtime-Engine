import pytest

from dare_framework import AgentBuilder
from dare_framework.core.models import Task
from dare_framework.models import NoopModelAdapter
from dare_framework.tools import NoopTool


@pytest.mark.asyncio
async def test_agent_builder_runs_task():
    agent = (
        AgentBuilder("test-agent")
        .with_tools(NoopTool())
        .with_model(NoopModelAdapter(response_text="done"))
        .build()
    )

    result = await agent.run(Task(description="hello"), deps=None)

    assert result.success is True
    assert result.session_summary is not None
