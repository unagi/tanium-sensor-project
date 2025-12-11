from pathlib import Path

from sensors.foo import win
from tests.helpers.fixtures import prepare_sensor_files


def test_win_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "win", tmp_path)

    result = win.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "alice\tExist" in lines
    assert "bob\tNo" in lines
