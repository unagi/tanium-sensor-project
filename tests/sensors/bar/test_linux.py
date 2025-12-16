import re
import sys

import pytest

from sensors.bar import linux

pytestmark = [
    pytest.mark.skipif(sys.platform != "linux", reason="Linux sensor test requires Linux."),
]


def test_linux_reports_kernel_build(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate that we capture a plausible kernel build number."""

    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        class _Result:
            returncode = 0
            stdout = "6.8.0-1008-azure"

        return _Result()

    monkeypatch.setattr(linux.subprocess, "run", fake_run)

    result = linux.run_sensor().strip()

    assert result, "Kernel build output must not be empty."
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+[-\w.]*", result)
