import os
import re
import sys

import pytest

from sensors.bar import linux

pytestmark = [
    pytest.mark.skipif(not os.environ.get("CI"), reason="bar sensor tests run only in CI."),
    pytest.mark.skipif(sys.platform != "linux", reason="Linux sensor test requires Linux."),
]


def test_linux_reports_kernel_build() -> None:
    """Validate that we capture a plausible kernel build number."""
    result = linux.run_sensor().strip()

    assert result, "Kernel build output must not be empty."
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+[-\w.]*", result)
