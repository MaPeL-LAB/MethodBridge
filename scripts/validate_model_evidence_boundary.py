#!/usr/bin/env python3
"""Validate the fail-closed model-evidence, campaign, claims, and release boundary."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from methodbridge.inference.runner import InferenceConfigurationError, run_simulation_proxy  # noqa: E402
from validate_local_model_campaign import validate_campaign  # noqa: E402
from validate_public_claims import validate as validate_public_claims  # noqa: E402

ALLOWED_SELECTION_STATES = {
    "no_empirical_selection",
    "empirical_comparison_in_progress",
    "preferred_with_conditions",
    "finalist_pending_human_approval",
    "human_approved_finalist",
}


def main() -> int:
    errors: list[str] = []
    policy = yaml.safe_load((ROOT / "config/model_evidence_policy.yml").read_text(encoding="utf-8"))
    state = yaml.safe_load((ROOT / "config/model_selection_state.yml").read_text(encoding="utf-8"))
    release = yaml.safe_load((ROOT / "config/release_authorization.yml").read_text(encoding="utf-8"))
    metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))

    required_classes = {"simulation_proxy", "local_real_model_output", "official_reference_profile"}
    present_classes = set(policy.get("evidence_classes", {}))
    if not required_classes.issubset(present_classes):
        errors.append("model evidence policy is missing required evidence classes")

    simulation_policy = policy.get("evidence_classes", {}).get("simulation_proxy", {})
    for field in (
        "model_executed",
        "measured",
        "eligible_as_model_output_evidence",
        "eligible_for_model_selection",
        "eligible_for_submission_score",
    ):
        if simulation_policy.get(field) is not False:
            errors.append(f"simulation_proxy.{field} must be false")

    selection_status = state.get("status")
    if selection_status not in ALLOWED_SELECTION_STATES:
        errors.append(f"unsupported model selection state: {selection_status}")
    final = state.get("final_selection", {})
    human = final.get("human_approval", {})
    if selection_status == "human_approved_finalist":
        required_values = (
            final.get("candidate_id"), final.get("source_model"),
            final.get("source_revision"), final.get("gguf_sha256"),
            final.get("quantization"), final.get("evidence_references"),
            human.get("actor"), human.get("timestamp"), human.get("decision_reference"),
        )
        if not all(required_values):
            errors.append("human-approved finalist lacks required evidence or attribution")
    else:
        if any(final.get(field) is not None for field in (
            "candidate_id", "source_model", "source_revision", "gguf_sha256",
            "quantization", "runtime_configuration",
        )):
            errors.append("non-final selection state contains final model fields")
        if final.get("evidence_references"):
            errors.append("non-final selection state contains final evidence references")
        if human.get("status") != "not_recorded":
            errors.append("non-final selection state claims human model approval")

    metadata_text = (ROOT / "metadata.json").read_text(encoding="utf-8")
    model = metadata.get("model", {})
    model_path = metadata.get("_runtime", {}).get("model_path", "")
    if selection_status != "human_approved_finalist":
        for field in ("name", "quantization", "parameters_estimate"):
            if not str(model.get(field, "")).startswith("REQUIRES_"):
                errors.append(f"metadata model.{field} must remain unresolved")
        if model_path != "model/methodbridge-local-final.gguf":
            errors.append("metadata model_path must use stable submission path")
        if (ROOT / model_path).exists():
            errors.append("final GGUF exists before an approved selection state")
    if len(metadata.get("test_prompts", [])) != 2:
        errors.append("metadata must contain exactly two public prompt candidates")

    try:
        run_simulation_proxy("test prompt", candidate_id="test", mode="contract", explicit_acknowledgement=False)
        errors.append("simulation proxy ran without explicit acknowledgement")
    except InferenceConfigurationError:
        pass
    simulated = run_simulation_proxy("test prompt", candidate_id="test", mode="contract", explicit_acknowledgement=True)
    if any((simulated.measured, simulated.eligible_as_model_output_evidence, simulated.eligible_for_model_selection, simulated.eligible_for_submission_score)):
        errors.append("simulation result violates fail-closed classification")
    if any(value is not None for value in (simulated.time_to_first_token_ms, simulated.total_time_ms, simulated.throughput_tps, simulated.peak_rss_mb)):
        errors.append("simulation proxy contains fabricated performance measurements")

    _, campaign_errors = validate_campaign(ROOT)
    errors.extend(f"campaign:{error}" for error in campaign_errors)
    errors.extend(f"public_claims:{error}" for error in validate_public_claims(ROOT))

    release_schema = json.loads((ROOT / "schemas/release_authorization.schema.json").read_text(encoding="utf-8"))
    for error in Draft202012Validator(release_schema).iter_errors(release):
        errors.append(f"release_schema:{error.json_path}:{error.message}")
    if release.get("status") == "human_approved_release":
        if selection_status != "human_approved_finalist":
            errors.append("release approved without a human-approved finalist")
    else:
        if release.get("human_authorization", {}).get("status") != "not_recorded":
            errors.append("blocked release contains human authorization")
        if any(value for value in release.get("required_evidence", {}).values()):
            errors.append("blocked release contains final evidence references")

    runner_source = (ROOT / "src/methodbridge/inference/runner.py").read_text(encoding="utf-8")
    if "CANDIDATE_MEMORY_PROFILES" in runner_source:
        errors.append("runner contains static candidate memory profiles")
    private_source = (ROOT / "scripts/run_private_challenger.py").read_text(encoding="utf-8")
    for prohibited in ("response_preview", 'prompt_text_exported": True', 'response_text_exported": True'):
        if prohibited in private_source:
            errors.append(f"private challenger exposes prohibited field: {prohibited}")

    release_source = (ROOT / "scripts/prepare_model_release.py").read_text(encoding="utf-8")
    for required in (
        "human_approved_release", "human_approved_finalist",
        "release_authorization.yml", "GGUF SHA-256 does not match release authorization",
    ):
        if required not in release_source:
            errors.append(f"release tool missing fail-closed marker: {required}")
    if "Q5_K_M (5-bit medium quantization with optimal" in release_source:
        errors.append("release tool hard-codes an unsupported quantization conclusion")
    if "REQUIRES_HUMAN_MODEL_SELECTION" not in metadata_text:
        errors.append("metadata does not preserve unresolved final-model state")

    if errors:
        print("Model evidence boundary: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Model evidence boundary: PASS")
    print(f"Selection status: {selection_status}")
    print("Campaign: prepared, empirical execution not authorized")
    print("Release: blocked, human authorization not recorded")
    print("Simulation proxy: measured=false, selection=false, submission=false")
    print("Automated scorer: keyword proxy; semantic review required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
