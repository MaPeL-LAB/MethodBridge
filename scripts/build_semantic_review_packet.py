#!/usr/bin/env python3
"""Build a privacy-preserving, pending semantic-review record."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def build_packet(run: dict, response_manifest: dict, reviewer_name: str, reviewer_role: str) -> dict:
    cases = []
    for item in response_manifest.get("responses", []):
        cases.append(
            {
                "case_id": item["case_id"],
                "response_sha256": item["response_sha256"],
                "judgment": "human_review_required",
                "error_categories": [],
                "rationale": "Pending qualified semantic adjudication.",
            }
        )
    return {
        "schema_version": 1,
        "review_id": f"review-{run['run_id']}",
        "run_id": run["run_id"],
        "benchmark": run["benchmark"],
        "reviewer": {
            "name": reviewer_name,
            "role": reviewer_role,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "conflict_declaration": "Pending reviewer confirmation.",
        },
        "cases": cases,
        "aggregate": {
            "pass": 0,
            "fail": 0,
            "inconclusive": 0,
            "human_review_required": len(cases),
            "test_error": 0,
        },
        "decision": {
            "status": "pending",
            "eligible_for_comparison": False,
            "limitations": ["No case has been semantically adjudicated."],
        },
        "raw_prompt_exported": False,
        "raw_response_exported": False,
    }


def validate_packet(packet: dict, root: Path = ROOT) -> list[str]:
    schema = json.loads(
        (root / "schemas/semantic_review_record.schema.json").read_text(encoding="utf-8")
    )
    return [
        f"{error.json_path}:{error.message}"
        for error in Draft202012Validator(schema).iter_errors(packet)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-record", type=Path, required=True)
    parser.add_argument("--response-manifest", type=Path, required=True)
    parser.add_argument("--reviewer-name", required=True)
    parser.add_argument("--reviewer-role", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run = json.loads(args.run_record.read_text(encoding="utf-8"))
    responses = json.loads(args.response_manifest.read_text(encoding="utf-8"))
    packet = build_packet(run, responses, args.reviewer_name, args.reviewer_role)
    errors = validate_packet(packet)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"valid": True, "cases": len(packet["cases"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
