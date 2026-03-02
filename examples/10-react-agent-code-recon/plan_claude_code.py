from __future__ import annotations

import argparse
import asyncio
import os
import sys
from dataclasses import replace
from enum import Enum
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.agent import BaseAgent
from dare_framework.config import Config
from dare_framework.skill._internal.filesystem_skill_loader import FileSystemSkillLoader
from dare_framework.model import OpenRouterModelAdapter
from dare_framework.model.types import Prompt
from dare_framework.plan_v2 import (
    PLAN_AGENT_SYSTEM_PROMPT,
    SUB_AGENT_TASK_PROMPT,
    Planner,
    PlannerState,
    SubAgentRegistry,
)
from dare_framework.tool._internal.tools import (
    EditLineTool,
    ReadFileTool,
    RunCommandTool,
    SearchCodeTool,
    SearchFileTool,
    WriteFileTool,
)

EXAMPLE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = EXAMPLE_DIR / "workspace"


def _parse_args() -> argparse.Namespace:
    """解析命令行：目标工程路径。"""
    parser = argparse.ArgumentParser(
        description="对标 Claude Code：项目级 AI 编程助手。支持深度理解、修改代码、执行命令。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python plan_claude_code.py                    # 目标工程 = 当前目录
  python plan_claude_code.py .                  # 同上
  python plan_claude_code.py D:/Agent/realesrgan/Real-ESRGAN
""",
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="目标工程路径（默认当前目录）",
    )
    return parser.parse_args()


class CommandType(Enum):
    QUIT = "quit"
    HELP = "help"


def _parse_command(user_input: str) -> CommandType | tuple[None, str]:
    """解析 / 开头的命令，否则返回 (None, 原始输入)。"""
    stripped = user_input.strip()
    if not stripped.startswith("/"):
        return (None, stripped)
    cmd = stripped[1:].split(maxsplit=1)[0].lower()
    mapping = {
        "quit": CommandType.QUIT, "exit": CommandType.QUIT, "q": CommandType.QUIT,
        "help": CommandType.HELP,
    }
    if cmd not in mapping:
        return (None, stripped)  # 未知 / 命令当作普通输入
    return mapping[cmd]


def _print_help(project_path: str) -> None:
    print("\nCommands: /help  /quit", flush=True)
    print("\n任务类型:", flush=True)
    print("  - 理解项目、回答问题、修改代码、运行测试", flush=True)
    print(f"\n目标工程: {project_path}", flush=True)


def _reset_plan_state(state: PlannerState) -> None:
    """每轮新对话前重置 plan 状态，避免上一轮计划干扰。"""
    state.plan_description = ""
    state.steps.clear()
    state.completed_step_ids.clear()
    state.plan_validated = False
    state.plan_success = True
    state.plan_errors.clear()
    state.last_verify_errors.clear()
    state.last_remediation_summary = ""
    state.critical_block = ""


def _build_plan_prompt(workspace_dir: str, project_path: str) -> str:
    """构建主 Agent prompt（意图驱动），注入路径与 sub-agent 说明。"""
    return PLAN_AGENT_SYSTEM_PROMPT + f"""

【路径 - 全部用绝对路径】
- 目标工程（只读）: {project_path}
- 产出目录（可写）: {workspace_dir}

【可用 sub-agent】委托格式见上方【委托原则】。
- sub_agent_recon：侦察。理解代码、回答问题、搜索、生成报告（可写 workspace）。
- sub_agent_coder：可读写。创建/修改代码、添加功能、修复 bug、重构。
- sub_agent_runner：可执行。运行测试、构建、执行命令。

任务类型与 sub-agent 对应：
- 理解项目、回答问题、代码侦查 → sub_agent_recon
- 添加功能、修复 bug、写代码 → sub_agent_recon 先理解 → sub_agent_coder 实现
- 运行测试、构建 → sub_agent_runner"""


def _ensure_run_alias(agent: BaseAgent) -> BaseAgent:
    """SubAgentRegistry 需要 agent.run()，BaseAgent 仅有 __call__。添加 run 别名。"""
    if not hasattr(agent, "run") or not callable(getattr(agent, "run", None)):
        agent.run = agent.__call__  # type: ignore[method-assign]
    return agent


async def main() -> None:
    args = _parse_args()
    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"Error: 目标工程路径不存在: {project_path}")
        sys.exit(1)

    api_key = os.getenv("OPENROUTER_API_KEY", "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")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        sys.exit(1)

    model_name = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2.5")
    max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))

    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    model = OpenRouterModelAdapter(
        model=model_name,
        api_key=api_key,
        extra={
            "max_tokens": max_tokens,
            "temperature": 0.5,  # Agent 场景常用：工具调用稳定，表述略有变化
            "seed": 42,  # 提高 function call 一致性
        },
    )

    # 全部用绝对路径，禁止相对路径
    workspace_dir_abs = str(WORKSPACE_DIR.resolve())
    project_path_abs = str(project_path.resolve())
    roots = [workspace_dir_abs, project_path_abs]

    class _ConfigWithRoots:
        """包装 Config，添加 workspace_roots 供 file_utils 使用。"""

        def __init__(self, base: Config, workspace_roots: list[str]) -> None:
            object.__setattr__(self, "_base", base)
            object.__setattr__(self, "workspace_roots", workspace_roots)

        def __getattr__(self, name: str) -> object:
            return getattr(self._base, name)

    base_config = Config(
        workspace_dir=str(PROJECT_ROOT),
        user_dir=str(Path.home()),
    )
    base_config = _ConfigWithRoots(base_config, roots)

    def _build_sub_prompt() -> str:
        return SUB_AGENT_TASK_PROMPT

    sub_prompt = Prompt(
        prompt_id="sub-agent.system",
        role="system",
        content=_build_sub_prompt(),
        supported_models=[],
        order=0,
    )

    # sub_agent_recon：只读 + write_file，加载 code-recon skill
    _code_recon_skill_dir = EXAMPLE_DIR / "skills" / "code-recon"
    _code_recon_skills = FileSystemSkillLoader(_code_recon_skill_dir).load()
    _code_recon_skill = _code_recon_skills[0] if _code_recon_skills else None

    recon_agent = await (
        BaseAgent.react_agent_builder("sub_agent_recon")
        .with_model(model)
        .with_config(base_config)
        .with_context_strategy("smart")
        .with_prompt(sub_prompt)
        .with_sys_skill(_code_recon_skill)
        .with_skill_tool(False)  # 使用固定 code-recon skill，不启用 search_skill
        .add_tools(ReadFileTool(), SearchCodeTool(), SearchFileTool(), WriteFileTool())
        .with_max_tool_rounds(80)
        .build()
    )
    _ensure_run_alias(recon_agent)

    # sub_agent_coder：可写
    coder_agent = await (
        BaseAgent.react_agent_builder("sub_agent_coder")
        .with_model(model)
        .with_config(base_config)
        .with_context_strategy("smart")
        .with_prompt(sub_prompt)
        .add_tools(ReadFileTool(), WriteFileTool(), SearchCodeTool(), EditLineTool())
        .build()
    )
    _ensure_run_alias(coder_agent)

    # sub_agent_runner：可执行
    runner_agent = await (
        BaseAgent.react_agent_builder("sub_agent_runner")
        .with_model(model)
        .with_config(base_config)
        .with_context_strategy("smart")
        .with_prompt(sub_prompt)
        .add_tools(RunCommandTool(), ReadFileTool())
        .build()
    )
    _ensure_run_alias(runner_agent)

    registry = SubAgentRegistry()
    registry.register(
        "sub_agent_recon",
        "侦察：理解代码、回答问题、搜索、生成报告（产出到 workspace）。task 只写任务目标、交付件、目标路径。",
        lambda: recon_agent,
    )
    registry.register(
        "sub_agent_coder",
        "代码编写：read_file、write_file、search_code、edit_line。用于创建或修改代码文件。",
        lambda: coder_agent,
    )
    registry.register(
        "sub_agent_runner",
        "命令执行：run_command、read_file。用于运行测试、构建等。",
        lambda: runner_agent,
    )

    state = PlannerState(task_id="plan-claude-code-1", session_id="plan-claude-code-session-1")
    planner = Planner(state, sub_agent_registry=registry, plan_tools=False)

    plan_prompt = Prompt(
        prompt_id="plan-agent.system",
        role="system",
        content=_build_plan_prompt(workspace_dir_abs, project_path_abs),
        supported_models=[],
        order=0,
    )

    plan_config = _ConfigWithRoots(replace(base_config._base, mcp_paths=[]), roots)
    plan_agent = await (
        BaseAgent.react_agent_builder("plan-agent")
        .with_config(plan_config)
        .with_model(model)
        .with_context_strategy("smart")
        .with_prompt(plan_prompt)
        .with_plan_provider(planner)
        .add_tools(ReadFileTool())
        .with_skill_tool(False)
        .with_max_tool_rounds(30)
        .build()
    )

    print("对标 Claude Code - 项目级 AI 编程助手（意图驱动）")
    print("  Sub-agents: sub_agent_recon (只读) | sub_agent_coder (可写) | sub_agent_runner (可执行)")
    print(f"  Model: {model_name}")
    print(f"  目标工程: {project_path_abs}")
    print(f"  Workspace: {workspace_dir_abs}")
    _print_help(project_path_abs)
    print("-" * 60)

    while True:
        try:
            raw = input("\ntask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.", flush=True)
            return

        if not raw:
            continue

        parsed = _parse_command(raw)
        if isinstance(parsed, CommandType):
            if parsed is CommandType.QUIT:
                print("Bye.", flush=True)
                return
            if parsed is CommandType.HELP:
                _print_help(project_path_abs)
                continue
            continue
        task_text = parsed[1] if isinstance(parsed, tuple) else raw

        # 每轮新任务前重置 plan 状态
        _reset_plan_state(state)

        result = await plan_agent(task_text)
        output_text = result.output_text or str(result.output)
        print(f"\nAssistant: {output_text}", flush=True)
        if result.errors:
            print(f"Errors: {result.errors}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
