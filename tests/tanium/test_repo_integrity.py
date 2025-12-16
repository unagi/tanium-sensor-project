"""Repository-wide integrity tests enforcing AGENTS.md policy."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SENSORS_ROOT = REPO_ROOT / "sensors"

COPY_BLOCK_START = "# === SENSOR_COPY_BLOCK START ==="
COPY_BLOCK_END = "# === SENSOR_COPY_BLOCK END ==="
ERROR_CODE_PATTERN = re.compile(r'_ERROR_[A-Z0-9_]+\s*=\s*"([A-Z]+[0-9]+)"')


def _iter_sensor_dirs() -> list[Path]:
    return [
        path for path in SENSORS_ROOT.iterdir() if path.is_dir() and not path.name.startswith("__")
    ]


def _extract_copy_blocks(source: str) -> list[str]:
    blocks: list[str] = []
    buffer: list[str] = []
    collecting = False

    for line in source.splitlines():
        if COPY_BLOCK_START in line:
            collecting = True
            buffer = []
            continue
        if COPY_BLOCK_END in line and collecting:
            blocks.append("\n".join(buffer).strip())
            collecting = False
            buffer = []
            continue
        if collecting:
            buffer.append(line.rstrip())

    return blocks


def _extract_error_codes_from_file(path: Path) -> set[str]:
    text = path.read_text()
    return set(ERROR_CODE_PATTERN.findall(text))


def _extract_error_codes_from_readme(path: Path) -> set[str]:
    if not path.exists():
        return set()

    text = path.read_text()
    section_start = text.find("## Error codes")
    if section_start == -1:
        return set()

    section_tail = text[section_start:].split("\n## ", 1)[0]
    codes: set[str] = set()
    for line in section_tail.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0].lower() == "code" or set(cells[0]) == {"-"}:
            continue
        codes.add(cells[0])
    return codes


def test_copy_blocks_are_in_sync():  # pragma: no cover - repo policy enforcement
    """Copy/paste governance requires identical SENSOR_COPY_BLOCK sections across OS files."""
    for sensor_dir in _iter_sensor_dirs():
        blocks_per_os: dict[str, list[str]] = {}
        for os_name in ("linux", "mac", "win"):
            os_path = sensor_dir / f"{os_name}.py"
            if not os_path.exists():
                continue
            blocks = _extract_copy_blocks(os_path.read_text())
            assert blocks, f"{os_path} is missing SENSOR_COPY_BLOCK content."
            blocks_per_os[os_name] = blocks

        if len(blocks_per_os) <= 1:
            continue

        baseline_os, baseline_blocks = next(iter(blocks_per_os.items()))
        for os_name, blocks in blocks_per_os.items():
            assert len(blocks) == len(
                baseline_blocks
            ), f"{sensor_dir.name}: {os_name} has {len(blocks)} copy blocks but {baseline_os} has {len(baseline_blocks)}."
            for index, (expected, actual) in enumerate(zip(baseline_blocks, blocks, strict=True)):
                assert (
                    actual == expected
                ), f"{sensor_dir.name} copy block {index} mismatch between {baseline_os} and {os_name}."


def test_error_codes_documented():  # pragma: no cover - repo policy enforcement
    """Ensure README tables match the _ERROR_* constants in source files."""
    for sensor_dir in _iter_sensor_dirs():
        source_codes: set[str] = set()
        for os_name in ("linux", "mac", "win"):
            os_path = sensor_dir / f"{os_name}.py"
            if os_path.exists():
                source_codes |= _extract_error_codes_from_file(os_path)

        readme_codes = _extract_error_codes_from_readme(sensor_dir / "README.md")

        if not source_codes and not readme_codes:
            continue

        assert readme_codes == source_codes, (
            f"{sensor_dir.name}: README documents {sorted(readme_codes)} but source defines {sorted(source_codes)}. "
            "Keep error code tables and _ERROR_* constants in sync."
        )
