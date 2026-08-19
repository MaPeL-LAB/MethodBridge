#!/usr/bin/env python3
"""Run local candidate inference in dry-run, native, or contract mode."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.inference.runner import run_candidate_inference


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local candidate inference")
    parser.add_argument("--dry-run", action="store_true", help="Inspect contract without execution")
    parser.add_argument("--prompt", type=str, default="Distinguish an observation from a causal inference.")
    parser.add_argument("--candidate", type=str, default="qwen25_1_5b_instruct")
    parser.add_argument("--mode", choices=["native", "contract", "methodbridge_contract"], default="contract")
    args = parser.parse_args()

    if args.dry_run:
        print(json.dumps({
            "action": "run llama.cpp inference",
            "mode": "dry-run",
            "executed": False,
            "status": "requires_empirical_phase",
            "candidate": args.candidate,
            "prompt_mode": args.mode,
        }, indent=2))
        return 0

    result = run_candidate_inference(
        prompt=args.prompt,
        candidate_id=args.candidate,
        mode=args.mode,
    )
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
