import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Marker registration & automatic injection from canonical ownership map
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Register ``module`` and ``owner`` markers so they pass ``--strict-markers``."""
    config.addinivalue_line("markers", "module(name): responsible dare_framework module")
    config.addinivalue_line("markers", "owner(name): responsible owner/team handle")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Inject ``@pytest.mark.module`` / ``@pytest.mark.owner`` from the ownership map."""
    from scripts.ci.test_ownership_map import OWNERSHIP_MAP

    for item in items:
        rel = str(Path(item.fspath).relative_to(ROOT))
        entry = OWNERSHIP_MAP.get(rel)
        if entry:
            item.add_marker(pytest.mark.module(entry["module"]))
            if entry.get("owner"):
                item.add_marker(pytest.mark.owner(entry["owner"]))
