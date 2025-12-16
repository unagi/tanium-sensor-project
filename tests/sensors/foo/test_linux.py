import errno
from pathlib import Path

import pytest

from sensors.foo import linux
from tests.helpers.fake_entries import FakeUserDir
from tests.helpers.fixtures import prepare_sensor_files


class TestRealExecution:
    def test_linux_reports_ssh_keys(self, tmp_path: Path) -> None:
        base_dir = prepare_sensor_files("foo", "linux", tmp_path)

        result = linux.run_sensor(base_dir=str(base_dir))
        lines = result.splitlines()

        assert "erin\tExist" in lines
        assert "frank\tNo" in lines

    def test_linux_handles_missing_home(self, tmp_path: Path) -> None:
        result = linux.run_sensor(base_dir=str(tmp_path))
        assert result == ""


class TestMockedBehavior:
    def test_linux_sanitizes_usernames(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base_dir = prepare_sensor_files("foo", "linux", tmp_path)
        home_dir = base_dir / "home"
        placeholder = home_dir / "placeholder"
        placeholder.mkdir(parents=True, exist_ok=True)

        fake_entry = FakeUserDir(path=placeholder, fake_name="\t")
        original_iterdir = linux.Path.iterdir

        def patched_iterdir(self: Path):
            entries = list(original_iterdir(self))
            if self == home_dir:
                entries.append(fake_entry)
            return iter(entries)

        monkeypatch.setattr(linux.Path, "iterdir", patched_iterdir, raising=False)

        result = linux.run_sensor(base_dir=str(base_dir))
        assert "<unknown>\tNo" in result

    @pytest.mark.parametrize(
        "exception",
        [PermissionError(errno.EACCES, "Denied"), OSError(errno.ENOENT, "boom")],
    )
    def test_linux_handles_iterdir_errors(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exception: OSError
    ) -> None:
        base_dir = prepare_sensor_files("foo", "linux", tmp_path)

        target = linux._home_dir(Path(str(base_dir)))
        original_iterdir = linux.Path.iterdir

        def patched_iterdir(self: Path):
            if self == target:
                raise exception
            return original_iterdir(self)

        monkeypatch.setattr(linux.Path, "iterdir", patched_iterdir, raising=False)

        result = linux.run_sensor(base_dir=str(base_dir))
        assert result == ""
