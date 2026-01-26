Tool Internal Layout (dare_framework3_4)

This directory contains non-public implementations for the tool domain.
Imports should prefer `dare_framework3_4.tool` or `dare_framework3_4.tool._internal`
aggregates; the subpackages below organize internal responsibilities.

Subpackages
- adapters: protocol adapters (example: MCP adapter + no-op client).
- control: execution control plane (pause/resume/checkpoints).
- gateway: tool gateway implementations (capability registry + invoke).
- providers: capability providers / manager-style adapters.
- toolkits: tool aggregation helpers (example: MCP toolkit).
- tools: built-in tools shipped with the framework.
- utils: shared utilities for tool implementations.

Naming
- Use snake_case for file and function names.
- Keep new internal modules in the appropriate subpackage and re-export
  through `dare_framework3_4.tool._internal.__init__` when needed.
