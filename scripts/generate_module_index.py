from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_FILES = sorted(ROOT.glob("**/module.yaml"))


def main() -> None:
    lines = ["# Genesis Module Index", ""]
    for path in MODULE_FILES:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rel = path.parent.relative_to(ROOT).as_posix()
        lines.append(f"## {rel}")
        lines.append("")
        lines.append(f"- name: `{data.get('name', path.parent.name)}`")
        lines.append(f"- status: `{data.get('status', 'unknown')}`")
        lines.append(f"- purpose: {data.get('purpose', 'not documented')}")
        lines.append("")
    output = ROOT / "MODULE_INDEX.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

