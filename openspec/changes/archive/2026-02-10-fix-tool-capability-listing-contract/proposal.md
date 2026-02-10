# Change: Fix tool capability listing contract

## Why
A P0 regression occurred because the tool capability listing contract drifted between sync and async call sites. Some runtime paths awaited `list_capabilities()` while the implementation returned a plain list, and context assembly temporarily returned tool-definition dicts instead of `CapabilityDescriptor` objects, causing model adapter crashes.

## What Changes
- Align the gateway contract so `IToolGateway.list_capabilities()` is awaitable and returns `list[CapabilityDescriptor]`.
- Keep synchronous runtime assembly paths supported via a manager-side synchronous capability snapshot helper.
- Require context tool assembly to provide trusted `CapabilityDescriptor` entries to `ModelInput.tools`.
- Add regression coverage to prevent descriptor-to-dict type drift in context assembly.

## Impact
- Affected specs: `interface-layer`
- Affected code:
  - `dare_framework/tool/kernel.py`
  - `dare_framework/tool/tool_manager.py`
  - `dare_framework/context/context.py`
  - `tests/unit/test_context_implementation.py`
