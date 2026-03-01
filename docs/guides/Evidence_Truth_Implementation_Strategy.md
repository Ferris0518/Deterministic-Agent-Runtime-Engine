# Evidence Truth Implementation Strategy

> Scope: Governance changes that use `docs/features/*.md` as aggregation entry documents.

## 1. Goal

Evidence truth must be an auditable artifact, not a narrative promise.
For each active governance change, reviewers should be able to answer:
- what was executed,
- what passed/failed,
- what behavior was verified (happy path + error path),
- what risk remains and how rollback works,
- whether review/merge decisions are traceable.

## 2. Contract (Required Structure)

Each active feature aggregation doc MUST include:
- `## Evidence`
- `### Commands`
- `### Results`
- `### Behavior Verification`
- `### Risks and Rollback`
- `### Review and Merge Gate Links`

Frontmatter mode requirements:
- OpenSpec mode: `change_ids` required.
- TODO fallback mode: `mode: todo_fallback` + `topic_slug` required.

## 3. Implementation Strategy

### Phase 1 (now): Structural gate in CI

Use a deterministic script gate:
- script: `scripts/ci/check_governance_evidence_truth.sh`
- checks:
  - required evidence headings exist in active feature aggregation docs
  - frontmatter keys satisfy mode contract
  - OpenSpec artifact paths listed in aggregation docs are repository-resolvable files
  - review/merge gate section contains at least one GitHub PR review link

This phase blocks obviously incomplete governance records with low false-positive risk.

### Phase 2: Semantic consistency checks

Add semantic assertions:
- command/result pairing is present for each listed command
- behavior verification includes both happy path and changed error branch
- unresolved risk items are explicit (or marked none with reason)
- review thread fix records reference concrete commits

### Phase 3: Merge policy coupling

Connect evidence truth with merge policy:
- merge gate requires evidence section completeness for active governance change docs
- fallback-mode changes require explicit migration-debt note before closeout
- archive transition requires evidence links to remain resolvable

## 4. Operational Rules

- Evidence truth is owned by the current change implementer.
- Reviewers validate evidence links before approval.
- `docs/mailbox/` entries tagged as `audit_evidence` are retained (not deleted by default).
- Any temporary downgrade from blocking to warning must be documented in the feature doc risk section.

## 5. Command of Record

Primary gate command:

```bash
./scripts/ci/check_governance_evidence_truth.sh
```

This command is intended to run both locally and in CI.
