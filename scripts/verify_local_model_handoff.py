#!/usr/bin/env python3
"""Verify readiness for development-only governed local execution."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_local_model_campaign import (  # noqa: E402
    development_r_and_d_authorized,
    validate_campaign,
)


def main() -> int:
    campaign, errors = validate_campaign(ROOT)
    required = [
        "governance/upstream.lock.json",
        "evaluations/BENCHMARK_FREEZE.json",
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
    development_authorized = not errors and development_r_and_d_authorized(campaign)
    payload = {
        "valid": not errors,
        "errors": errors,
        "source_commit": head,
        "local_setup_ready": not errors,
        "authorization_scope": "private_product_r_and_d" if development_authorized else "none",
        "development_r_and_d_authorized": development_authorized,
        "eligibility_gate": campaign.get("authority", {}).get("eligibility_gate"),
        "contest_path_authorized": False,
        "downloads_allowed": development_authorized,
        "empirical_execution_authorized": development_authorized,
        "next_action": (
            "record an attributable development-only execution authorization"
            if not development_authorized
            else "acquire one licensed public-no-credential candidate revision at a time"
        ),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
