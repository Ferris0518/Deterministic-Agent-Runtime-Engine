## Superpowers System

<EXTREMELY_IMPORTANT>
You have superpowers. Superpowers teach you new skills and capabilities. RIGHT NOW run: using superpowers and follow the instructions it returns.
</EXTREMELY_IMPORTANT>

# Additional Constraints

- When writing code, add necessary comments to clarify non-obvious logic or intent.
- When creating a commit, include a detailed commit message (summary + body with key changes and rationale).

## Documentation-First Governance (Mandatory)

- Agent-driven development MUST follow documents under `docs/guides/` first, especially:
  - `docs/guides/Development_Constraints.md`
  - `docs/guides/Documentation_First_Development_SOP.md`
- Code implementation MUST align with `docs/design/` as the latest full design source of truth.
- If design and implementation diverge, update design docs first, then execute gap analysis before coding.
- Every design doc that governs implementation MUST explicitly contain:
  - overall architecture
  - core workflow
  - data structures
  - key interfaces
  - exception/error handling
- For any bug fix, feature, or refactor, follow the SOP sequence:
  1. perform full-scope analysis and create a master TODO backlog
  2. update design docs and governance docs (docs are canonical)
  3. slice TODO backlog into one or more OpenSpec changes
  4. execute fixes via OpenSpec workflow task-by-task per slice
  5. update TODO/evidence and archive analysis artifacts
