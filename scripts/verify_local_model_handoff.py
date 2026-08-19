#!/usr/bin/env python3
"""Verify that the remote repository is ready for governed local execution."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_local_model_campaign import validate_campaign  # noqa: E402


def main() -> int:
    campaign, errors = validate_campaign(ROOT)
    required = [
        "governance/upstream.lock.json",
        "evaluations/reviews/benchmark_freeze_v1.json",
        "config/model_evidence_policy.yml",
        "config/model_selection_state.yml",
        "config/adtc_standard_laptop.yml",
        "docs/LOCAL_MODEL_EXECUTION_HANDOFF.md",
        "docs/SEMANTIC_ADJUDICATION_PROTOCOL.md",
        "scripts/run_local_inference.py",
        "scripts/run_evaluation.py",
        "scripts/convert_to_gguf.py",
        "scripts/quantize_model.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    errors.extend(f"missing:{path}" for path in missing)
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        head = "unavailable"
        errors.append("git_head_unavailable")
    payload = {
        "valid": not errors,
        "errors": errors,
        "source_commit": head,
        "local_setup_ready": not errors,
        "eligibility_gate": campaign.get("authority", {}).get("eligibility_gate"),
        "downloads_allowed": campaign.get("authority", {}).get("downloads_allowed"),
        "empirical_execution_authorized": campaign.get("authority", {}).get("empirical_execution_allowed"),
        "next_action": (
            "record eligibility and attributable execution authorization"
            if not campaign.get("authority", {}).get("empirical_execution_allowed")
            else "begin one exact candidate at a time"
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
