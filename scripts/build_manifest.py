#!/usr/bin/env python3
"""Build or check the deterministic tracked-file manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"


def tracked_paths() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8"))
        if rel.as_posix() == "MANIFEST.json":
            continue
        path = ROOT / rel
        if path.is_file():
            paths.append(rel)
    return sorted(paths, key=lambda p: p.as_posix())


def category_for(rel: Path) -> str:
    return rel.parts[0] if len(rel.parts) > 1 else "root"


def build_manifest() -> dict:
    files = []
    for rel in tracked_paths():
        data = (ROOT / rel).read_bytes()
        files.append(
            {
                "path": rel.as_posix(),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "category": category_for(rel),
                "source_status": "tracked_repository",
                "implementation_status": "bootstrap",
                "sensitivity": "public_synthetic_or_documentation",
            }
        )
    return {
        "repository": "methodbridge-local",
        "release": "v0.1.0-bootstrap",
        "provenance_note": (
            "The initial public bootstrap was reconstructed from retained research "
            "artifacts. The tracked Git repository is now the authoritative source."
        ),
        "file_count_excluding_manifest": len(files),
        "manifest_self_excluded": True,
        "files": files,
    }


def canonical_text(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="Fail if MANIFEST.json is stale")
    group.add_argument("--write", action="store_true", help="Rewrite MANIFEST.json")
    args = parser.parse_args()

    expected = canonical_text(build_manifest())
    if args.write or not args.check:
        MANIFEST.write_text(expected, encoding="utf-8")
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
        return 0

    current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
    if current != expected:
        print("MANIFEST.json is stale; run: python scripts/build_manifest.py --write")
        return 1
    print("MANIFEST.json is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
