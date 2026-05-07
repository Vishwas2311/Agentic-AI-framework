from __future__ import annotations

from pathlib import Path

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported


class MendixAdapter(SourceAdapter):
    source_type = "mendix"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        # Production implementation should call Mendix Model SDK/metamodel APIs.
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.30,
            ast={"source": str(source), "adapter": "mendix", "mode": "sdk-placeholder"},
            unsupported_items=[unsupported("Mendix Model SDK integration not connected yet", "model_sdk")],
            evidence_refs=[],
        )

