"""Enforce OS-specific implementation size caps from AGENTS.md."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SENSORS_ROOT = REPO_ROOT / "sensors"
MAX_TOTAL_CHARS = 45_000
MAX_PER_FILE_CHARS = 15_000
OS_FILES = ("win", "mac", "linux")


def _iter_sensor_dirs() -> list[Path]:
    return [
        path for path in SENSORS_ROOT.iterdir() if path.is_dir() and not path.name.startswith("__")
    ]


def test_sensor_source_files_remain_within_budget():  # pragma: no cover - repo policy enforcement
    for sensor_dir in _iter_sensor_dirs():
        total_chars = 0
        missing_files: list[str] = []
        per_file_counts: list[tuple[str, int]] = []

        for os_name in OS_FILES:
            source_path = sensor_dir / f"{os_name}.py"
            if not source_path.exists():
                missing_files.append(f"{os_name}.py")
                continue
            char_count = len(source_path.read_text(encoding="utf-8"))
            per_file_counts.append((os_name, char_count))
            total_chars += char_count

            assert char_count <= MAX_PER_FILE_CHARS, (
                f"{sensor_dir.name}/{os_name}.py is {char_count} characters, exceeding the"
                f" {MAX_PER_FILE_CHARS} character per-file guidance. Trim the implementation or split logic."
            )

        assert not missing_files, f"{sensor_dir.name} is missing: {', '.join(missing_files)}"
        assert total_chars <= MAX_TOTAL_CHARS, (
            f"{sensor_dir.name} total source size is {total_chars} characters across win/mac/linux,"
            f" exceeding the {MAX_TOTAL_CHARS} character budget. Counts: "
            + ", ".join(f"{name}:{count}" for name, count in per_file_counts)
        )
