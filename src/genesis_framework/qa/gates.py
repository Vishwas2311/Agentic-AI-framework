from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    details: str


def approval_summary(results: list[GateResult]) -> dict[str, object]:
    return {
        "passed": all(result.passed for result in results),
        "gates": [result.__dict__ for result in results],
    }

