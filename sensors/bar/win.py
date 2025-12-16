"""Windows Tanium sensor returning the OS build number via `cmd /c ver`."""

from __future__ import annotations

import re
import subprocess
import sys
from typing import Final

_COMMAND: Final[list[str]] = [
    "cmd.exe",
    "/d",
    "/s",
    "/c",
    "ver",
]
_BUILD_PATTERN = re.compile(r"Version\s+([0-9.]+)")
_TIMEOUT_SECONDS = 0.5

_ERROR_EXECUTION_FAILED = "BAR101"
_ERROR_NON_ZERO_RC = "BAR102"


# === SENSOR_COPY_BLOCK START ===
def _emit_error(code: str, message: str) -> None:
    sys.stderr.write(f"{code} {message}\n")


def _capture_command_output(command: list[str]) -> str:
    """Return stdout for the OS command, falling back to empty on failure."""
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        _emit_error(_ERROR_EXECUTION_FAILED, f"Command failed: {exc}")
        return ""

    stdout = completed.stdout
    if completed.returncode != 0:
        _emit_error(_ERROR_NON_ZERO_RC, f"Command exited with {completed.returncode}")
    return stdout


def _sanitize_build_number(raw_value: str, pattern: re.Pattern[str]) -> str:
    """Extract and normalize the build number from command stdout."""
    match = pattern.search(raw_value)
    if match:
        return match.group(1).strip()
    return raw_value.strip()


# === SENSOR_COPY_BLOCK END ===


def run_sensor(base_dir: str | None = None) -> str:
    """Return the Windows build identifier as a single-column response."""
    if base_dir is not None:
        _ = base_dir

    stdout = _capture_command_output(_COMMAND)
    build = _sanitize_build_number(stdout, _BUILD_PATTERN)
    return build


if __name__ == "__main__":
    print(run_sensor())
