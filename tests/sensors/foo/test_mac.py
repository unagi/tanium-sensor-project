import errno
from pathlib import Path

import pytest

from sensors.foo import mac
from tests.helpers.fake_entries import FakeUserDir
from tests.helpers.fixtures import prepare_sensor_files


def test_mac_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "mac", tmp_path)

    result = mac.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "charlie\tExist" in lines
    assert "dana\tNo" in lines


def test_mac_handles_missing_users(tmp_path: Path) -> None:
    result = mac.run_sensor(base_dir=str(tmp_path))
    assert result == ""


def test_mac_sanitizes_usernames(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base_dir = prepare_sensor_files("foo", "mac", tmp_path)
    users_dir = base_dir / "Users"
    placeholder = users_dir / "placeholder"
    placeholder.mkdir(parents=True, exist_ok=True)

    fake_entry = FakeUserDir(path=placeholder, fake_name="\t")
    original_iterdir = mac.Path.iterdir

    def patched_iterdir(self: Path):
        entries = list(original_iterdir(self))
        if self == users_dir:
            entries.append(fake_entry)
        return iter(entries)

    monkeypatch.setattr(mac.Path, "iterdir", patched_iterdir, raising=False)

    result = mac.run_sensor(base_dir=str(base_dir))
    assert "<unknown>\tNo" in result


@pytest.mark.parametrize(
    "exception",
    [PermissionError(errno.EACCES, "Denied"), OSError(errno.ENOENT, "boom")],
)
def test_mac_handles_iterdir_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exception: OSError
) -> None:
    base_dir = prepare_sensor_files("foo", "mac", tmp_path)

    users_dir = base_dir / "Users"
    original_iterdir = mac.Path.iterdir

    def patched_iterdir(self: Path):
        if self == users_dir:
            raise exception
        return original_iterdir(self)

    monkeypatch.setattr(mac.Path, "iterdir", patched_iterdir, raising=False)

    result = mac.run_sensor(base_dir=str(base_dir))
    assert result == ""
