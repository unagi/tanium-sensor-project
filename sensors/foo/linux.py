"""Sample Linux Tanium sensor reporting SSH key presence."""

from __future__ import annotations

import sys
from pathlib import Path

_ERROR_MISSING_HOME = "FOO001"
_ERROR_UNREADABLE_HOME = "FOO002"
_ERROR_KEY_SCAN_FAILED = "FOO003"


def _default_root() -> Path:
    return Path("/")


def _home_dir(root: Path) -> Path:
    return root / "home"


def _emit_error(code: str, message: str) -> None:
    sys.stderr.write(f"{code} {message}\n")


def _sanitize_user(value: str) -> str:
    sanitized_chars: list[str] = []
    saw_visible = False

    for char in value:
        code_point = ord(char)
        if char in {"\t", "\n", "\r"} or not (32 <= code_point <= 126):
            sanitized_chars.append("?")
            continue

        sanitized_chars.append(char)
        if not char.isspace():
            saw_visible = True

    sanitized = "".join(sanitized_chars).strip()
    if not sanitized or not saw_visible:
        return "<unknown>"
    return sanitized


def run_sensor(base_dir: str | None = None) -> str:
    """Scan Linux home directories for private SSH keys."""
    if base_dir is None:
        root = _default_root()
    else:
        root = Path(base_dir)

    home_root = _home_dir(root)

    if not home_root.exists():
        _emit_error(_ERROR_MISSING_HOME, f"Missing directory: {home_root}")
        return ""

    try:
        user_dirs = sorted(
            (entry for entry in home_root.iterdir() if entry.is_dir()),
            key=lambda entry: entry.name,
        )
    except OSError as exc:
        _emit_error(_ERROR_UNREADABLE_HOME, f"Unable to enumerate {home_root}: {exc}")
        return ""

    # === SENSOR_COPY_BLOCK START ===
    results: list[str] = []

    for user_dir in user_dirs:
        ssh_dir = user_dir / ".ssh"
        key_file = ssh_dir / "id_ed25519"
        try:
            key_exists = key_file.is_file()
        except OSError as exc:
            _emit_error(
                _ERROR_KEY_SCAN_FAILED, f"Cannot determine key status for {user_dir}: {exc}"
            )
            key_exists = False

        status = "Exist" if key_exists else "No"
        user_name = _sanitize_user(user_dir.name)
        results.append(f"{user_name}\t{status}")

    if results:
        return "\n".join(results)

    return "[no results]\t"
    # === SENSOR_COPY_BLOCK END ===


if __name__ == "__main__":
    print(run_sensor())
