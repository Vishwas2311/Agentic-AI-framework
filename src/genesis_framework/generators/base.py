from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Generator(ABC):
    @abstractmethod
    def generate(self, canonical_spec: dict[str, Any], output_dir: Path) -> list[Path]:
        """Generate files from the canonical app spec."""

