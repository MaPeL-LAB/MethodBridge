#!/usr/bin/env python3
"""Validate the local empirical campaign without authorizing it."""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def validate_campaign(root: Path = ROOT) -> tuple[dict, list[str]]:
    document = yaml.safe_load((root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    schema = json.loads((root / "schemas/local_model_campaign.schema.json").read_text(encoding="utf-8"))
    errors = [
        f"schema:{error.json_path}:{error.message}"
        for error in sorted(Draft202012Validator(schema).iter_errors(document), key=lambda item: list(item.path))
    ]
    authority = document.get("authority", {})
    human = authority.get("human_execution_authorization", {})
    fully_authorized = (
        authority.get("eligibility_gate") == "pass"
        and human.get("status") == "recorded"
        and all(human.get(key) for key in ("actor", "timestamp", "decision_reference"))
    )
    if fully_authorized:
        if not authority.get("downloads_allowed"):
            errors.append("authorized campaign must allow downloads")
        if not authority.get("empirical_execution_allowed"):
            errors.append("authorized campaign must allow empirical execution")
        if document.get("status") != "authorized_for_local_execution":
            errors.append("authorized campaign has wrong status")
    else:
        if authority.get("downloads_allowed"):
            errors.append("downloads_allowed must remain false before authorization")
        if authority.get("empirical_execution_allowed"):
            errors.append("empirical_execution_allowed must remain false before authorization")
        if document.get("status") == "authorized_for_local_execution":
            errors.append("campaign claims authorization without eligibility and human record")
    candidates = [item["candidate_id"] for item in document.get("execution_order", [])]
    if len(candidates) != len(set(candidates)):
        errors.append("candidate IDs must be unique")
    if candidates[:3] != ["qwen25_1_5b_instruct", "qwen3_1_7b", "smollm3_3b"]:
        errors.append("primary candidate order changed without reviewed campaign update")
    if set(document.get("modes", [])) != {"native", "contract", "mode_c"}:
        errors.append("all three governed prompt modes are required")
    return document, errors


def main() -> int:
    document, errors = validate_campaign()
    payload = {
        "valid": not errors,
        "errors": errors,
        "campaign_id": document.get("campaign_id"),
        "campaign_status": document.get("status"),
        "local_setup_ready": not errors,
        "empirical_execution_authorized": bool(document.get("authority", {}).get("empirical_execution_allowed")),
        "downloads_allowed": bool(document.get("authority", {}).get("downloads_allowed")),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
