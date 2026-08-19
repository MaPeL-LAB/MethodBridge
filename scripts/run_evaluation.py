#!/usr/bin/env python3
"""Run structural checks or a provenance-labelled benchmark evaluation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.evaluation import load_cases, run_benchmark_evaluation, structural_check
from methodbridge.hardware import classify_host, detect_host, load_profile, make_attestation
from methodbridge.inference.runner import (
    run_candidate_inference,
    run_candidate_inference_mode_c,
    run_simulation_proxy,
    run_simulation_proxy_mode_c,
)


def _locked_llama_commit() -> str:
    lock = json.loads((ROOT / "governance/upstream.lock.json").read_text(encoding="utf-8"))
    return next(item["commit"] for item in lock["upstreams"] if item["name"] == "llama.cpp")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MethodBridge benchmark evaluation")
    parser.add_argument("--dry-run", action="store_true", help="Check benchmark structure only")
    parser.add_argument("--candidate", default="qwen25_1_5b_instruct")
    parser.add_argument(
        "--mode",
        choices=["native", "contract", "mode_c", "both", "all"],
        default="both",
    )
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument(
        "--simulation-proxy",
        action="store_true",
        help="Explicitly run the canned plumbing proxy; never model evidence.",
    )
    execution.add_argument("--model-path", type=Path, help="Actual GGUF for llama.cpp execution")
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

    cases = load_cases(ROOT)
    errors = {case["case_id"]: structural_check(case) for case in cases if structural_check(case)}
    executable = sum(1 for case in cases if case.get("bootstrap_executable"))

    if args.dry_run:
        result = {
            "mode": "dry-run",
            "case_count": len(cases),
            "bootstrap_executable_count": executable,
            "structural_errors": errors,
            "model_results": None,
            "evidence_status": "no_model_execution",
        }
        print(json.dumps(result, indent=2))
        return 1 if errors else 0

    if errors:
        print(f"Benchmark structural errors detected: {len(errors)} invalid cases", file=sys.stderr)
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
        requested_execution = "simulation_proxy"
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
            if mode == "mode_c":
                return run_candidate_inference_mode_c(**common)
            return run_candidate_inference(mode=mode, **common)
        requested_execution = "llama_cpp"

    modes = {
        "both": ["native", "contract"],
        "all": ["native", "contract", "mode_c"],
    }.get(args.mode, [args.mode])

    profile = load_profile(ROOT / "config/adtc_standard_laptop.yml")
    facts = detect_host()
    classification = classify_host(facts, profile)
    attestation = make_attestation(facts, classification, profile)

    results_by_mode = {
        mode: run_benchmark_evaluation(
            ROOT,
            candidate_id=args.candidate,
            mode=mode,
            executor=executor,
        )
        for mode in modes
    }

    payload = {
        "benchmark_version": "1.0.0",
        "freeze_id": "methodbridge-public-benchmark-v1.0.0",
        "candidate_id": args.candidate,
        "requested_execution": requested_execution,
        "host_attestation": attestation,
        "modes_evaluated": results_by_mode,
        "summary": {
            "candidate_id": args.candidate,
            "host_measurement_class": classification.measurement_class,
            "eligible_for_submission_score": False,
            "eligible_for_automatic_model_selection": False,
            "semantic_review_status": "required",
            "native_automated_keyword_proxy_pass_rate": results_by_mode.get("native", {}).get(
                "automated_keyword_proxy_pass_rate"
            ),
            "contract_automated_keyword_proxy_pass_rate": results_by_mode.get("contract", {}).get(
                "automated_keyword_proxy_pass_rate"
            ),
            "mode_c_automated_keyword_proxy_pass_rate": results_by_mode.get("mode_c", {}).get(
                "automated_keyword_proxy_pass_rate"
            ),
        },
    }

    text = json.dumps(payload, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote evaluation artifact to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
