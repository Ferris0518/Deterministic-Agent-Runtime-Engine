from __future__ import annotations

import importlib
import zipfile
from pathlib import Path


def test_local_backend_build_editable_contains_pth_and_entry_points(tmp_path: Path) -> None:
    backend = importlib.import_module("_local_backend")
    wheel_name = backend.build_editable(str(tmp_path))
    wheel_path = tmp_path / wheel_name
    assert wheel_path.exists()

    with zipfile.ZipFile(wheel_path, "r") as archive:
        names = set(archive.namelist())
        assert any(name.endswith(".dist-info/METADATA") for name in names)
        assert any(name.endswith(".dist-info/entry_points.txt") for name in names)
        pth_names = [name for name in names if name.endswith(".pth")]
        assert len(pth_names) == 1
        pth_content = archive.read(pth_names[0]).decode("utf-8").strip()
        assert pth_content == str(backend._project_root())


def test_local_backend_build_wheel_includes_cli_sources(tmp_path: Path) -> None:
    backend = importlib.import_module("_local_backend")
    wheel_name = backend.build_wheel(str(tmp_path))
    wheel_path = tmp_path / wheel_name
    assert wheel_path.exists()

    with zipfile.ZipFile(wheel_path, "r") as archive:
        names = set(archive.namelist())
        assert "client/main.py" in names
        assert "dare_framework/__init__.py" in names
        assert any(name.endswith(".dist-info/RECORD") for name in names)
