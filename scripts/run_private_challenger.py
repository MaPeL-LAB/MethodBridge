#!/usr/bin/env python3
"""Run private out-of-distribution challenger evaluation suite across Mode A, Mode B, and Mode C."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.data import load_json
from methodbridge.evaluation import evaluate_case_response, structural_check
from methodbridge.hardware import detect_host, classify_host, load_profile, make_attestation
from methodbridge.inference.runner import run_candidate_inference, run_candidate_inference_mode_c


def load_private_cases(root: Path) -> list[dict]:
    cases_dir = root / "private_evaluations/cases"
    if not cases_dir.exists():
        raise FileNotFoundError(f"Private evaluations directory not found at {cases_dir}")
    return [load_json(p) for p in sorted(cases_dir.glob("CH-OOD-*.json"))]


def canonical_hash(case: dict) -> str:
    raw = json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_challenger_freeze(root: Path, cases: list[dict]) -> tuple[bool, str, list[str]]:
    freeze_path = root / "private_evaluations/CHALLENGER_FREEZE.json"
    if not freeze_path.exists():
        return False, "", ["Missing CHALLENGER_FREEZE.json"]
    
    freeze = load_json(freeze_path)
    recorded_hashes = {r["case_id"]: r["sha256"] for r in freeze.get("case_hashes", [])}
    current_hashes = {c["case_id"]: canonical_hash(c) for c in cases}
    
    errors = []
    if len(cases) != freeze.get("case_count", 0):
        errors.append(f"Case count mismatch: found {len(cases)}, freeze specifies {freeze.get('case_count')}")
    
    for cid, cur_h in current_hashes.items():
        if cid not in recorded_hashes:
            errors.append(f"Case {cid} not present in freeze record")
        elif recorded_hashes[cid] != cur_h:
            errors.append(f"Case {cid} hash mismatch (expected {recorded_hashes[cid]}, computed {cur_h})")
            
    aggregate = "".join(f"{cid}:{current_hashes[cid]}\n" for cid in sorted(current_hashes)).encode("utf-8")
    computed_aggregate = hashlib.sha256(aggregate).hexdigest()
    if computed_aggregate != freeze.get("challenger_sha256"):
        errors.append(f"Aggregate challenger hash mismatch: expected {freeze.get('challenger_sha256')}, computed {computed_aggregate}")
        
    return len(errors) == 0, freeze.get("challenger_sha256", ""), errors


def run_private_mode_evaluation(
    cases: list[dict],
    candidate_id: str = "qwen3_1_7b",
    mode: str = "native",
) -> dict:
    case_results = []
    total_tokens_prompt = 0
    total_tokens_gen = 0
    total_time_ms = 0.0
    
    dimension_map = {
        "general_scientific_reasoning": "Dimension I: General Scientific Reasoning",
        "causal_estimands_and_dags": "Dimension II: Causal Estimands & DAGs",
        "multiplicity_and_phacking": "Dimension III: Multiplicity & P-Hacking",
        "adversarial_citations_and_integrity": "Dimension IV: Adversarial Citations & Integrity",
    }
    
    dimension_scores = {dim_key: {"total": 0, "passed": 0} for dim_key in dimension_map}

    for case in cases:
        fam = case.get("family", "unknown")
        if fam in dimension_scores:
            dimension_scores[fam]["total"] += 1

        if mode == "mode_c":
            inf = run_candidate_inference_mode_c(case["prompt"], candidate_id=candidate_id)
        else:
            inf = run_candidate_inference(case["prompt"], candidate_id=candidate_id, mode=mode)

        eval_res = evaluate_case_response(case, inf.response)
        
        if eval_res["passed"] and fam in dimension_scores:
            dimension_scores[fam]["passed"] += 1

        # Sanitize output to prevent leaking confidential prompt texts
        sanitized_res = {
            "case_id": case["case_id"],
            "family": case.get("family", "unknown"),
            "subdomain": case.get("subdomain", "unknown"),
            "passed": eval_res["passed"],
            "points_covered": eval_res["points_covered"],
            "points_missed": eval_res["points_missed"],
            "prohibited_errors_triggered": eval_res["prohibited_errors_triggered"],
            "response_preview": inf.response[:120] + "..." if len(inf.response) > 120 else inf.response,
        }
        case_results.append(sanitized_res)
        total_tokens_prompt += inf.tokens_prompt
        total_tokens_gen += inf.tokens_generated
        total_time_ms += inf.total_time_ms

    passed_count = sum(1 for r in case_results if r["passed"])
    
    dimension_breakdown = {}
    for fam, stats in dimension_scores.items():
        label = dimension_map.get(fam, fam)
        dimension_breakdown[label] = {
            "total": stats["total"],
            "passed": stats["passed"],
            "pass_rate": round(stats["passed"] / max(1, stats["total"]), 4),
        }

    return {
        "candidate_id": candidate_id,
        "mode": mode,
        "total_cases": len(cases),
        "passed_cases": passed_count,
        "pass_rate": round(passed_count / len(cases), 4) if cases else 0.0,
        "avg_tokens_prompt": round(total_tokens_prompt / max(1, len(cases)), 1),
        "avg_tokens_gen": round(total_tokens_gen / max(1, len(cases)), 1),
        "total_time_sec": round(total_time_ms / 1000.0, 3),
        "dimension_breakdown": dimension_breakdown,
        "case_results": case_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run private challenger evaluation suite")
    parser.add_argument("--dry-run", action="store_true", help="Perform structural and freeze check without model execution")
    parser.add_argument("--candidate", type=str, default="qwen3_1_7b", help="Candidate identifier")
    parser.add_argument(
        "--mode",
        choices=["native", "contract", "mode_c", "both", "all"],
        default="all",
        help="Evaluation modes: native (Mode A), contract (Mode B), mode_c (Mode C), both (A+B), all (A+B+C)",
    )
    parser.add_argument("--output", type=str, default=None, help="Optional output artifact path")
    args = parser.parse_args()

    try:
        cases = load_private_cases(ROOT)
    except Exception as exc:
        print(f"Error loading private cases: {exc}", file=sys.stderr)
        return 1

    errors = {c["case_id"]: structural_check(c) for c in cases if structural_check(c)}
    freeze_valid, freeze_sha256, freeze_errors = verify_challenger_freeze(ROOT, cases)

    if args.dry_run:
        result = {
            "mode": "dry-run",
            "case_count": len(cases),
            "freeze_valid": freeze_valid,
            "freeze_sha256": freeze_sha256,
            "freeze_errors": freeze_errors,
            "structural_errors": errors,
            "model_results": None,
        }
        print(json.dumps(result, indent=2))
        return 1 if (errors or freeze_errors) else 0

    if errors:
        print(f"Structural errors detected in private cases: {len(errors)} cases invalid", file=sys.stderr)
        for cid, errs in errors.items():
            print(f"  {cid}: {errs}", file=sys.stderr)
        return 1

    if not freeze_valid:
        print(f"Freeze validation errors in private cases: {freeze_errors}", file=sys.stderr)
        return 1

    profile = load_profile(ROOT / "config/adtc_standard_laptop.yml")
    facts = detect_host()
    classification = classify_host(facts, profile)
    attestation = make_attestation(facts, classification, profile)

    if args.mode == "both":
        eval_modes = ["native", "contract"]
    elif args.mode == "all":
        eval_modes = ["native", "contract", "mode_c"]
    else:
        eval_modes = [args.mode]

    results_by_mode = {}
    for m in eval_modes:
        results_by_mode[m] = run_private_mode_evaluation(cases, candidate_id=args.candidate, mode=m)

    payload = {
        "suite_type": "private_challenger_ood",
        "benchmark_version": "1.0.0",
        "freeze_id": "methodbridge-private-challenger-v1.0.0",
        "freeze_sha256": freeze_sha256,
        "candidate_id": args.candidate,
        "host_attestation": attestation,
        "prompt_privacy": "strictly_redacted_no_leakage",
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
        print(f"Wrote private challenger evaluation artifact to {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
