from __future__ import annotations

import struct
from pathlib import Path
from typing import Any


UI_TOKENS = (
    "login",
    "dashboard",
    "form",
    "table",
    "admin",
    "portal",
    "settings",
    "queue",
    "report",
    "wizard",
    "onboarding",
    "profile",
)


def analyze_visual_artifact(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    dimensions = _detect_dimensions(path)
    filename = path.stem.lower()
    visual_hints = [token for token in UI_TOKENS if token in filename]
    viewport_kind = _viewport_kind(dimensions)
    confidence = 0.58
    if dimensions["width"] and dimensions["height"]:
        confidence += 0.12
    if visual_hints:
        confidence += 0.1
    return {
        "source": str(path),
        "type": suffix.lstrip("."),
        "dimensions": dimensions,
        "viewport_kind": viewport_kind,
        "screen_candidates": _screen_candidates_from_name(path.stem),
        "visual_hints": visual_hints,
        "confidence": round(min(confidence, 0.85), 4),
    }


def _screen_candidates_from_name(name: str) -> list[str]:
    cleaned = name.replace("_", " ").replace("-", " ").strip()
    if not cleaned:
        return []
    return [cleaned.title()]


def _viewport_kind(dimensions: dict[str, int | None]) -> str:
    width = dimensions.get("width") or 0
    height = dimensions.get("height") or 0
    if not width or not height:
        return "unknown"
    if width <= 540:
        return "mobile"
    if width <= 900:
        return "tablet"
    return "desktop"


def _detect_dimensions(path: Path) -> dict[str, int | None]:
    try:
        with path.open("rb") as handle:
            header = handle.read(32)
    except OSError:
        return {"width": None, "height": None}

    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        width, height = struct.unpack(">II", header[16:24])
        return {"width": int(width), "height": int(height)}

    if header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
        width, height = struct.unpack("<HH", header[6:10])
        return {"width": int(width), "height": int(height)}

    if header.startswith(b"\xff\xd8"):
        return _jpeg_dimensions(path)

    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return _webp_dimensions(path)

    return {"width": None, "height": None}


def _jpeg_dimensions(path: Path) -> dict[str, int | None]:
    try:
        with path.open("rb") as handle:
            handle.read(2)
            while True:
                marker_start = handle.read(1)
                if not marker_start:
                    break
                if marker_start != b"\xff":
                    continue
                marker = handle.read(1)
                while marker == b"\xff":
                    marker = handle.read(1)
                if marker in {b"\xc0", b"\xc1", b"\xc2", b"\xc3", b"\xc5", b"\xc6", b"\xc7", b"\xc9", b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"}:
                    length = struct.unpack(">H", handle.read(2))[0]
                    _precision = handle.read(1)
                    height, width = struct.unpack(">HH", handle.read(4))
                    return {"width": int(width), "height": int(height)}
                elif marker in {b"\xd8", b"\xd9"}:
                    continue
                else:
                    length_bytes = handle.read(2)
                    if len(length_bytes) != 2:
                        break
                    length = struct.unpack(">H", length_bytes)[0]
                    handle.seek(max(length - 2, 0), 1)
    except OSError:
        pass
    return {"width": None, "height": None}


def _webp_dimensions(path: Path) -> dict[str, int | None]:
    try:
        with path.open("rb") as handle:
            data = handle.read(64)
    except OSError:
        return {"width": None, "height": None}

    if data[12:16] == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return {"width": int(width & 0x3FFF), "height": int(height & 0x3FFF)}
    if data[12:16] == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
        return {"width": int(width), "height": int(height)}
    if data[12:16] == b"VP8X" and len(data) >= 30:
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return {"width": width, "height": height}
    return {"width": None, "height": None}
