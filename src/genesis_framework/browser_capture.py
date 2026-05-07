from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, url2pathname, urlopen


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def capture_runtime_targets(
    urls: list[str],
    output_dir: Path,
    *,
    allow_remote: bool = False,
    timeout_seconds: float = 4.0,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    captures = [
        _capture_single_target(url, output_dir, allow_remote=allow_remote, timeout_seconds=timeout_seconds)
        for url in urls
    ]
    captured = [item for item in captures if item["status"] == "captured"]
    return {
        "schema_version": "3.1.0",
        "status": "captured" if captured else ("partial" if captures else "not_applicable"),
        "captured_count": len(captured),
        "targets": captures,
    }


def inspect_website_reference(
    url: str,
    output_dir: Path,
    *,
    allow_remote: bool = False,
    timeout_seconds: float = 4.0,
) -> dict[str, Any]:
    capture = _capture_single_target(url, output_dir, allow_remote=allow_remote, timeout_seconds=timeout_seconds)
    parsed = urlparse(url)
    return {
        "source": url,
        "domain": parsed.netloc,
        "path": parsed.path,
        "scheme": parsed.scheme,
        "mode": "captured_html" if capture["status"] == "captured" else "url_reference",
        "title": capture.get("title"),
        "forms": capture.get("forms"),
        "links": capture.get("links"),
        "buttons": capture.get("buttons"),
        "inputs": capture.get("inputs"),
        "snapshot_file": capture.get("snapshot_file"),
        "capture_status": capture["status"],
        "capture_reason": capture.get("reason"),
    }


def _capture_single_target(
    url: str,
    output_dir: Path,
    *,
    allow_remote: bool,
    timeout_seconds: float,
) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        try:
            file_path = Path(url2pathname(parsed.path))
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            return {"url": url, "status": "error", "reason": str(exc)}
        return _build_capture_record(url, text, output_dir)

    if parsed.scheme not in {"http", "https"}:
        return {"url": url, "status": "skipped", "reason": f"Unsupported scheme: {parsed.scheme or 'none'}"}

    if parsed.hostname not in LOCAL_HOSTS and not allow_remote:
        return {
            "url": url,
            "status": "skipped",
            "reason": "Remote capture is disabled for non-local targets in this runtime pass.",
        }

    try:
        request = Request(url, headers={"User-Agent": "GenesisRuntimeCapture/3.1"})
        with urlopen(request, timeout=timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(300_000).decode("utf-8", errors="ignore")
    except URLError as exc:
        return {"url": url, "status": "error", "reason": str(exc)}

    if "html" not in content_type.lower() and "<html" not in body.lower():
        return {
            "url": url,
            "status": "skipped",
            "reason": f"Target returned non-HTML content: {content_type or 'unknown'}",
        }
    return _build_capture_record(url, body, output_dir)


def _build_capture_record(url: str, html: str, output_dir: Path) -> dict[str, Any]:
    slug = _slug_for_url(url)
    snapshot_file = output_dir / f"{slug}.html"
    snapshot_file.write_text(html, encoding="utf-8")
    title = _extract_title(html)
    return {
        "url": url,
        "status": "captured",
        "title": title,
        "forms": len(re.findall(r"<form\b", html, flags=re.IGNORECASE)),
        "links": len(re.findall(r"<a\b", html, flags=re.IGNORECASE)),
        "buttons": len(re.findall(r"<button\b", html, flags=re.IGNORECASE)),
        "inputs": len(re.findall(r"<input\b|<select\b|<textarea\b", html, flags=re.IGNORECASE)),
        "snapshot_file": str(snapshot_file),
        "html_excerpt": _excerpt(html),
    }


def _extract_title(html: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return unescape(re.sub(r"\s+", " ", match.group(1)).strip())


def _excerpt(html: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:280]


def _slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc or 'file'}{parsed.path}".strip("/") or "root"
    slug = "".join(character.lower() if character.isalnum() else "-" for character in raw)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "capture"
