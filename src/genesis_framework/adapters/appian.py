from __future__ import annotations

from pathlib import Path

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported


class AppianAdapter(SourceAdapter):
    source_type = "appian"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        # Production implementation should use Appian Deployment API export packages.
        return AdapterResult(
            source_type=self.source_type,
            confidence=0.25,
            ast={"source": str(source), "adapter": "appian", "mode": "deployment-api-placeholder"},
            unsupported_items=[unsupported("Appian Deployment API parser not connected yet", "deployment_package")],
            evidence_refs=[],
        )

