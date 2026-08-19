#!/usr/bin/env python3
"""Create a sanitized evidence record after a real local model run."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _require(pattern: re.Pattern[str], value: str, label: str) -> str:
    lowered = value.lower()
    if not pattern.fullmatch(lowered):
        raise ValueError(f"{label} has invalid format")
    return lowered


def build_record(args: argparse.Namespace) -> dict:
    started = args.started_at or datetime.now(timezone.utc).isoformat()
    finished = args.finished_at or datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "run_id": args.run_id,
        "campaign_id": args.campaign_id,
        "evidence_class": "local_real_model_output",
        "model_executed": True,
        "measured": True,
        "eligible_for_model_selection": False,
        "eligible_for_submission_score": False,
        "source_commit": _require(HEX40, args.source_commit, "source commit"),
        "candidate": {
            "candidate_id": args.candidate_id,
            "repository": args.repository,
            "revision": _require(HEX40, args.revision, "candidate revision"),
            "license_identifier": args.license_identifier,
        },
        "artifact": {
            "gguf_sha256": _require(HEX64, args.gguf_sha256, "GGUF SHA-256"),
            "byte_size": args.byte_size,
            "quantization": args.quantization,
            "local_path_exported": False,
        },
        "runtime": {
            "executor": "llama.cpp",
            "llama_cpp_commit": _require(HEX40, args.llama_cpp_commit, "llama.cpp commit"),
            "prompt_template": "chatml",
            "mode": args.mode,
            "configuration_sha256": _require(HEX64, args.configuration_sha256, "configuration SHA-256"),
            "command_exported": False,
        },
        "benchmark": {
            "freeze_id": args.freeze_id,
            "aggregate_sha256": _require(HEX64, args.benchmark_sha256, "benchmark SHA-256"),
            "case_count": 60,
        },
        "host": {
            "measurement_class": args.measurement_class,
            "attestation_sha256": _require(HEX64, args.host_attestation_sha256, "host attestation SHA-256"),
            "eligible_for_submission_score": False,
        },
        "timestamps": {"started_at": started, "finished_at": finished},
        "outputs": {
            "raw_bundle_sha256": _require(HEX64, args.raw_bundle_sha256, "raw bundle SHA-256"),
            "response_manifest_sha256": _require(HEX64, args.response_manifest_sha256, "response manifest SHA-256"),
            "raw_text_exported": False,
            "prompt_text_exported": False,
            "response_text_exported": False,
        },
        "semantic_review_status": "pending",
        "limitations": [
            "Qualified semantic adjudication is pending.",
            "This local run is not official ADTC performance or thermal evidence.",
        ],
    }


def validate_record(record: dict, root: Path = ROOT) -> list[str]:
    schema = json.loads((root / "schemas/model_run_evidence.schema.json").read_text(encoding="utf-8"))
    return [
        f"{error.json_path}:{error.message}"
        for error in sorted(Draft202012Validator(schema).iter_errors(record), key=lambda item: list(item.path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    for flag in (
        "run_id", "campaign_id", "source_commit", "candidate_id", "repository",
        "revision", "license_identifier", "gguf_sha256", "quantization",
        "llama_cpp_commit", "configuration_sha256", "freeze_id",
        "benchmark_sha256", "host_attestation_sha256", "raw_bundle_sha256",
        "response_manifest_sha256",
    ):
        parser.add_argument(f"--{flag.replace('_', '-')}", required=True)
    parser.add_argument("--byte-size", type=int, required=True)
    parser.add_argument("--mode", choices=["native", "contract", "mode_c"], required=True)
    parser.add_argument("--measurement-class", choices=["simulation_only", "reference_match"], required=True)
    parser.add_argument("--started-at")
    parser.add_argument("--finished-at")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    record = build_record(args)
    errors = validate_record(record)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"valid": True, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
