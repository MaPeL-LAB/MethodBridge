#!/usr/bin/env python3
"""Run the local-only challenger without exporting prompt or response text."""
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
from methodbridge.hardware import classify_host, detect_host, load_profile, make_attestation
from methodbridge.inference.runner import (
    run_candidate_inference,
    run_candidate_inference_mode_c,
    run_simulation_proxy,
    run_simulation_proxy_mode_c,
)


def _locked_llama_commit() -> str:
    lock = load_json(ROOT / "governance/upstream.lock.json")
    return next(item["commit"] for item in lock["upstreams"] if item["name"] == "llama.cpp")


def load_private_cases(root: Path) -> list[dict]:
    cases_dir = root / "private_evaluations/cases"
    if not cases_dir.exists():
        raise FileNotFoundError(f"Private evaluations directory not found at {cases_dir}")
    return [load_json(path) for path in sorted(cases_dir.glob("CH-OOD-*.json"))]


def canonical_hash(case: dict) -> str:
    raw = json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_challenger_freeze(root: Path, cases: list[dict]) -> tuple[bool, str, list[str]]:
    freeze_path = root / "private_evaluations/CHALLENGER_FREEZE.json"
    if not freeze_path.exists():
        return False, "", ["Missing CHALLENGER_FREEZE.json"]
    freeze = load_json(freeze_path)
    recorded = {item["case_id"]: item["sha256"] for item in freeze.get("case_hashes", [])}
    current = {case["case_id"]: canonical_hash(case) for case in cases}
    errors: list[str] = []
    if len(cases) != freeze.get("case_count", 0):
        errors.append(f"Case count mismatch: found {len(cases)}, freeze specifies {freeze.get('case_count')}")
    for case_id, digest in current.items():
        if case_id not in recorded:
            errors.append(f"Case {case_id} not present in freeze record")
        elif recorded[case_id] != digest:
            errors.append(f"Case {case_id} hash mismatch")
    aggregate = "".join(f"{case_id}:{current[case_id]}\n" for case_id in sorted(current)).encode("utf-8")
    aggregate_digest = hashlib.sha256(aggregate).hexdigest()
    if aggregate_digest != freeze.get("challenger_sha256"):
        errors.append("Aggregate challenger hash mismatch")
    return not errors, freeze.get("challenger_sha256", ""), errors


def _sanitized_case_result(case: dict, inference, proxy: dict) -> dict:
    """Return shareable fields without prompt, response, or rubric text."""
    return {
        "case_id": case["case_id"],
        "family": case.get("family", "unknown"),
        "subdomain": case.get("subdomain", "unknown"),
        "output_sha256": inference.response_sha256,
        "executor_kind": inference.executor_kind,
        "evidence_class": inference.evidence_class,
        "model_output_measured": inference.measured,
        "automated_proxy": proxy["automated_proxy"],
        "proxy_pass": proxy["proxy_pass"],
        "proxy_points_covered_count": len(proxy["proxy_points_covered"]),
        "proxy_points_missed_count": len(proxy["proxy_points_missed"]),
        "proxy_prohibited_error_count": len(proxy["proxy_prohibited_errors_triggered"]),
        "semantic_review_required": True,
    }


