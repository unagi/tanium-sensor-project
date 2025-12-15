from pathlib import Path

from tests.helpers.fixtures import prepare_sensor_files

from sensors.foo import mac


def test_mac_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "mac", tmp_path)

    result = mac.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "charlie\tExist" in lines
    assert "dana\tNo" in lines


def test_mac_handles_missing_users(tmp_path: Path) -> None:
    result = mac.run_sensor(base_dir=str(tmp_path))
    assert result == ""
