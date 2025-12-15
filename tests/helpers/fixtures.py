"""Utilities for preparing fixture directories for Tanium sensors."""

from __future__ import annotations

import shutil
from pathlib import Path


def prepare_sensor_files(sensor_name: str, os_name: str, tmp_root: Path) -> Path:
    """Copy fixture trees to a temp directory and return the new root for tests."""
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "tests" / "sensors" / sensor_name / "fixtures" / os_name / "files"

    if not src.exists():
        raise FileNotFoundError(f"Fixture not found: {src}")

    dst = tmp_root / f"{sensor_name}_{os_name}_files"
    shutil.copytree(src, dst)
    return dst
