from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_smoke_client_parser_accepts_doctor_command() -> None:
    client_main = importlib.import_module("client.main")
    parser = client_main._build_parser()
    args = parser.parse_args(["doctor"])
    assert args.command == "doctor"


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_smoke_client_doctor_command_runs(tmp_path: Path) -> None:
    client_main = importlib.import_module("client.main")
    workspace = tmp_path / "workspace"
    user_dir = tmp_path / "user"
    workspace.mkdir(parents=True, exist_ok=True)
    user_dir.mkdir(parents=True, exist_ok=True)

    # `doctor` should complete even when environment is partially configured.
    rc = await client_main.main(
        [
            "--workspace",
            str(workspace),
            "--user-dir",
            str(user_dir),
            "--adapter",
            "openrouter",
            "--api-key",
            "dummy",
            "doctor",
        ]
    )
    assert rc in {0, 3}
