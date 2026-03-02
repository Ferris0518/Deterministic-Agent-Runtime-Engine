---
name: spec-driven-collab-board
description: Use when starting, refreshing, re-scoping, or downgrading a spec-driven collaborative change that needs an execution board, work-package ownership, Gate freeze tracking, or historical-reference handling.
---

# Spec-Driven Collab Board

## Authoritative inputs
- `docs/todos/README.md`
- `docs/todos/templates/change_execution_todo_template.md`
- `docs/guides/Team_Agent_Collab_Playbook.md`
- `docs/todos/project_overall_todos.md`
- `docs/design/TODO_INDEX.md`
- `openspec/changes/<change-id>/tasks.md`
- `docs/features/<change-id>.md` when present

## Core rule

Treat `docs/todos/YYYY-MM-DD_<change-id>_execution_todos.md` as the only claim board for an active change.

Do not turn `docs/todos/project_overall_todos.md` into a task board.
Do not claim work directly from `docs/design/TODO_INDEX.md`.

## Workflow

1. Confirm the change state before editing any board.
- Read `openspec/changes/<change-id>/tasks.md`.
- Read `docs/features/<change-id>.md` when it exists.
- Read the matching initiative entry in `docs/todos/project_overall_todos.md` when one exists.
- If tasks are complete and the feature or roadmap status is `done`, do not create a new active board for that change.

2. Choose exactly one board action.
- `create`: no execution board exists for an active change.
- `refresh`: an execution board exists but its gates, work packages, or evidence links are stale.
- `historical-reference`: the change is completed or superseded and the old board should remain only as reference.

3. Create or refresh the board from the template.
- Use `docs/todos/templates/change_execution_todo_template.md` as the structural baseline.
- Name the file `docs/todos/YYYY-MM-DD_<change-id>_execution_todos.md`.
- Keep the status explicit: `active`, `blocked`, `archived`, or `historical reference`.
- Include these sections unless there is a strong reason not to:
  - usage rules
  - context and scope boundary
  - Gate freeze summary
  - work-package claim board
  - subtask acceptance tables
  - interface compatibility matrix
  - integration and closeout
  - maintenance rules

4. Split work at the work-package level, not at the bullet level.
- Create `2-5` work packages for one change.
- Target `0.5-2` days of work per package.
- Give each package one owner, one main goal, one declared touch scope, and one freeze boundary.
- Keep subtasks small for acceptance and evidence mapping, but do not use them as the default claim unit.

5. Apply Gate rules before allowing parallel work.
- Shared contracts must freeze before downstream packages claim dependent work.
- A package should cross at most one Gate.
- If two developers need the same schema, payload, enum, state machine, or audit contract, split into upstream freeze work and downstream implementation work.

6. Keep the board synchronized with the surrounding governance documents.
- `project_overall_todos.md` remains roadmap-only.
- `TODO_INDEX.md` remains backlog-only.
- The execution board must link back to the OpenSpec change and reflect the same completion state as `tasks.md`.
- If a package moves to `review` or `done`, update evidence on the same day.

7. Downgrade completed boards instead of pretending they are still active.
- Change the title and status to make the historical role obvious.
- State why the board is no longer active.
- Point future coordination to the currently active change when one is known.

## Board quality checks

Before claiming the board update is complete, verify:
- the chosen change is still active if the board is marked `active`
- each work package has `WP`, `Goal`, `Owner`, `Depends On`, `Touch Scope`, `Freeze Gate`, `Status`, `Branch/Worktree`, `PR`, `Evidence`, and `Last Updated`
- subtask tables map back to OpenSpec task IDs, gap IDs, or testable acceptance points
- the board does not duplicate implementation detail into `project_overall_todos.md`
- the board and `openspec/changes/<change-id>/tasks.md` do not contradict each other

## Output expectations

Report:
- which action was taken: `create`, `refresh`, or `historical-reference`
- why this change is the correct active or historical board target
- which files were created or updated
- what still needs owner assignment, evidence, or Gate freeze

## Examples

Use these boards as references when the structure is unclear:
- `docs/todos/agentscope_domain_execution_todos.md`
- `docs/todos/templates/change_execution_todo_template.md`
