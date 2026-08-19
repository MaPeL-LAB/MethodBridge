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
]
errors = [f"missing:{p}" for p in required if not (ROOT / p).exists()]
case_files = sorted((ROOT / "evaluations/cases").glob("MB-*.json"))
adr_files = sorted((ROOT / "docs/adr").glob("ADR-*.md"))
if len(case_files) != 60:
    errors.append(f"evaluation_count:{len(case_files)}")
if len(adr_files) != 18:
    errors.append(f"adr_count:{len(adr_files)}")
if list(ROOT.rglob("*.gguf")):
    errors.append("gguf_committed")
try:
    json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    yaml.safe_load((ROOT / "data/source_registry.yml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/evaluation_case.schema.json").read_text(encoding="utf-8"))
    for path in case_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: e.path)
        if schema_errors:
            errors.append(f"schema:{path.name}:{schema_errors[0].message}")
except Exception as exc:
    errors.append(f"parse:{type(exc).__name__}:{exc}")
print(json.dumps({"valid": not errors, "errors": errors, "evaluation_count": len(case_files), "adr_count": len(adr_files)}, indent=2))
raise SystemExit(0 if not errors else 1)
