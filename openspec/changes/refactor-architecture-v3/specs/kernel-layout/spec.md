## MODIFIED Requirements
### Requirement: Kernel defaults are domain-owned
The system SHALL locate Kernel default implementations within the `_internal` domain package that owns the corresponding Kernel contract and SHALL NOT centralize defaults under a catch-all directory.

#### Scenario: Default implementations live with their contracts
- **WHEN** a developer looks for the default event log implementation
- **THEN** it MUST be located under `dare_framework3/_internal/execution/impl/` (not under a global defaults directory).

### Requirement: Layer 0 must not depend on Layer 2
Kernel code under `dare_framework3/_internal/**/kernel.py` SHALL NOT import from `dare_framework3/_internal/**/components.py` or other Layer 2 implementations. Shared capability contracts required by Kernel defaults SHALL live under the stable interface/type facade packages.

#### Scenario: Context manager depends only on contracts
- **WHEN** `DefaultContextManager` depends on `IMemory`
- **THEN** it MUST reference `IMemory` from `dare_framework3.interfaces` and MUST NOT import internal component implementations.

## ADDED Requirements
### Requirement: Kernel and component interfaces are separated per domain
Each internal domain package SHALL define kernel interfaces in `kernel.py` and pluggable component interfaces in `components.py` to make Layer 0 vs Layer 2 boundaries explicit.

#### Scenario: Context domain interface split
- **WHEN** a contributor inspects `dare_framework3/_internal/context/`
- **THEN** kernel interfaces are defined in `kernel.py` and component interfaces are defined in `components.py`.
