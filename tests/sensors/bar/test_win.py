import re
import sys

import pytest

from sensors.bar import win

pytestmark = [
    pytest.mark.skipif(sys.platform != "win32", reason="Windows sensor test requires Windows."),
]


def test_win_reports_build_number(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate that cmd /c ver returns a plausible Windows build string."""

    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        class _Result:
            returncode = 0
            stdout = "Version 10.0.19045"

        return _Result()

    monkeypatch.setattr(win.subprocess, "run", fake_run)

    result = win.run_sensor().strip()

    assert result, "Windows build output must not be empty."
    assert re.fullmatch(r"[0-9.]+", result)
