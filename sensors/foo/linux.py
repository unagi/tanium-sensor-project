"""Sample Linux Tanium sensor reporting SSH key presence."""

from __future__ import annotations

from pathlib import Path


def _default_root() -> Path:
    return Path("/")


def _home_dir(root: Path) -> Path:
    return root / "home"


def run_sensor(base_dir: str | None = None) -> str:
    """Scan Linux home directories for private SSH keys."""
    if base_dir is None:
        root = _default_root()
    else:
        root = Path(base_dir)

    home_root = _home_dir(root)

    if not home_root.exists():
        return ""

    # === SENSOR_COPY_BLOCK START ===
    results: list[str] = []

    for user_dir in sorted(home_root.iterdir()):
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
