from __future__ import annotations

from pathlib import Path

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported


class OutSystemsAdapter(SourceAdapter):
    source_type = "outsystems"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        # OutSystems is evidence-first because proprietary semantics may not be cleanly extractable.
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.15,
            ast={"source": str(source), "adapter": "outsystems", "mode": "runtime-evidence-placeholder"},
            unsupported_items=[unsupported("OutSystems extraction requires APIs/runtime evidence/human review", "proprietary_semantics")],
            evidence_refs=[],
        )

