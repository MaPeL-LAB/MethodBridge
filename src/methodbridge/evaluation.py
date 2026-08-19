from pathlib import Path
from .data import load_json


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
