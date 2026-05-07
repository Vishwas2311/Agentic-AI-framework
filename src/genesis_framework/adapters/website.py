from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from genesis_framework.adapters.base import AdapterResult, SourceAdapter, unsupported
from genesis_framework.browser_capture import inspect_website_reference


class WebsiteAdapter(SourceAdapter):
    source_type = "website"

    def extract(self, source: Path | str, output_dir: Path) -> AdapterResult:
        url = str(source).strip()
        parsed = urlparse(url)
        capture = inspect_website_reference(url, output_dir, allow_remote=False)
        domain = parsed.netloc or ""
        confidence = 0.82 if capture.get("capture_status") == "captured" else (0.72 if domain else 0.45)
        unsupported_items = [
            unsupported("Backend logic, auth rules, and private APIs still require runtime evidence or docs.", "backend_logic")
        ]
        if capture.get("capture_status") == "skipped":
            unsupported_items.append(unsupported(str(capture.get("capture_reason")), "runtime_capture"))
        return AdapterResult(
            source_type=self.source_type,
            confidence=confidence,
            ast={"adapter": "website", **capture},
            unsupported_items=unsupported_items,
            evidence_refs=[url] if domain else [],
        )