def run_private_mode_evaluation(cases: list[dict], *, candidate_id: str, mode: str, executor) -> dict:
    results: list[dict] = []
    for case in cases:
        inference = executor(case["prompt"], candidate_id, mode)
        proxy = evaluate_case_response(case, inference.response)
        results.append(_sanitized_case_result(case, inference, proxy))
    proxy_passed = sum(1 for result in results if result["proxy_pass"])
    return {
        "candidate_id": candidate_id,
        "mode": mode,
        "total_cases": len(cases),
        "automated_proxy": "keyword_overlap_v1",
        "automated_keyword_proxy_passed_cases": proxy_passed,
        "automated_keyword_proxy_pass_rate": round(proxy_passed / len(cases), 4) if cases else 0.0,
        "semantic_review_status": "required",
        "eligible_for_automatic_model_selection": False,
        "eligible_for_model_selection": False,
        "eligible_for_submission_score": False,
        "case_results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run private challenger evaluation")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--candidate", default="qwen3_1_7b")
    parser.add_argument("--mode", choices=["native", "contract", "mode_c", "both", "all"], default="all")
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument("--simulation-proxy", action="store_true")
    execution.add_argument("--model-path", type=Path)
    parser.add_argument("--expected-model-sha256")
    parser.add_argument("--llama-cli", default="llama-cli")
    parser.add_argument("--prompt-template", choices=["chatml"])
    parser.add_argument("--llama-cpp-commit", default=_locked_llama_commit())
    parser.add_argument("--context-size", type=int, default=2048)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        cases = load_private_cases(ROOT)
    except Exception as exc:
        print(f"Error loading private cases: {exc}", file=sys.stderr)
        return 1

    errors = {case["case_id"]: structural_check(case) for case in cases if structural_check(case)}
    freeze_valid, freeze_sha256, freeze_errors = verify_challenger_freeze(ROOT, cases)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "mode": "dry-run",
                    "case_count": len(cases),
                    "freeze_valid": freeze_valid,
                    "freeze_sha256": freeze_sha256,
                    "freeze_errors": freeze_errors,
                    "structural_errors": errors,
                    "model_results": None,
                },
                indent=2,
            )
        )
        return 1 if errors or freeze_errors else 0
    if errors or not freeze_valid:
        print("Private challenger structure or freeze validation failed", file=sys.stderr)
        return 1
    if not args.simulation_proxy and args.model_path is None:
        parser.error("choose --simulation-proxy or provide --model-path")
    if args.model_path is not None and not args.expected_model_sha256:
        parser.error("--expected-model-sha256 is required with --model-path")
    if args.model_path is not None and not args.prompt_template:
        parser.error("--prompt-template is required with --model-path")

    if args.simulation_proxy:
        def executor(prompt: str, candidate_id: str, mode: str):
            if mode == "mode_c":
                return run_simulation_proxy_mode_c(
                    prompt,
                    candidate_id=candidate_id,
                    explicit_acknowledgement=True,
                )
            return run_simulation_proxy(
                prompt,
                candidate_id=candidate_id,
                mode=mode,
                explicit_acknowledgement=True,
            )
        execution_kind = "simulation_proxy"
    else:
        def executor(prompt: str, candidate_id: str, mode: str):
            common = {
                "prompt": prompt,
                "candidate_id": candidate_id,
                "model_path": args.model_path,
                "expected_model_sha256": args.expected_model_sha256,
                "llama_cpp_commit": args.llama_cpp_commit,
                "llama_cli": args.llama_cli,
                "prompt_template": args.prompt_template,
                "context_size": args.context_size,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "timeout_seconds": args.timeout_seconds,
            }
            return (
                run_candidate_inference_mode_c(**common)
                if mode == "mode_c"
                else run_candidate_inference(mode=mode, **common)
            )
        execution_kind = "llama_cpp"

    modes = {
        "both": ["native", "contract"],
        "all": ["native", "contract", "mode_c"],
    }.get(args.mode, [args.mode])
    profile = load_profile(ROOT / "config/adtc_standard_laptop.yml")
    facts = detect_host()
    classification = classify_host(facts, profile)
    attestation = make_attestation(facts, classification, profile)
    results = {
        mode: run_private_mode_evaluation(cases, candidate_id=args.candidate, mode=mode, executor=executor)
        for mode in modes
    }
    payload = {
        "suite_type": "private_challenger_ood",
        "benchmark_version": "1.0.0",
        "freeze_id": "methodbridge-private-challenger-v1.0.0",
        "freeze_sha256": freeze_sha256,
        "candidate_id": args.candidate,
        "execution_kind": execution_kind,
        "host_attestation": attestation,
        "privacy_contract": {
            "prompt_text_exported": False,
            "response_text_exported": False,
            "rubric_text_exported": False,
            "shareable_output_contains_hashes_and_counts_only": True,
        },
        "modes_evaluated": results,
        "summary": {
            "measurement_class": classification.measurement_class,
            "eligible_for_submission_score": False,
            "eligible_for_automatic_model_selection": False,
            "semantic_review_status": "required",
        },
    }
    text = json.dumps(payload, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote private challenger artifact to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
