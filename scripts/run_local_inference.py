#!/usr/bin/env python3
"""Run explicit simulation-proxy or real digest-bound local inference."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
    parser = argparse.ArgumentParser(description="Run local MethodBridge inference")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--prompt", default="Distinguish an observation from a causal inference.")
    parser.add_argument("--candidate", default="qwen25_1_5b_instruct")
    parser.add_argument("--mode", choices=["native", "contract", "mode_c"], default="contract")
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument(
        "--simulation-proxy",
        action="store_true",
        help="Explicitly use the canned plumbing proxy; no model is loaded.",
    )
    execution.add_argument("--model-path", type=Path)
    parser.add_argument("--expected-model-sha256")
    parser.add_argument("--llama-cli", default="llama-cli")
    parser.add_argument("--prompt-template", choices=["chatml"])
    parser.add_argument("--llama-cpp-commit", default=_locked_llama_commit())
    parser.add_argument("--context-size", type=int, default=2048)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    if args.dry_run:
        print(
            json.dumps(
                {
                    "action": "run local inference",
                    "executed": False,
                    "status": "requires_explicit_executor",
                    "allowed_executors": ["simulation_proxy", "llama_cpp"],
                    "candidate": args.candidate,
                    "prompt_mode": args.mode,
                },
                indent=2,
            )
        )
        return 0

    if not args.simulation_proxy and args.model_path is None:
        parser.error("choose --simulation-proxy or provide --model-path")
    if args.model_path is not None and not args.expected_model_sha256:
        parser.error("--expected-model-sha256 is required with --model-path")
    if args.model_path is not None and not args.prompt_template:
        parser.error("--prompt-template is required with --model-path")

    if args.simulation_proxy:
        if args.mode == "mode_c":
            result = run_simulation_proxy_mode_c(
                args.prompt,
                candidate_id=args.candidate,
                explicit_acknowledgement=True,
            )
        else:
            result = run_simulation_proxy(
                args.prompt,
                candidate_id=args.candidate,
                mode=args.mode,
                explicit_acknowledgement=True,
            )
    else:
        common = {
            "prompt": args.prompt,
            "candidate_id": args.candidate,
            "model_path": args.model_path,
            "expected_model_sha256": args.expected_model_sha256,
            "llama_cpp_commit": args.llama_cpp_commit,
            "llama_cli": args.llama_cli,
            "prompt_template": args.prompt_template,
            "context_size": args.context_size,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "threads": args.threads,
            "timeout_seconds": args.timeout_seconds,
        }
        result = (
            run_candidate_inference_mode_c(**common)
            if args.mode == "mode_c"
            else run_candidate_inference(mode=args.mode, **common)
        )

    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
