from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sensors.bar import linux as bar_linux  # noqa: E402
from sensors.bar import mac as bar_mac  # noqa: E402
from sensors.bar import win as bar_win  # noqa: E402
from sensors.foo import linux as sensor_linux  # noqa: E402
from sensors.foo import mac as sensor_mac  # noqa: E402
from sensors.foo import win as sensor_win  # noqa: E402


class ForbiddenCallError(RuntimeError):
    """Raised when a forbidden API is invoked during tests."""


_SENSOR_MODULES = (bar_win, bar_mac, bar_linux, sensor_win, sensor_mac, sensor_linux)


def _forbidden(*args, **kwargs):  # type: ignore[no-untyped-def]
    raise ForbiddenCallError("Forbidden API invoked (disallowed within Tanium sensors).")


@pytest.fixture(autouse=True)
def forbid_heavy_apis(monkeypatch: pytest.MonkeyPatch) -> None:
    """Automatically patch dangerous APIs for every test."""

    for mod in _SENSOR_MODULES:
        time_module = getattr(mod, "time", None)
        if time_module is not None:
            monkeypatch.setattr(time_module, "sleep", _forbidden, raising=False)

        subprocess_module = getattr(mod, "subprocess", None)
        if subprocess_module is not None:
            monkeypatch.setattr(subprocess_module, "check_output", _forbidden, raising=False)

        threading_module = getattr(mod, "threading", None)
        if threading_module is not None:
            monkeypatch.setattr(threading_module, "Thread", _forbidden, raising=False)

    original_os_walk = os.walk

    def safe_walk(top, *args, **kwargs):  # type: ignore[no-untyped-def]
        p = Path(top)
        if str(p) in {"/", "C:\\", "C:/"}:
            raise ForbiddenCallError("os.walk('/') or os.walk('C\\') is forbidden")
        return original_os_walk(top, *args, **kwargs)

    monkeypatch.setattr(os, "walk", safe_walk, raising=False)
    monkeypatch.setattr(os, "popen", _forbidden, raising=False)
