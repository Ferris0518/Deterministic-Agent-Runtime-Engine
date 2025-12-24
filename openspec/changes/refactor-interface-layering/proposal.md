# Change: Refactor interface layering (Layer 1 vs Layer 2)

## Why
Current interface definitions are co-located, which blurs architectural boundaries. The design docs specify Layer 1 (core infrastructure) and Layer 2 (pluggable components), and separating these interfaces will improve clarity and enforce the intended architecture.

## What Changes
- Split interface definitions into Layer 1 and Layer 2 modules aligned with `Interface_Layer_Design_v1.1_MCP_and_Builtin.md`.
- Update imports across the codebase to reference the correct layer.
- Provide compatibility re-exports to avoid breaking downstream imports (if applicable).

## Impact
- Affected specs: interface-layer
- Affected code: `dare_framework/core/`, `dare_framework/components/`, public exports
