from __future__ import annotations

import importlib


def test_checkpoint_defaults_module_exports_are_importable() -> None:
    defaults = importlib.import_module("dare_framework.checkpoint.defaults")

    for symbol in (
        "MemoryCheckpointStore",
        "DefaultCheckpointSaveRestore",
        "StmContributor",
        "WorkspaceGitContributor",
        "SessionStateContributor",
        "SessionContextContributor",
    ):
        assert hasattr(defaults, symbol), f"missing checkpoint default symbol: {symbol}"
