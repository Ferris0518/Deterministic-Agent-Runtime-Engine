from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_smoke_python_module_entrypoint_help() -> None:
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "client", "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path.cwd())},
        check=False,
    )
    assert completed.returncode == 0
    assert "DARE external CLI" in completed.stdout


@pytest.mark.smoke
def test_smoke_python_module_entrypoint_doctor(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    user_dir = tmp_path / "user"
    workspace.mkdir(parents=True, exist_ok=True)
    user_dir.mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "client",
            "--workspace",
            str(workspace),
            "--user-dir",
            str(user_dir),
            "--adapter",
            "openrouter",
            "--api-key",
            "dummy",
            "--output",
            "json",
            "doctor",
        ],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(Path.cwd())},
        check=False,
    )
    # Some environments may still report warnings and return non-zero.
    assert completed.returncode in {0, 3}
    assert '"type": "result"' in completed.stdout
