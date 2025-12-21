"""
Run Tests Tool

验证点：
1. 产出证据的工具如何定义 produces_assertions？
2. 长时间运行的工具如何处理超时？
"""

from typing import Any
import asyncio
import subprocess


class RunTestsTool:
    """
    运行测试工具

    功能：运行项目的测试套件
    风险级别：READ_ONLY（不修改代码，只运行测试）
    """

    @property
    def name(self) -> str:
        return "run_tests"

    @property
    def description(self) -> str:
        return """Run the project's test suite.

Use this tool when you need to:
- Verify code changes work correctly
- Check for regressions
- Validate bug fixes
"""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Test file or directory to run"
                },
                "pattern": {
                    "type": "string",
                    "description": "Test name pattern to match"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Enable verbose output",
                    "default": False
                }
            }
        }

    @property
    def output_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "passed": {"type": "integer"},
                "failed": {"type": "integer"},
                "skipped": {"type": "integer"},
                "output": {"type": "string"},
                "failures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test": {"type": "string"},
                            "error": {"type": "string"}
                        }
                    }
                }
            }
        }

    @property
    def risk_level(self) -> str:
        return "READ_ONLY"

    @property
    def timeout_seconds(self) -> int:
        return 300  # 5 分钟超时

    @property
    def produces_assertions(self) -> list:
        """
        这个工具产出测试证据

        验证：这正是 Coverage 确定性计算需要的
        """
        return [
            {"type": "test_pass", "produces": {"suite": "unit"}},
            {"type": "evidence_type", "produces": {"types": ["TEST_REPORT"]}}
        ]

    async def execute(self, input: dict[str, Any], context: Any) -> dict[str, Any]:
        """执行测试"""
        cmd = ["pytest", "--tb=short", "-q"]

        if input.get("path"):
            cmd.append(input["path"])
        if input.get("pattern"):
            cmd.extend(["-k", input["pattern"]])
        if input.get("verbose"):
            cmd.append("-v")

        try:
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                ),
                timeout=self.timeout_seconds
            )
            stdout, _ = await result.communicate()
            output = stdout.decode()

            # 解析 pytest 输出
            parsed = self._parse_pytest_output(output)

            return {
                "success": result.returncode == 0,
                "passed": parsed["passed"],
                "failed": parsed["failed"],
                "skipped": parsed["skipped"],
                "output": output,
                "failures": parsed["failures"],
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "output": "Test execution timed out",
                "failures": [],
            }

    def _parse_pytest_output(self, output: str) -> dict:
        """解析 pytest 输出"""
        # 简化实现
        return {
            "passed": output.count(" passed"),
            "failed": output.count(" failed"),
            "skipped": output.count(" skipped"),
            "failures": [],
        }
