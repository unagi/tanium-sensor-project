import errno
from pathlib import Path

import pytest

from sensors.foo import win
from tests.helpers.fake_entries import FakeUserDir
from tests.helpers.fixtures import prepare_sensor_files


def test_win_reports_ssh_keys(tmp_path: Path) -> None:
    base_dir = prepare_sensor_files("foo", "win", tmp_path)

    result = win.run_sensor(base_dir=str(base_dir))
    lines = result.splitlines()

    assert "alice\tExist" in lines
    assert "bob\tNo" in lines


def test_win_handles_missing_users(tmp_path: Path) -> None:
    result = win.run_sensor(base_dir=str(tmp_path))
    assert result == ""


def test_win_sanitizes_usernames(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    base_dir = prepare_sensor_files("foo", "win", tmp_path)
    users_dir = base_dir / "Users"
    placeholder = users_dir / "placeholder"
    placeholder.mkdir(parents=True, exist_ok=True)

    fake_entry = FakeUserDir(path=placeholder, fake_name="\t")
    original_iterdir = win.Path.iterdir

    def patched_iterdir(self: Path):
        entries = list(original_iterdir(self))
        if self == users_dir:
            entries.append(fake_entry)
        return iter(entries)

    monkeypatch.setattr(win.Path, "iterdir", patched_iterdir, raising=False)

    result = win.run_sensor(base_dir=str(base_dir))
    assert "<unknown>\tNo" in result


@pytest.mark.parametrize(
    "exception",
    [PermissionError(errno.EACCES, "Denied"), OSError(errno.ENOENT, "boom")],
)
def test_win_handles_iterdir_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exception: OSError
) -> None:
    base_dir = prepare_sensor_files("foo", "win", tmp_path)
    users_dir = base_dir / "Users"

    original_iterdir = win.Path.iterdir

    def patched_iterdir(self: Path):
        if self == users_dir:
            raise exception
        return original_iterdir(self)

    monkeypatch.setattr(win.Path, "iterdir", patched_iterdir, raising=False)

    result = win.run_sensor(base_dir=str(base_dir))
    assert result == ""
