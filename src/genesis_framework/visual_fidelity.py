from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def default_visual_lock_spec(screen_id: str, mode: str = "modernized_fidelity") -> dict[str, Any]:
    return {
        "schema_version": "3.1.0",
        "mode": mode,
        "screens": [
            {
                "screen_id": screen_id,
                "source_refs": [],
                "must_match": {
                    "layout": True,
                    "spacing": True,
                    "typography": True,
                    "colors": True,
                    "component_positions": True,
                    "visible_content": True,
                },
                "allowed_changes": {
                    "modernize_icons": mode == "modernized_fidelity",
                    "improve_accessibility": True,
                    "improve_responsiveness": True,
                },
                "blocked_changes": {
                    "change_navigation_model": True,
                    "change_primary_layout": mode == "exact_fidelity",
                    "remove_visible_content": True,
                },
                "thresholds": {
                    "minor_spacing_tolerance_px": 8,
                    "max_unexplained_pixel_diff_ratio": 0.03,
                    "min_visual_parity_score": 0.90,
                },
            }
        ],
    }


def write_visual_lock_spec(path: Path, screen_id: str, mode: str = "modernized_fidelity") -> Path:
    spec = default_visual_lock_spec(screen_id, mode)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return path


def bbox_delta(source: dict[str, float], generated: dict[str, float]) -> dict[str, float]:
    return {
        "x": generated.get("x", 0) - source.get("x", 0),
        "y": generated.get("y", 0) - source.get("y", 0),
        "width": generated.get("width", 0) - source.get("width", 0),
        "height": generated.get("height", 0) - source.get("height", 0),
    }

