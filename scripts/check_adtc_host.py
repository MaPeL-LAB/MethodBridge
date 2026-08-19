#!/usr/bin/env python3
"""Detect and classify the current host against the ADTC reference profile."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

from methodbridge.hardware import (
    REFERENCE_MATCH,
    classify_host,
    detect_host,
    load_profile,
    make_attestation,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=ROOT / "config/adtc_standard_laptop.yml",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-reference",
        action="store_true",
        help="Exit 2 unless the host exactly matches the declared reference class.",
    )
    args = parser.parse_args()

    profile = load_profile(args.profile)
    facts = detect_host()
    classification = classify_host(facts, profile)
    attestation = make_attestation(facts, classification, profile)

    schema = json.loads(
        (ROOT / "schemas/hardware_attestation.schema.json").read_text(
            encoding="utf-8"
        )
    )
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(attestation),
        key=lambda error: list(error.path),
    )
    if errors:
        print(json.dumps({"valid": False, "errors": [f"{'.'.join(map(str, error.path))}: {error.message}" for error in errors]}, indent=2))
        return 1

    if args.output:
        write_json(args.output, attestation)

    print(json.dumps(attestation, indent=2, sort_keys=True))
    if args.require_reference and classification.measurement_class != REFERENCE_MATCH:
        return 2
    return 0 if classification.measurement_class != "invalid_environment" else 1


if __name__ == "__main__":
    sys.exit(main())
