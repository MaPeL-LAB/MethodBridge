#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
required = [
    "README.md", "AGENTS.md", "GOVERNANCE.md", "BOOTSTRAP_STATUS.md",
    "metadata.json", "download_model.sh", "REPORT.md", "data/source_registry.yml",
    "evaluations/benchmark_manifest.yml", "governance/PROJECT_THEORY_OF_CHANGE.md",
    "config/adtc_standard_laptop.yml",
    "schemas/hardware_attestation.schema.json",
    "schemas/adtc_reference_run.schema.json",
    "src/methodbridge/hardware.py",
    "scripts/check_adtc_host.py",
    "scripts/verify_adtc_reference_run.py",
    "scripts/run_adtc_simulated_profile.sh",
    "scripts/run_adtc_reference_profile.sh",
    "docs/ADTC_HARDWARE_VALIDATION_PROTOCOL.md",
    "docs/ADTC_SIMULATION_LIMITATIONS.md",
    "docs/REFERENCE_LAPTOP_SETUP.md",
]
errors = [f"missing:{p}" for p in required if not (ROOT / p).exists()]
case_files = sorted((ROOT / "evaluations/cases").glob("MB-*.json"))
adr_files = sorted((ROOT / "docs/adr").glob("ADR-*.md"))
if len(case_files) != 60:
    errors.append(f"evaluation_count:{len(case_files)}")
if len(adr_files) != 19:
    errors.append(f"adr_count:{len(adr_files)}")
if list(ROOT.rglob("*.gguf")):
    errors.append("gguf_committed")
try:
    json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "data/source_registry.yml").read_text(encoding="utf-8"))
    profile = yaml.safe_load(
        (ROOT / "config/adtc_standard_laptop.yml").read_text(encoding="utf-8")
    )
    if profile.get("profile_id") != "adtc-standard-laptop-2026":
        errors.append("hardware_profile_id")
    if profile.get("memory", {}).get("official_peak_rss_limit_gib") != 7.0:
        errors.append("hardware_peak_rss_limit")
    if profile.get("thermal", {}).get("official_limit_celsius") != 85.0:
        errors.append("hardware_thermal_limit")
    for schema_name in (
        "evaluation_case.schema.json",
        "hardware_attestation.schema.json",
        "adtc_reference_run.schema.json",
    ):
        schema = json.loads(
            (ROOT / "schemas" / schema_name).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
    schema = json.loads(
        (ROOT / "schemas/evaluation_case.schema.json").read_text(encoding="utf-8")
    )
    for path in case_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = sorted(
            Draft202012Validator(schema).iter_errors(doc), key=lambda e: e.path
        )
        if schema_errors:
            errors.append(f"schema:{path.name}:{schema_errors[0].message}")
except Exception as exc:
    errors.append(f"parse:{type(exc).__name__}:{exc}")
print(
    json.dumps(
        {
            "valid": not errors,
            "errors": errors,
            "evaluation_count": len(case_files),
            "adr_count": len(adr_files),
            "hardware_contract": "present" if not any(
                error.startswith("hardware_") or error.startswith("missing:config/adtc")
                for error in errors
            ) else "invalid",
        },
        indent=2,
    )
)
raise SystemExit(0 if not errors else 1)
