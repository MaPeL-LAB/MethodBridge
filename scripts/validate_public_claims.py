#!/usr/bin/env python3
"""Reject unsupported public model, performance, and release claims."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_FILES = (
    "README.md",
    "REPORT.md",
    "MODEL_CARD.md",
    "model/README.md",
    "docs/DEVPOST_SUBMISSION_DRAFT.md",
    "docs/DEMO_VIDEO_STORYBOARD.md",
    "BOOTSTRAP_STATUS.md",
)

PROHIBITED = {
    r"\b31\.2\s*(?:tps|tokens?/?s)\b": "unsupported throughput",
    r"\b26\.8\s*(?:tps|tokens?/?s)\b": "unsupported throughput",
    r"\b22\.4\s*(?:tps|tokens?/?s)\b": "unsupported throughput",
    r"\b1\.93\s*gib\b": "unsupported peak-memory result",
    r"\b99\.2%\b": "unsupported reasoning-retention claim",
    r"\b0\.0?4\s+perplexity\b": "unsupported perplexity claim",
    r"\b0\.14\s+perplexity\b": "unsupported perplexity claim",
    r"\bpareto optimum\b": "unsupported Pareto conclusion",
    r"\b5[- ]candidate bake[- ]off\b": "unsubstantiated empirical bake-off",
    r"\bqwen3-1\.7b winner\b": "premature winner claim",
    r"\bselected quantization\b": "premature quantization selection",
    r"\bfinal model is\b": "premature final model claim",
}

REQUIRED_MARKERS = ("submission ready", "no final model", "simulation")


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for relative in PUBLIC_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing public-claim surface: {relative}")
            continue
        texts[relative] = path.read_text(encoding="utf-8")
    combined = "\n".join(texts.values()).lower()
    for pattern, label in PROHIBITED.items():
        if re.search(pattern, combined, flags=re.IGNORECASE):
            errors.append(label)
    for marker in REQUIRED_MARKERS:
        if marker not in combined:
            errors.append(f"missing fail-closed marker: {marker}")
    if "REQUIRES_EMPIRICAL_SELECTION" not in (root / "metadata.json").read_text(encoding="utf-8"):
        errors.append("metadata lost unresolved quantization placeholder")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
