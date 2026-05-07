from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SourceTruthDecision:
    artifact_id: str
    artifact_type: str
    winning_source: str
    reason: str
    confidence: float
    requires_human_review: bool


def decide_source_truth(
    artifact_id: str,
    artifact_type: str,
    candidates: dict[str, Any],
    preferred_order: tuple[str, ...] = ("human", "runtime", "api", "db", "export", "design"),
) -> SourceTruthDecision:
    weighted_scores: dict[str, float] = {}
    for source, candidate in candidates.items():
        if candidate is None:
            continue
        weighted_scores[source] = _candidate_score(source, candidate)

    if weighted_scores:
        for source in preferred_order:
            if source not in weighted_scores:
                continue
            highest = max(weighted_scores.values())
            if weighted_scores[source] >= highest:
                confidence = min(0.95, round(weighted_scores[source], 4))
                return SourceTruthDecision(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    winning_source=source,
                    reason=f"Selected {source} using weighted confidence and configured order.",
                    confidence=confidence,
                    requires_human_review=confidence < 0.75,
                )

    for source in preferred_order:
        if source in candidates and candidates[source] is not None:
            confidence = 0.85 if source in {"human", "runtime", "api"} else 0.70
            return SourceTruthDecision(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                winning_source=source,
                reason=f"Selected first available source by configured order: {source}",
                confidence=confidence,
                requires_human_review=confidence < 0.75,
            )
    return SourceTruthDecision(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        winning_source="none",
        reason="No candidate source available",
        confidence=0.0,
        requires_human_review=True,
    )


def _candidate_score(source: str, candidate: Any) -> float:
    base = {
        "human": 0.95,
        "runtime": 0.88,
        "api": 0.86,
        "db": 0.82,
        "export": 0.78,
        "design": 0.72,
    }.get(source, 0.65)
    if isinstance(candidate, dict):
        if isinstance(candidate.get("confidence"), (float, int)):
            base = max(base, float(candidate["confidence"]))
        if candidate.get("unsupported_items"):
            base -= 0.08
        populated_fields = sum(1 for value in candidate.values() if value not in (None, [], {}, ""))
        base += min(0.08, populated_fields * 0.01)
    return max(0.0, min(0.95, base))
