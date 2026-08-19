from pathlib import Path
import re
from typing import Any, Mapping
from .data import load_json
from .inference.runner import run_candidate_inference


def load_cases(root: Path) -> list[dict]:
    return [load_json(p) for p in sorted((root / "evaluations/cases").glob("MB-*.json"))]


def structural_check(case: dict) -> list[str]:
    errors = []
    for key in ["case_id", "family", "prompt", "expected_key_points", "prohibited_errors", "bootstrap_executable"]:
        if key not in case:
            errors.append(f"missing:{key}")
    if not case.get("prompt", "").strip():
        errors.append("empty_prompt")
    if not case.get("expected_key_points"):
        errors.append("missing_expected_key_points")
    return errors


def evaluate_case_response(case: dict, response_text: str) -> dict[str, Any]:
    """Score a model response against an evaluation case specification."""
    resp_lower = response_text.lower()
    
    # Check expected key points
    points_covered = []
    points_missed = []
    for point in case.get("expected_key_points", []):
        # Extract keywords from the key point specification
        words = [w for w in re.findall(r"\w+", point.lower()) if len(w) > 3]
        if any(w in resp_lower for w in words):
            points_covered.append(point)
        else:
            points_missed.append(point)
            
    # Check prohibited errors
    prohibited_triggered = []
    for error in case.get("prohibited_errors", []):
        words = [w for w in re.findall(r"\w+", error.lower()) if len(w) > 3]
        if words and all(w in resp_lower for w in words[:2]):
            prohibited_triggered.append(error)
            
    passed = len(points_covered) >= max(1, len(case.get("expected_key_points", [])) // 2) and not prohibited_triggered
    
    return {
        "case_id": case["case_id"],
        "family": case.get("family", "unknown"),
        "points_covered": points_covered,
        "points_missed": points_missed,
        "prohibited_errors_triggered": prohibited_triggered,
        "passed": passed,
    }


def run_benchmark_evaluation(
    root: Path,
    candidate_id: str = "qwen25_1_5b_instruct",
    mode: str = "native",
) -> dict[str, Any]:
    """Run full evaluation suite for a candidate in native or contract mode."""
    cases = load_cases(root)
    case_results = []
    total_tokens_prompt = 0
    total_tokens_gen = 0
    total_time_ms = 0.0
    
    for case in cases:
        inf = run_candidate_inference(case["prompt"], candidate_id=candidate_id, mode=mode)
        eval_res = evaluate_case_response(case, inf.response)
        eval_res["response_preview"] = inf.response[:120] + "..." if len(inf.response) > 120 else inf.response
        case_results.append(eval_res)
        total_tokens_prompt += inf.tokens_prompt
        total_tokens_gen += inf.tokens_generated
        total_time_ms += inf.total_time_ms

    passed_count = sum(1 for r in case_results if r["passed"])
    return {
        "candidate_id": candidate_id,
        "mode": mode,
        "total_cases": len(cases),
        "passed_cases": passed_count,
        "pass_rate": round(passed_count / len(cases), 4) if cases else 0.0,
        "avg_tokens_prompt": round(total_tokens_prompt / max(1, len(cases)), 1),
        "avg_tokens_gen": round(total_tokens_gen / max(1, len(cases)), 1),
        "total_time_sec": round(total_time_ms / 1000.0, 3),
        "case_results": case_results,
    }
