import re
import sys

import pytest

from sensors.bar import mac

pytestmark = [
    pytest.mark.skipif(sys.platform != "darwin", reason="macOS sensor test requires macOS."),
]


def test_mac_reports_build_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate that sw_vers -buildVersion returns a plausibly formatted build."""

    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        class _Result:
            returncode = 0
            stdout = "23B81"

        return _Result()

    monkeypatch.setattr(mac.subprocess, "run", fake_run)

    result = mac.run_sensor().strip()

    assert result, "macOS build output must not be empty."
    assert re.fullmatch(r"[0-9A-Z]+", result)
