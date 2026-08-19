#!/usr/bin/env python3
"""Validate the fail-closed model-evidence and selection boundary."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from methodbridge.inference.runner import (  # noqa: E402
    InferenceConfigurationError,
    run_simulation_proxy,
)

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
            final.get("candidate_id"),
            final.get("source_model"),
            final.get("source_revision"),
            final.get("gguf_sha256"),
            final.get("quantization"),
            final.get("evidence_references"),
            human.get("actor"),
            human.get("timestamp"),
            human.get("decision_reference"),
        )
        if not all(required_values):
            errors.append("human-approved finalist lacks required evidence or attribution")
    else:
        if any(
            final.get(field) is not None
            for field in (
                "candidate_id",
                "source_model",
                "source_revision",
                "gguf_sha256",
                "quantization",
                "runtime_configuration",
            )
        ):
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
                errors.append(f"metadata model.{field} must remain an unresolved placeholder")
        if model_path != "model/methodbridge-local-final.gguf":
            errors.append("metadata model_path must use the stable submission path")
        if (ROOT / model_path).exists():
            errors.append("final GGUF exists before an approved selection state")
    if len(metadata.get("test_prompts", [])) != 2:
        errors.append("metadata must contain exactly two public prompt candidates")

    try:
        run_simulation_proxy(
            "test prompt",
            candidate_id="test",
            mode="contract",
            explicit_acknowledgement=False,
        )
        errors.append("simulation proxy ran without explicit acknowledgement")
    except InferenceConfigurationError:
        pass

    simulated = run_simulation_proxy(
        "test prompt",
        candidate_id="test",
        mode="contract",
        explicit_acknowledgement=True,
    )
    if any(
        (
            simulated.measured,
            simulated.eligible_as_model_output_evidence,
            simulated.eligible_for_model_selection,
            simulated.eligible_for_submission_score,
        )
    ):
        errors.append("simulation result violates fail-closed classification")
    if any(
        value is not None
        for value in (
            simulated.time_to_first_token_ms,
            simulated.total_time_ms,
            simulated.throughput_tps,
            simulated.peak_rss_mb,
        )
    ):
        errors.append("simulation proxy contains fabricated performance measurements")

    authoritative_files = [
        ROOT / "BOOTSTRAP_STATUS.md",
        ROOT / "REPORT.md",
        ROOT / "MODEL_CARD.md",
    ]
    prohibited_patterns = {
        r"\b31\.2\s*tps\b": "unsupported Q4 throughput claim",
        r"\b26\.8\s*tps\b": "unsupported Q5 throughput claim",
        r"\b22\.4\s*tps\b": "unsupported Q6 throughput claim",
        r"\b99\.2%\b": "unsupported retention claim",
        r"\b0\.0?4\s+perplexity\b": "unsupported perplexity claim",
        r"\b0\.14\s+perplexity\b": "unsupported perplexity claim",
        r"\bprimary finalist\b": "premature finalist claim",
        r"\bpareto optimum\b": "unsupported Pareto claim",
    }
    combined = "\n".join(path.read_text(encoding="utf-8") for path in authoritative_files).lower()
    for pattern, description in prohibited_patterns.items():
        if re.search(pattern, combined, flags=re.IGNORECASE):
            errors.append(description)
    required_phrases = (
        "no final model",
        "simulation proxy",
        "automated_keyword_proxy_pass_rate",
    )
    for phrase in required_phrases:
        if phrase not in combined:
            errors.append(f"authoritative evidence documents are missing phrase: {phrase}")

    runner_source = (ROOT / "src/methodbridge/inference/runner.py").read_text(encoding="utf-8")
    if "CANDIDATE_MEMORY_PROFILES" in runner_source:
        errors.append("runner contains static candidate memory profiles")
    private_source = (ROOT / "scripts/run_private_challenger.py").read_text(encoding="utf-8")
    for prohibited in ("response_preview", "prompt_text_exported\": True", "response_text_exported\": True"):
        if prohibited in private_source:
            errors.append(f"private challenger exposes prohibited field: {prohibited}")

    if "REQUIRES_HUMAN_MODEL_SELECTION" not in metadata_text:
        errors.append("metadata does not preserve unresolved final-model state")

    if errors:
        print("Model evidence boundary: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Model evidence boundary: PASS")
    print(f"Selection status: {selection_status}")
    print("Simulation proxy: measured=false, selection=false, submission=false")
    print("Automated scorer: keyword proxy; semantic review required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
