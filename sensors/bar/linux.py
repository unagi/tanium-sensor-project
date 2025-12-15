"""Linux Tanium sensor returning the kernel build number via `uname -r`."""

from __future__ import annotations

import os
import re


_COMMAND = "uname -r"
_BUILD_PATTERN = re.compile(r"([0-9]+(?:\.[0-9]+){1,2}[\w\-.]*)")


# === SENSOR_COPY_BLOCK START ===
def _capture_command_output(command: str) -> str:
    """Return stdout for the OS command, falling back to empty on failure."""
    try:
        stream = os.popen(command)
    except OSError:
        return ""

    try:
        return stream.read()
    finally:
        stream.close()


def _sanitize_build_number(raw_value: str, pattern: re.Pattern[str]) -> str:
    """Extract and normalize the build number from command stdout."""
    match = pattern.search(raw_value)
    if match:
        return match.group(1).strip()
    return raw_value.strip()
# === SENSOR_COPY_BLOCK END ===


def run_sensor(base_dir: str | None = None) -> str:
    """Return the Linux kernel build identifier as a single-column response."""
    if base_dir is not None:
        # This sensor does not touch the filesystem, so the base_dir is unused.
        _ = base_dir

    stdout = _capture_command_output(_COMMAND)
    build = _sanitize_build_number(stdout, _BUILD_PATTERN)
    return build


if __name__ == "__main__":
    print(run_sensor())
