# Main Branch Protection and Merge Queue Setup

This checklist is the source of truth for enabling merge gates on `main`.

## Required GitHub Settings for `main`
In **Settings -> Branches -> Add rule** (branch name pattern: `main`):

1. Enable `Require a pull request before merging`.
2. Set required approvals to at least `1`.
3. Enable `Dismiss stale pull request approvals when new commits are pushed`.
4. Enable `Require review from Code Owners`.
5. Enable `Require conversation resolution before merging`.
6. Enable `Require status checks to pass before merging` and add:
   - `lint`
   - `build`
7. Enable `Require branches to be up to date before merging`.
8. Disable direct pushes (do not grant bypass except emergency admins).
9. Disable force pushes.
10. Disable branch deletion.

## Merge Queue (Preferred)
If your GitHub plan supports merge queue:

1. Enable `Require merge queue` for `main`.
2. Keep required checks as `lint` and `build` initially.
3. Start with a conservative queue strategy (small batches, low parallelism).
4. Add `merge_group` workflow trigger support (already included in `.github/workflows/ci-gate.yml`).

## Phase Rollout for Required Checks
- Phase 1 (now, required): `lint`, `build`
- Phase 2 (observe first, then required): `smoke-tests`
- Phase 3 (after 1-2 stable weeks, then required): `risk-matrix`, `test-skip-guard`, `lockfile-policy`
- Phase 4 (planned after `p0-conformance-gate` lands): `p0-gate`
  - workflow entrypoint: `.github/workflows/ci-gate.yml` job `p0-gate` runs `python scripts/ci/p0_gate.py`
  - promotion threshold: security / step-driven / audit category anchors all green in the same run
  - summary contract: `p0-gate` must emit deterministic category labels and failing test/module pointers before it can become a required branch check
  - repo-admin action: after this change merges, add `p0-gate` to the protected-branch required checks list / ruleset

## P0-Gate Required Check Rollout (Admin Checklist)

> Tracking scope: `openspec/changes/p0-conformance-gate/tasks.md` item `3.2`.

### Preconditions

1. `p0-conformance-gate` change has been merged to `main`.
2. Latest `main` run shows `p0-gate` green with all three categories reported.
3. `.github/workflows/ci-gate.yml` still contains job name `p0-gate` (required-check name must match exactly).

### Execution Steps

1. Open `Settings -> Branches` (or repository Rulesets) for `main`.
2. Enable `Require status checks to pass before merging` if not already enabled.
3. Add `p0-gate` to required status checks.
4. Keep existing required checks (`lint`, `build`, and other active phases) unchanged.
5. Save the branch protection / ruleset change.

### Acceptance

1. Open a test PR targeting `main` and force one `p0-gate` anchor failure; merge must be blocked.
2. Fix the failure and rerun; merge must be unblocked only after `p0-gate` is green.
3. Verify merge-queue path (if enabled) also enforces `p0-gate` on `merge_group`.

### Evidence to Record

1. Branch protection / ruleset screenshot or settings URL proving `p0-gate` is required.
2. One blocked PR run URL where `p0-gate` failed.
3. One unblocked PR run URL where `p0-gate` passed.
4. Update:
   - `openspec/changes/p0-conformance-gate/tasks.md` item `3.2` to `done` with links
   - `docs/features/p0-conformance-gate.md` `Results` and `Next Milestone`

## Fallback if Merge Queue Is Unavailable
Use pre-merge combined checks:

1. Keep `Require branches to be up to date before merging` enabled.
2. Keep PR checks running on GitHub's synthetic merge commit (default `pull_request` behavior).
3. Require a fresh green run after rebasing/cherry-picking onto latest `main`.

## Free-Tier Fallback if Branch Protection Is Unavailable
Use `.github/workflows/main-guard.yml` as an automated guard rail:

1. Detect pushes to `main` where commits have no associated PR metadata.
2. Open an incident issue automatically with run link and commit context.
3. In `MAIN_GUARD_MODE=revert-pr`, auto-create a rollback PR that reverts unlinked commits.
4. Fail the `main-guard` run intentionally so incidents are visible in Actions history.

### Variables (Repository -> Settings -> Secrets and variables -> Actions -> Variables)
- `MAIN_GUARD_MODE`
  - `revert-pr`: detect + issue + rollback PR (recommended default)
  - `alert-only`: detect + issue only
- `MAIN_GUARD_ALLOW_ACTORS`
  - Comma-separated pusher names allowed to bypass detection (emergency admins/bots)
- `MAIN_GUARD_ALLOW_MARKER`
  - Commit message override marker (default `[main-guard:allow-direct-push]`)

This fallback does not replace native branch protection, but it gives enforceable detection and remediation when plan limits block branch rules.

## Free-Tier Fallback: Manual Approval Enforcement
Use `.github/workflows/manual-merge-guard.yml` to enforce a review-based policy after merge:

1. Trigger on merged PR close events targeting `main`.
2. Mark non-compliant when:
   - PR is self-merged (`author == merged_by`), or
   - no independent `APPROVED` review exists.
3. Open incident issue automatically.
4. In `MANUAL_MERGE_GUARD_MODE=revert-pr`, auto-create a rollback PR.
5. Fail the guard run for visible audit signal.

### Variables
- `MANUAL_MERGE_GUARD_MODE`
  - `revert-pr`: detect + issue + rollback PR
  - `alert-only`: detect + issue only
- `MANUAL_MERGE_GUARD_ALLOW_MERGERS`
  - Emergency merger allowlist (comma-separated)

## Verification Steps
1. Open a small PR.
2. Confirm `lint` and `build` run automatically.
3. Confirm merge is blocked while checks are failing.
4. Confirm merge is allowed only after all required checks are green.
