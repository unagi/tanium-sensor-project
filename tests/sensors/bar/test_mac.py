import os
import re
import sys

import pytest

from sensors.bar import mac


pytestmark = [
    pytest.mark.skipif(not os.environ.get("CI"), reason="bar sensor tests run only in CI."),
    pytest.mark.skipif(sys.platform != "darwin", reason="macOS sensor test requires macOS."),
]


def test_mac_reports_build_version() -> None:
    """Validate that sw_vers -buildVersion returns a plausibly formatted build."""
    result = mac.run_sensor().strip()

    assert result, "macOS build output must not be empty."
    assert re.fullmatch(r"[0-9A-Z]+", result)
