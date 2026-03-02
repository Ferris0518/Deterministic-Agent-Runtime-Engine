# P0 Step-Driven Execution Board Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the first real execution board for `openspec/changes/p0-step-driven-execution` using the standardized collaboration template.

**Architecture:** Reframe the change around a small set of work packages that map cleanly to the OpenSpec task groups and the plan-to-execute-to-verify lifecycle. Preserve the existing proposal/design/task semantics and express them as ownership, dependency, Gate freeze, and evidence fields.

**Tech Stack:** Markdown, OpenSpec artifacts, docs/todos execution-board template

---

### Task 1: Freeze input sources

**Files:**
- Reference: `openspec/changes/p0-step-driven-execution/proposal.md`
- Reference: `openspec/changes/p0-step-driven-execution/design.md`
- Reference: `openspec/changes/p0-step-driven-execution/tasks.md`
- Reference: `docs/todos/templates/change_execution_todo_template.md`

**Step 1: Confirm source of truth**

Use the OpenSpec proposal, design, and tasks files as the only change inputs.

**Step 2: Keep scope discipline**

Do not mark implementation tasks as done. Do not change OpenSpec artifacts. Only build the execution board.

### Task 2: Build the execution board

**Files:**
- Create: `docs/todos/2026-03-02_p0-step-driven-execution_execution_todos.md`

**Step 1: Add standardized metadata**

Include:
- date
- change id
- OpenSpec path
- active status

**Step 2: Define work packages**

Map the change into a small number of work packages with:
- owner
- dependency
- touch scope
- freeze gate
- status
- branch/worktree
- PR
- evidence

**Step 3: Expand acceptance tables**

Map all OpenSpec tasks into work-package-local acceptance tables without changing task semantics.

### Task 3: Verify the board is usable

**Files:**
- Create: `docs/todos/2026-03-02_p0-step-driven-execution_execution_todos.md`

**Step 1: Check field completeness**

Ensure the final board includes Gate summary, work package board, acceptance tables, compatibility matrix, and integration closeout.

**Step 2: Check naming consistency**

Ensure the change id and file naming match the active change exactly enough for humans to follow.
