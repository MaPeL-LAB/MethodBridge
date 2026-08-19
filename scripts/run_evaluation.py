#!/usr/bin/env python3
"""Run benchmark evaluation suite in dry-run structural check or candidate evaluation mode."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.evaluation import load_cases, structural_check, run_benchmark_evaluation
from methodbridge.hardware import detect_host, classify_host, load_profile, make_attestation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run benchmark evaluation suite")
    parser.add_argument("--dry-run", action="store_true", help="Perform structural check without model execution")
    parser.add_argument("--candidate", type=str, default="qwen25_1_5b_instruct", help="Candidate identifier")
    parser.add_argument(
        "--mode",
        choices=["native", "contract", "mode_c", "both", "all"],
        default="both",
        help=(
            "Prompt contract mode: "
            "native=Mode A (untouched), "
            "contract=Mode B (MethodBridge contract), "
            "mode_c=Mode C (task-level prompt router), "
            "both=A+B, all=A+B+C"
        ),
    )
    parser.add_argument("--output", type=str, default=None, help="Optional output artifact path")
    args = parser.parse_args()

    cases = load_cases(ROOT)
    errors = {c["case_id"]: structural_check(c) for c in cases if structural_check(c)}
    executable = sum(1 for c in cases if c.get("bootstrap_executable"))

    if args.dry_run:
        result = {
            "mode": "dry-run",
            "case_count": len(cases),
            "bootstrap_executable_count": executable,
            "structural_errors": errors,
            "model_results": None,
        }
        print(json.dumps(result, indent=2))
        return 1 if errors else 0

    if errors:
        print(f"Benchmark structural errors detected: {len(errors)} cases invalid", file=sys.stderr)
        return 1

    profile = load_profile(ROOT / "config/adtc_standard_laptop.yml")
    facts = detect_host()
    classification = classify_host(facts, profile)
    attestation = make_attestation(facts, classification, profile)

    # Determine which modes to run
    if args.mode == "both":
        eval_modes = ["native", "contract"]
    elif args.mode == "all":
        eval_modes = ["native", "contract", "mode_c"]
    else:
        eval_modes = [args.mode]

    results_by_mode = {}
    for m in eval_modes:
        results_by_mode[m] = run_benchmark_evaluation(ROOT, candidate_id=args.candidate, mode=m)

    payload = {
        "benchmark_version": "1.0.0",
        "freeze_id": "methodbridge-public-benchmark-v1.0.0",
        "candidate_id": args.candidate,
        "host_attestation": attestation,
        "modes_evaluated": results_by_mode,
        "summary": {
            "candidate_id": args.candidate,
            "measurement_class": classification.measurement_class,
            "eligible_for_submission_score": classification.eligible_for_submission_score,
            "native_mode_pass_rate": results_by_mode.get("native", {}).get("pass_rate"),
            "contract_mode_pass_rate": results_by_mode.get("contract", {}).get("pass_rate"),
            "mode_c_pass_rate": results_by_mode.get("mode_c", {}).get("pass_rate"),
        },
    }

    print(json.dumps(payload, indent=2))

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote evaluation artifact to {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
