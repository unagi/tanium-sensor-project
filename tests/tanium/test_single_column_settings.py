"""Validate single-column tanium_settings.yaml entries."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pytest
import yaml


class _SingleColumnCase(TypedDict):
    sensor: str
    settings_path: Path
    tanium: dict[str, object]


def _iter_single_column_cases() -> list[_SingleColumnCase]:
    repo_root = Path(__file__).resolve().parents[2]
    sensors_root = repo_root / "sensors"

    cases: list[_SingleColumnCase] = []

    for sensor_dir in sorted(sensors_root.iterdir()):
        if not sensor_dir.is_dir():
            continue

        settings_path = sensor_dir / "tanium_settings.yaml"
        if not settings_path.exists():
            continue

        tanium_cfg = yaml.safe_load(settings_path.read_text()) or {}
        tanium_section = tanium_cfg.get("tanium", {})
        if tanium_section.get("multi_column"):
            continue

        cases.append(
            _SingleColumnCase(
                sensor=sensor_dir.name,
                settings_path=settings_path,
                tanium=tanium_section,
            )
        )

    return cases


CASES = _iter_single_column_cases()
CASE_IDS = [case["sensor"] for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_single_column_settings(case: _SingleColumnCase) -> None:
    if not CASES:
        pytest.skip("No single-column sensors defined.")

    cfg = case["tanium"]

    assert cfg.get("multi_column") is False, "Single-column sensors must set multi_column to false."

    assert cfg.get("result_type") == "text", "Single-column sensors must use text result type."

    ttl = cfg.get("ttl_minutes")
    assert isinstance(ttl, int) and ttl > 0, "ttl_minutes must be a positive integer."

    string_ttl_enabled = cfg.get("string_ttl_enabled")
    assert isinstance(string_ttl_enabled, bool), "string_ttl_enabled must be boolean."
    if string_ttl_enabled:
        string_ttl_minutes = cfg.get("string_ttl_minutes")
        assert (
            isinstance(string_ttl_minutes, int) and string_ttl_minutes > 0
        ), "string_ttl_minutes must be a positive integer when enabled."

    max_string_enabled = cfg.get("max_string_enabled")
    assert isinstance(max_string_enabled, bool), "max_string_enabled must be boolean."

    ignore_case = cfg.get("ignore_case")
    assert isinstance(ignore_case, bool), "ignore_case must be boolean."

    hide_in_sensor_list = cfg.get("hide_in_sensor_list")
    assert isinstance(hide_in_sensor_list, bool), "hide_in_sensor_list must be boolean."

    hide_in_results = cfg.get("hide_in_results")
    assert isinstance(hide_in_results, bool), "hide_in_results must be boolean."

    assert "delimiter" not in cfg, "Single-column sensors must not define delimiter."
    assert "columns" not in cfg, "Single-column sensors must not define columns."
