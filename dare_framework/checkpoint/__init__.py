"""Checkpoint domain facade."""

from dare_framework.checkpoint.interfaces import (
    ICheckpointContributor,
    ICheckpointSaveRestore,
    ICheckpointStore,
)
from dare_framework.checkpoint.types import (
    CheckpointContext,
    CheckpointScope,
    ScopePresets,
)
from dare_framework.checkpoint.factory import create_default_save_restore
from dare_framework.checkpoint.defaults import (
    DefaultCheckpointSaveRestore,
    MemoryCheckpointStore,
    SessionContextContributor,
    SessionStateContributor,
    StmContributor,
    WorkspaceGitContributor,
)


__all__ = [
    "ICheckpointContributor",
    "ICheckpointSaveRestore",
    "ICheckpointStore",
    "CheckpointContext",
    "CheckpointScope",
    "ScopePresets",
    "MemoryCheckpointStore",
    "DefaultCheckpointSaveRestore",
    "create_default_save_restore",
]
