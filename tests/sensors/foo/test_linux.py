from pathlib import Path

from sensors.foo import linux
from tests.helpers.fixtures import prepare_sensor_files


def test_linux_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "linux", tmp_path)

    result = linux.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "erin\tExist" in lines
    assert "frank\tNo" in lines
