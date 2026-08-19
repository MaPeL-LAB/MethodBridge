#!/usr/bin/env python3
"""Validate a candidate ADTC reference-run evidence record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

from methodbridge.hardware import load_profile, validate_reference_run

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument(
        "--profile",
        type=Path,
        default=ROOT / "config/adtc_standard_laptop.yml",
    )
    args = parser.parse_args()

    record = json.loads(args.record.read_text(encoding="utf-8"))
    profile = load_profile(args.profile)
    schema = json.loads(
        (ROOT / "schemas/adtc_reference_run.schema.json").read_text(encoding="utf-8")
    )
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record),
        key=lambda error: list(error.path),
    )
    result = validate_reference_run(record, profile)
    blockers = [
        f"schema:{'.'.join(map(str, error.path))}:{error.message}"
        for error in schema_errors
    ]
    blockers.extend(result.blockers)
    blockers = list(dict.fromkeys(blockers))
    output = {
        "accepted": not blockers,
        "eligible_for_submission_score": not blockers,
        "blockers": blockers,
        "warnings": list(result.warnings),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not blockers else 1


if __name__ == "__main__":
    sys.exit(main())
