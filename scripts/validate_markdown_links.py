#!/usr/bin/env python3
"""Validate repository-relative links in Markdown files."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    errors: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip()
            if not target or target.startswith(("#", "mailto:")) or "://" in target:
                continue
            target = target.split("#", 1)[0]
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)} -> {raw_target}")
    if errors:
        print("Broken repository-relative Markdown links:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Markdown links are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
