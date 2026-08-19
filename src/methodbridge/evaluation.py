"""Evaluation plumbing with explicit evidence classification.

The built-in scorer is a lightweight keyword-overlap proxy for smoke testing. It
is not an accuracy benchmark and cannot select a model without qualified semantic
adjudication.
"""
from __future__ import annotations

from collections.abc import Callable
import hashlib
from pathlib import Path
import re
from typing import Any

from .data import load_json
from .inference.runner import InferenceResult

InferenceExecutor = Callable[[str, str, str], InferenceResult]


def load_cases(root: Path) -> list[dict]:
    return [load_json(path) for path in sorted((root / "evaluations/cases").glob("MB-*.json"))]


def structural_check(case: dict) -> list[str]:
    errors: list[str] = []
    for key in (
        "case_id",
        "family",
        "prompt",
        "expected_key_points",
        "prohibited_errors",
        "bootstrap_executable",
    ):
        if key not in case:
            errors.append(f"missing:{key}")
    if not case.get("prompt", "").strip():
        errors.append("empty_prompt")
    if not case.get("expected_key_points"):
        errors.append("missing_expected_key_points")
    return errors


def evaluate_case_response(case: dict, response_text: str) -> dict[str, Any]:
    """Apply the non-authoritative automated keyword proxy.

    The result is useful for plumbing and coarse regression detection only. It
    must not be labelled accuracy, reasoning retention, or expert adjudication.
    """
    response_lower = response_text.lower()
    covered: list[str] = []
    missed: list[str] = []
    for point in case.get("expected_key_points", []):
        words = [word for word in re.findall(r"\w+", point.lower()) if len(word) > 3]
        if any(word in response_lower for word in words):
            covered.append(point)
        else:
            missed.append(point)

    prohibited: list[str] = []
    for error in case.get("prohibited_errors", []):
        words = [word for word in re.findall(r"\w+", error.lower()) if len(word) > 3]
        if words and all(word in response_lower for word in words[:2]):
            prohibited.append(error)

    threshold = max(1, len(case.get("expected_key_points", [])) // 2)
    proxy_pass = len(covered) >= threshold and not prohibited
    return {
        "case_id": case["case_id"],
        "family": case.get("family", "unknown"),
        "automated_proxy": "keyword_overlap_v1",
        "proxy_points_covered": covered,
        "proxy_points_missed": missed,
        "proxy_prohibited_errors_triggered": prohibited,
        "proxy_pass": proxy_pass,
        "semantic_review_required": True,
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_benchmark_evaluation(
    root: Path,
    *,
    candidate_id: str,
    mode: str,
    executor: InferenceExecutor,
) -> dict[str, Any]:
    """Run the public benchmark through an injected, provenance-aware executor."""
    if executor is None:
        raise ValueError("an explicit inference executor is required")

    cases = load_cases(root)
    case_results: list[dict[str, Any]] = []
    inference_results: list[InferenceResult] = []
    for case in cases:
        inference = executor(case["prompt"], candidate_id, mode)
        inference_results.append(inference)
        proxy = evaluate_case_response(case, inference.response)
        case_results.append(
            {
                **proxy,
                "output_sha256": inference.response_sha256,
                "executor_kind": inference.executor_kind,
                "evidence_class": inference.evidence_class,
                "model_output_measured": inference.measured,
            }
        )

    proxy_passed = sum(1 for result in case_results if result["proxy_pass"])
    evidence_classes = sorted({result.evidence_class for result in inference_results})
    executor_kinds = sorted({result.executor_kind for result in inference_results})
    measured_outputs = bool(inference_results) and all(result.measured for result in inference_results)
    output_evidence_eligible = bool(inference_results) and all(
        result.eligible_as_model_output_evidence for result in inference_results
    )
    total_wall_time_ms = sum(
        result.total_time_ms for result in inference_results if result.total_time_ms is not None
    )

    return {
        "candidate_id": candidate_id,
        "mode": mode,
        "total_cases": len(cases),
        "automated_proxy": "keyword_overlap_v1",
        "automated_keyword_proxy_passed_cases": proxy_passed,
        "automated_keyword_proxy_pass_rate": (
            round(proxy_passed / len(cases), 4) if cases else 0.0
        ),
        "semantic_review_status": "required",
        "eligible_for_automatic_model_selection": False,
        "eligible_for_model_selection": False,
        "eligible_for_submission_score": False,
        "measured_model_outputs": measured_outputs,
        "eligible_as_model_output_evidence": output_evidence_eligible,
        "evidence_classes": evidence_classes,
        "executor_kinds": executor_kinds,
        "development_wall_time_sec": (
            round(total_wall_time_ms / 1000.0, 3) if measured_outputs else None
        ),
        "performance_metrics_valid": False,
        "performance_metrics_note": (
            "Use the pinned official ADTC profiler on an eligible reference host for "
            "scoreable throughput, memory, TTFT, and thermal evidence."
        ),
        "result_set_sha256": _sha256_text(
            "\n".join(
                f"{result['case_id']}:{result['output_sha256']}:{result['proxy_pass']}"
                for result in case_results
            )
        ),
        "case_results": case_results,
    }
