from __future__ import annotations

from pathlib import Path
import os
import sys
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sensors.foo import linux as sensor_linux
from sensors.foo import mac as sensor_mac
from sensors.foo import win as sensor_win


class ForbiddenCallError(RuntimeError):
    """Raised when a forbidden API is invoked during tests."""


_SENSOR_MODULES = (sensor_win, sensor_mac, sensor_linux)


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
            for attr in ("run", "Popen", "check_output"):
                monkeypatch.setattr(subprocess_module, attr, _forbidden, raising=False)

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
