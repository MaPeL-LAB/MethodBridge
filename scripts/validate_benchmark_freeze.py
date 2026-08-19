#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator, FormatChecker

def canonical_hash(case: dict) -> str:
    raw=json.dumps(case,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def normalize(text: str) -> str:
    return " ".join(text.lower().split())

def validate(root: Path) -> list[str]:
    errors=[]
    schema=json.loads((root/"schemas/evaluation_case.schema.json").read_text())
    validator=Draft202012Validator(schema,format_checker=FormatChecker())
    cases=[]
    for path in sorted((root/"evaluations/cases").glob("MB-*.json")):
        case=json.loads(path.read_text()); cases.append(case)
        for err in validator.iter_errors(case): errors.append(f"{path}:{err.json_path}:{err.message}")
    if len(cases)!=60: errors.append(f"expected 60 cases, found {len(cases)}")
    if sum(bool(c.get("bootstrap_executable")) for c in cases)!=40: errors.append("expected exactly 40 bootstrap-executable cases")
    ids=[c.get("case_id") for c in cases]
    if len(ids)!=len(set(ids)): errors.append("duplicate case IDs")
    prompts=[normalize(c.get("prompt", "")) for c in cases]
    if len(prompts)!=len(set(prompts)): errors.append("duplicate normalized prompts")
    freeze=json.loads((root/"evaluations/BENCHMARK_FREEZE.json").read_text())
    current={c["case_id"]:canonical_hash(c) for c in cases}
    recorded={r["case_id"]:r["sha256"] for r in freeze["case_hashes"]}
    if current!=recorded: errors.append("case hashes differ from freeze record")
    aggregate="".join(f"{cid}:{current[cid]}\n" for cid in sorted(current)).encode("utf-8")
    if hashlib.sha256(aggregate).hexdigest()!=freeze.get("benchmark_sha256"): errors.append("aggregate benchmark hash mismatch")
    manifest=yaml.safe_load((root/"evaluations/benchmark_manifest.yml").read_text())
    if manifest.get("benchmark_sha256")!=freeze.get("benchmark_sha256"): errors.append("manifest and freeze hashes differ")
    if manifest.get("visibility")!="public": errors.append("tracked benchmark must be marked public")
    if manifest.get("training_excluded") is not True: errors.append("tracked benchmark must remain training-excluded")
    reviews=yaml.safe_load((root/"evaluations/review_status.yml").read_text())
    if set(reviews.get("case_ids", [])) != set(ids): errors.append("review status does not cover all cases")
    if reviews.get("default_case_status") != "approved_with_conditions": errors.append("review status is not approved with conditions")
    for family, rubric in reviews.get("rubric_by_family", {}).items():
        if not (root / rubric).is_file(): errors.append(f"missing rubric for family {family}: {rubric}")
    for path in (root/"data/fixtures").glob("train_*.json"):
        if normalize(json.loads(path.read_text()).get("prompt", "")) in prompts: errors.append(f"public benchmark prompt appears in training fixture: {path}")
    forbidden=[p for p in (root/"evaluations/private_holdout").iterdir() if p.name not in {"README.md", ".gitignore"}]
    if forbidden: errors.append("private holdout content must not be committed")
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]); args=parser.parse_args()
    errors=validate(args.root)
    if errors:
        print("Benchmark freeze validation: FAIL"); [print(f"- {e}") for e in errors]; return 1
    freeze=json.loads((args.root/"evaluations/BENCHMARK_FREEZE.json").read_text())
    print("Benchmark freeze validation: PASS"); print(f"Benchmark: {freeze['freeze_id']}"); print(f"Cases: {freeze['case_count']}"); print(f"SHA-256: {freeze['benchmark_sha256']}"); return 0
if __name__=="__main__": sys.exit(main())
