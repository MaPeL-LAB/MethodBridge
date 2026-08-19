#!/usr/bin/env python3
from pathlib import Path
import argparse, json
from methodbridge.evaluation import load_cases, structural_check
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args=parser.parse_args()
cases=load_cases(ROOT)
errors={c["case_id"]: structural_check(c) for c in cases if structural_check(c)}
executable=sum(1 for c in cases if c.get("bootstrap_executable"))
result={"mode":"dry-run" if args.dry_run else "model-required","case_count":len(cases),"bootstrap_executable_count":executable,"structural_errors":errors,"model_results":None}
print(json.dumps(result, indent=2))
if not args.dry_run:
    raise SystemExit(2)
raise SystemExit(1 if errors else 0)
