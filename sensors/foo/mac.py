"""Sample macOS Tanium sensor mirroring the Windows variant."""

from __future__ import annotations

from pathlib import Path

SSH_MARKER = "ssh_keepalive.flag"


def _default_root() -> Path:
    return Path("/")


def _users_dir(root: Path) -> Path:
    return root / "Users"


def run_sensor(base_dir: str | None = None) -> str:
    """Scan macOS user homes for SSH private keys."""
    if base_dir is None:
        root = _default_root()
    else:
        root = Path(base_dir)

    users_root = _users_dir(root)

    if not users_root.exists():
        return ""

    # === SENSOR_COPY_BLOCK START ===
    results: list[str] = []

    for user_dir in sorted(users_root.iterdir()):
        if not user_dir.is_dir():
            continue

        ssh_dir = user_dir / ".ssh"
        key_file = ssh_dir / SSH_MARKER
        status = "Exist" if key_file.exists() else "No"
        results.append(f"{user_dir.name}\t{status}")

    return "\n".join(results)
    # === SENSOR_COPY_BLOCK END ===


if __name__ == "__main__":
    print(run_sensor())
