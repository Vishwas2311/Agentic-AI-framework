from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AdapterResult:
    source_type: str
    confidence: float
    ast: dict[str, Any]
    unsupported_items: list[dict[str, Any]]
    evidence_refs: list[str]


class SourceAdapter(ABC):
    source_type: str

    @abstractmethod
    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        """Extract native source data into a Genesis AST result."""


def unsupported(reason: str, artifact: str = "unknown") -> dict[str, Any]:
    return {"artifact": artifact, "reason": reason, "status": "manual"}

