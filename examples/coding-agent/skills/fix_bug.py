"""
Fix Bug Skill

验证点：
1. Skill 与 Tool 的边界是否清晰？
2. Skill 内部的决策逻辑如何表达？
3. DonePredicate 如何定义？
4. Skill 如何调用多个 Tool？
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class SkillTask:
    """技能任务"""
    description: str
    context: dict


@dataclass
class SkillResult:
    """技能结果"""
    success: bool
    output: Any
    steps_executed: list[str]
    evidence: list[str]


class FixBugSkill:
    """
    修复 Bug 技能

    这是一个复合技能，展示如何：
    1. 分析问题
    2. 定位代码
    3. 生成修复
    4. 验证修复
    """

    @property
    def name(self) -> str:
        return "fix_bug"

    @property
    def description(self) -> str:
        return """Analyze and fix a bug in the codebase.

This skill will:
1. Analyze the bug description
2. Search for relevant code
3. Identify the root cause
4. Generate a fix
5. Verify the fix passes tests
"""

    @property
    def required_tools(self) -> list[str]:
        """
        此技能依赖的工具

        验证：框架应该在加载技能时检查这些工具是否可用
        """
        return [
            "read_file",
            "write_file",
            "search_code",
            "run_tests",
        ]

    @property
    def done_predicate(self):  # -> DonePredicate
        """
        完成条件

        验证：如何表达复杂的完成条件？
        """
        # return DonePredicate(
        #     conditions=[
        #         {"type": "test_pass", "config": {"suite": "unit"}},
        #         {"type": "file_modified", "config": {"path": "*"}},
        #     ],
        #     require_all=True,
        # )
        return {
            "conditions": [
                {"type": "test_pass"},
                {"type": "file_modified"},
            ],
            "require_all": True,
        }

    async def execute(
        self,
        task: SkillTask,
        tool_runtime: Any,  # IToolRuntime
        context: Any,  # ExecutionContext
    ) -> SkillResult:
        """
        执行修复 Bug 技能

        这里展示了 Skill 的核心价值：
        1. 多步骤编排
        2. 决策逻辑
        3. 错误处理
        4. 最终验证
        """
        steps_executed = []
        evidence = []

        # === Step 1: 分析 Bug 描述 ===
        # 从任务描述中提取关键信息
        bug_info = self._analyze_bug_description(task.description)
        steps_executed.append("analyze_bug_description")

        # === Step 2: 搜索相关代码 ===
        search_result = await tool_runtime.invoke(
            "search_code",
            {
                "pattern": bug_info["search_pattern"],
                "file_pattern": bug_info.get("file_pattern", "*.py"),
            },
            context,
        )

        if not search_result.success:
            return SkillResult(
                success=False,
                output="Failed to search code",
                steps_executed=steps_executed,
                evidence=evidence,
            )

        steps_executed.append("search_code")

        # === Step 3: 读取相关文件 ===
        files_to_read = self._identify_files_to_read(search_result.output)

        file_contents = {}
        for file_path in files_to_read:
            read_result = await tool_runtime.invoke(
                "read_file",
                {"path": file_path},
                context,
            )
            if read_result.success:
                file_contents[file_path] = read_result.output["content"]

        steps_executed.append("read_files")

        # === Step 4: 生成修复 ===
        # 验证：这里需要调用 LLM 来生成修复
        # 问题：Skill 如何调用 LLM？通过 context.model？
        fix = await self._generate_fix(
            bug_info=bug_info,
            file_contents=file_contents,
            context=context,
        )

        if not fix:
            return SkillResult(
                success=False,
                output="Failed to generate fix",
                steps_executed=steps_executed,
                evidence=evidence,
            )

        steps_executed.append("generate_fix")

        # === Step 5: 应用修复 ===
        for file_path, new_content in fix.items():
            write_result = await tool_runtime.invoke(
                "write_file",
                {"path": file_path, "content": new_content},
                context,
            )

            if not write_result.success:
                return SkillResult(
                    success=False,
                    output=f"Failed to write fix to {file_path}",
                    steps_executed=steps_executed,
                    evidence=evidence,
                )

            if write_result.evidence_ref:
                evidence.append(write_result.evidence_ref)

        steps_executed.append("apply_fix")

        # === Step 6: 验证修复 ===
        test_result = await tool_runtime.invoke(
            "run_tests",
            {"path": bug_info.get("test_path")},
            context,
        )

        if test_result.evidence_ref:
            evidence.append(test_result.evidence_ref)

        steps_executed.append("verify_fix")

        return SkillResult(
            success=test_result.output.get("success", False),
            output={
                "bug_info": bug_info,
                "files_modified": list(fix.keys()),
                "test_result": test_result.output,
            },
            steps_executed=steps_executed,
            evidence=evidence,
        )

    def _analyze_bug_description(self, description: str) -> dict:
        """
        分析 Bug 描述

        验证：这种简单逻辑应该在 Skill 内还是调用 LLM？
        """
        # 简化实现：提取关键词
        return {
            "search_pattern": description.split()[0] if description else "",
            "file_pattern": "*.py",
            "test_path": None,
        }

    def _identify_files_to_read(self, search_output: dict) -> list[str]:
        """识别需要读取的文件"""
        matches = search_output.get("matches", [])
        return list(set(m["file"] for m in matches[:5]))

    async def _generate_fix(
        self,
        bug_info: dict,
        file_contents: dict[str, str],
        context: Any,
    ) -> dict[str, str]:
        """
        生成修复

        验证：Skill 如何访问 LLM？
        选项：
        1. context.model.generate(...)
        2. tool_runtime.invoke("llm_generate", ...)
        3. 专门的 IPlanner 接口
        """
        # TODO: 调用 LLM 生成修复
        # prompt = self._build_fix_prompt(bug_info, file_contents)
        # response = await context.model.generate(prompt)
        # return self._parse_fix_response(response)
        return {}
