# Example: Simple Coding Agent

这是一个使用 DARE Framework 构建的简单 Coding Agent 示例。

## 目的

1. **验证框架设计** - 确保接口设计合理、可用
2. **提供参考实现** - 开发者可以参考这个示例
3. **早期暴露问题** - 在框架开发过程中发现设计缺陷

## Agent 能力

这个 Coding Agent 可以：
- 读取和写入代码文件
- 搜索代码
- 运行测试
- 修复简单的 Bug

## 目录结构

```
coding-agent/
├── README.md           # 本文件
├── agent.py            # Agent 定义（入口）
├── config.yaml         # Agent 配置
├── tools/              # 自定义工具
│   ├── __init__.py
│   ├── read_file.py
│   ├── write_file.py
│   ├── search_code.py
│   └── run_tests.py
├── skills/             # 自定义技能
│   ├── __init__.py
│   └── fix_bug.py
└── tests/              # 测试
    ├── __init__.py
    ├── test_tools.py
    └── test_agent.py
```

## 使用方法

```python
from examples.coding_agent import CodingAgent

# 创建 Agent
agent = CodingAgent.from_config("config.yaml")

# 运行任务
result = await agent.run(
    task="修复 src/utils.py 中的类型错误"
)

print(result.success)
print(result.output)
```

## 这个示例验证了什么

### 1. ITool 接口的可用性

```python
# tools/read_file.py 验证：
# - ITool 接口是否足够表达工具能力
# - input_schema/output_schema 是否清晰
# - risk_level 分类是否合理
```

### 2. ISkill 接口的可用性

```python
# skills/fix_bug.py 验证：
# - ISkill 是否能表达复合能力
# - 技能内部如何调用工具
# - done_predicate 如何定义
```

### 3. IMemory 接口的必要性

```python
# agent.py 验证：
# - 如果没有记忆，Agent 能完成任务吗？
# - 记忆对任务完成有多重要？
# - 哪种记忆类型最常用？
```

### 4. 框架 vs Agent 的边界

```python
# 验证：
# - 框架提供了足够的能力吗？
# - Agent 开发者需要做的工作合理吗？
# - 接口是否足够灵活？
```

## 设计反馈

在开发这个示例的过程中发现的问题：

| 问题 | 严重程度 | 建议 |
|-----|---------|------|
| TBD | | |

---

*这个示例与框架同步开发，用于验证设计决策。*
