from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FakeUserDir:
    """Wrapper that exposes a fake directory name while using a real filesystem path."""

    path: Path
    fake_name: str

    def is_dir(self) -> bool:
        return self.path.is_dir()

    @property
    def name(self) -> str:
        return self.fake_name

    def __truediv__(self, child: str) -> Path:
        return self.path / child

    def joinpath(self, *children: str) -> Path:
        return self.path.joinpath(*children)

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return str(self.path)
