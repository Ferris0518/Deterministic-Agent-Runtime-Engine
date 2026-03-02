# AgentScope Execution Board Migration Implementation Plan

> 执行说明：按本计划逐项推进；不要假设本地 `superpowers` 技能已安装。若仓库内可用，优先使用 `.codex/skills/development-workflow/` 与 `.codex/skills/spec-driven-collab-board/` 的现有流程约束。

**Goal:** Migrate `docs/todos/agentscope_domain_execution_todos.md` into the standardized execution board format without changing its technical scope.

**Architecture:** Keep the existing AgentScope domain decomposition and Gate model, but reframe the document around work packages, Gate ownership, execution-board fields, and subtask acceptance tables. Preserve the current dependency model and reuse existing D1-D8 task content as the sample payload.

**Tech Stack:** Markdown, existing TODO governance docs, OpenSpec-style task references

---

### Task 1: Freeze migration scope

**Files:**
- Modify: `docs/todos/agentscope_domain_execution_todos.md`
- Reference: `docs/todos/templates/change_execution_todo_template.md`
- Reference: `docs/todos/README.md`

**Step 1: Confirm structure delta**

Read the existing execution board and map its current sections to:
- context and scope
- Gate summary
- work package board
- subtask acceptance tables
- compatibility matrix
- integration closeout

**Step 2: Keep content constraints**

Do not introduce new product scope. Reuse the current D1-D8 tasks, Gate definitions, and four-person split as the sample content.

### Task 2: Rewrite the sample board

**Files:**
- Modify: `docs/todos/agentscope_domain_execution_todos.md`

**Step 1: Add standardized header and usage rules**

Introduce:
- date
- change identifier placeholder for this migration stream
- status
- execution-board usage notes

**Step 2: Convert domain split into work packages**

Map the current four-person split into `WP-A` through `WP-D`, keeping:
- D1+D2+D3
- D6
- D7
- D4+D5+D8

**Step 3: Convert D1-D8 tasks into acceptance tables**

Keep the current task IDs and descriptions, but nest them under the owning work package with explicit evidence expectations.

### Task 3: Verify the sample stays usable

**Files:**
- Modify: `docs/todos/agentscope_domain_execution_todos.md`
- Reference: `docs/guides/Team_Agent_Collab_Playbook.md`
- Reference: `docs/todos/README.md`

**Step 1: Check terminology**

Ensure the sample now explicitly demonstrates:
- `work package`
- `Freeze Gate`
- `Status`
- `Branch/Worktree`
- `PR`
- `Evidence`

**Step 2: Check references**

Keep the file path unchanged so existing references remain valid.

**Step 3: Final review**

Confirm the document is readable as the canonical sample for future active changes.
