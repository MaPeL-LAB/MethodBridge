#!/usr/bin/env python3
"""Validate the fail-closed development-only local empirical campaign."""
from __future__ import annotations

import json
from pathlib import Path
import re

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_DECISION_REFERENCE = "EXEC-001"
DEVELOPMENT_DECISION_ACTOR = "Marothi Peter Letsoalo"
ACTIVE_CAMPAIGN_STATES = {"authorized_for_local_execution", "in_progress", "completed"}


def development_r_and_d_authorized(document: dict) -> bool:
    """Return true only for the attributable, development-only EXEC-001 grant."""
    authority = document.get("authority", {})
    human = authority.get("human_execution_authorization", {})
    return (
        human.get("status") == "recorded"
        and human.get("actor") == DEVELOPMENT_DECISION_ACTOR
        and human.get("decision_reference") == DEVELOPMENT_DECISION_REFERENCE
        and bool(human.get("timestamp"))
        and authority.get("downloads_allowed") is True
        and authority.get("empirical_execution_allowed") is True
        and document.get("status") in ACTIVE_CAMPAIGN_STATES
    )


def validate_campaign(root: Path = ROOT) -> tuple[dict, list[str]]:
    document = yaml.safe_load((root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    schema = json.loads((root / "schemas/local_model_campaign.schema.json").read_text(encoding="utf-8"))
    errors = [
        f"schema:{error.json_path}:{error.message}"
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: list(item.path),
        )
    ]
    authority = document.get("authority", {})
    human = authority.get("human_execution_authorization", {})
    human_record_complete = human.get("status") == "recorded" and all(
        human.get(key) for key in ("actor", "timestamp", "decision_reference")
    )
    if human.get("status") == "recorded" and not human_record_complete:
        errors.append("recorded human execution authorization is incomplete")
    if human_record_complete:
        if human.get("actor") != DEVELOPMENT_DECISION_ACTOR:
            errors.append("development authorization actor does not match EXEC-001")
        if human.get("decision_reference") != DEVELOPMENT_DECISION_REFERENCE:
            errors.append("development authorization must reference EXEC-001")
        if not authority.get("downloads_allowed"):
            errors.append("development-authorized campaign must allow downloads")
        if not authority.get("empirical_execution_allowed"):
            errors.append("development-authorized campaign must allow empirical execution")
        if document.get("status") not in ACTIVE_CAMPAIGN_STATES:
            errors.append("development-authorized campaign has wrong status")
    else:
        if authority.get("downloads_allowed"):
            errors.append("downloads_allowed requires a complete EXEC-001 human record")
        if authority.get("empirical_execution_allowed"):
            errors.append("empirical_execution_allowed requires a complete EXEC-001 human record")
        if document.get("status") in ACTIVE_CAMPAIGN_STATES:
            errors.append("campaign claims development authorization without a complete EXEC-001 human record")

    policy = yaml.safe_load((root / "config/model_candidate_policy.yml").read_text(encoding="utf-8"))
    registry = yaml.safe_load((root / "config/base_model_candidates.yml").read_text(encoding="utf-8"))
    registered = {item.get("id"): item for item in registry.get("candidates", [])}
    allowed_licenses = set(policy.get("allowed_licenses", []))
    admitted_states = set(policy.get("bakeoff_admitted_states", []))
    required_revision_length = policy.get("required_revision_length")
    if required_revision_length != 40:
        errors.append("candidate policy must require full 40-character commit revisions")
    candidates = [item.get("candidate_id") for item in document.get("execution_order", [])]
    if len(candidates) != len(set(candidates)):
        errors.append("candidate IDs must be unique")
    if candidates[:3] != ["qwen25_1_5b_instruct", "qwen3_1_7b", "smollm3_3b"]:
        errors.append("primary candidate order changed without reviewed campaign update")
    for candidate_id in candidates:
        candidate = registered.get(candidate_id)
        if not candidate:
            errors.append(f"campaign candidate is not registered: {candidate_id}")
            continue
        if candidate.get("license") not in allowed_licenses:
            errors.append(f"campaign candidate has unapproved license: {candidate_id}")
        if candidate.get("access") != "public_no_credentials":
            errors.append(f"campaign candidate requires non-public or credentialed access: {candidate_id}")
        if candidate.get("admission") not in admitted_states:
            errors.append(f"campaign candidate is not admitted to the empirical bake-off: {candidate_id}")
        revision = candidate.get("revision")
        if (
            not isinstance(required_revision_length, int)
            or not isinstance(revision, str)
            or len(revision) != required_revision_length
            or re.fullmatch(r"[0-9a-f]+", revision) is None
        ):
            errors.append(f"campaign candidate lacks an exact lowercase commit revision: {candidate_id}")
    if set(document.get("modes", [])) != {"native", "contract", "mode_c"}:
        errors.append("all three governed prompt modes are required")
    return document, errors


def main() -> int:
    document, errors = validate_campaign()
    development_authorized = not errors and development_r_and_d_authorized(document)
    payload = {
        "valid": not errors,
        "errors": errors,
        "campaign_id": document.get("campaign_id"),
        "campaign_status": document.get("status"),
        "local_setup_ready": not errors,
        "authorization_scope": "private_product_r_and_d" if development_authorized else "none",
        "development_r_and_d_authorized": development_authorized,
        "eligibility_gate": document.get("authority", {}).get("eligibility_gate"),
        "contest_path_authorized": False,
        "empirical_execution_authorized": development_authorized,
        "downloads_allowed": development_authorized,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
