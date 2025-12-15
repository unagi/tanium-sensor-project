"""Validate multi-column sensors against their tanium_settings.yaml manifest."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import TypedDict

import pytest
import yaml
from tests.helpers.fixtures import prepare_sensor_files


class _MultiColumnCase(TypedDict):
    sensor: str
    os: str
    module: str
    delimiter: str
    columns: list[dict[str, object]]


def _iter_multi_column_cases() -> list[_MultiColumnCase]:
    repo_root = Path(__file__).resolve().parents[2]
    sensors_root = repo_root / "sensors"
    fixtures_root = repo_root / "tests" / "sensors"

    cases: list[_MultiColumnCase] = []

    for sensor_dir in sorted(sensors_root.iterdir()):
        if not sensor_dir.is_dir():
            continue

        settings_path = sensor_dir / "tanium_settings.yaml"
        if not settings_path.exists():
            continue

        tanium_cfg = yaml.safe_load(settings_path.read_text()) or {}
        tanium_section = tanium_cfg.get("tanium", {})
        if not tanium_section.get("multi_column"):
            continue

        delimiter = tanium_section.get("delimiter")
        columns = tanium_section.get("columns", [])
        if not delimiter or not isinstance(columns, list) or not columns:
            raise AssertionError(
                f"{settings_path} must define a delimiter and non-empty columns list."
            )

        sensor_name = sensor_dir.name
        sensor_fixtures_root = fixtures_root / sensor_name / "fixtures"
        if not sensor_fixtures_root.exists():
            continue

        for os_dir in sorted(sensor_fixtures_root.iterdir()):
            files_dir = os_dir / "files"
            if not os_dir.is_dir() or not files_dir.exists():
                continue
            if not _os_matches_host(os_dir.name):
                continue

            cases.append(
                _MultiColumnCase(
                    sensor=sensor_name,
                    os=os_dir.name,
                    module=f"sensors.{sensor_name}.{os_dir.name}",
                    delimiter=delimiter,
                    columns=columns,
                )
            )

    return cases


def _os_matches_host(os_name: str) -> bool:
    platform = sys.platform
    if os_name == "linux":
        return platform.startswith("linux")
    if os_name == "mac":
        return platform == "darwin"
    if os_name == "win":
        return platform in {"win32", "cygwin"}
    return False


MULTI_COLUMN_CASES = _iter_multi_column_cases()
CASE_IDS = [f"{case['sensor']}-{case['os']}" for case in MULTI_COLUMN_CASES]


def _validate_value(column_type: str, value: str) -> None:
    if column_type in {"text", "string"}:
        return
    if column_type in {"number", "numeric", "float"}:
        float(value)
        return
    if column_type in {"integer", "int"}:
        int(value)
        return
    raise AssertionError(f"Unsupported column type '{column_type}' in tanium_settings.yaml")


@pytest.mark.parametrize("case", MULTI_COLUMN_CASES, ids=CASE_IDS)
def test_sensor_output_matches_tanium_settings(case: _MultiColumnCase, tmp_path: Path) -> None:
    """Ensure multi-column sensor output follows tanium_settings.yaml schema."""
    if not MULTI_COLUMN_CASES:
        pytest.skip("No multi-column sensors defined.")

    sensor_name = case["sensor"]
    os_name = case["os"]
    module_name = case["module"]
    delimiter = case["delimiter"]
    columns = case["columns"]

    module = importlib.import_module(module_name)
    base_dir = prepare_sensor_files(sensor_name, os_name, tmp_path)
    result = module.run_sensor(base_dir=str(base_dir))

    lines = [line for line in result.splitlines() if line.strip()]
    expected_columns = columns
    assert isinstance(expected_columns, list) and expected_columns

    for line in lines:
        parts = line.split(delimiter)
        assert len(parts) == len(expected_columns), (
            f"{module_name} produced '{line}' which does not match "
            f"{len(expected_columns)} columns defined in tanium_settings.yaml"
        )

        for part, column_meta in zip(parts, expected_columns, strict=True):
            if not isinstance(column_meta, dict):
                raise AssertionError("Each column entry must be a mapping with name/type keys.")
            column_type = column_meta.get("type", "text")
            _validate_value(str(column_type), part)
