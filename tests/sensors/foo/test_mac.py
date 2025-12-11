from pathlib import Path

from sensors.foo import mac
from tests.helpers.fixtures import prepare_sensor_files


def test_mac_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "mac", tmp_path)

    result = mac.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "charlie\tExist" in lines
    assert "dana\tNo" in lines
