import os
import re
import sys

import pytest

from sensors.bar import win

pytestmark = [
    pytest.mark.skipif(not os.environ.get("CI"), reason="Windows sensor integration test runs in CI only."),
    pytest.mark.skipif(sys.platform != "win32", reason="Windows sensor test requires Windows."),
]


def test_win_reports_build_number() -> None:
    """Validate that cmd /c ver returns a plausible Windows build string."""
    result = win.run_sensor().strip()

    assert result, "Windows build output must not be empty."
    assert re.fullmatch(r"[0-9.]+", result)
