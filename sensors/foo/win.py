"""Sample Windows Tanium sensor that reports SSH key presence per user."""
from __future__ import annotations

from pathlib import Path


def _default_root() -> Path:
    # Default to the typical Windows system drive root.
    return Path(r"C:\\")


def _users_dir(root: Path) -> Path:
    return root / "Users"


def run_sensor(base_dir: str | None = None) -> str:
    """Scan each user profile for a private SSH key."""
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
        key_file = ssh_dir / "id_ed25519"
        status = "Exist" if key_file.exists() else "No"
        results.append(f"{user_dir.name}\t{status}")

    return "\n".join(results)
    # === SENSOR_COPY_BLOCK END ===


if __name__ == "__main__":
    print(run_sensor())
