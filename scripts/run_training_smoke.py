#!/usr/bin/env python3
import argparse, json
parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
if not args.dry_run:
    raise SystemExit("Training is not authorized in the recovered bootstrap; use --dry-run.")
print(json.dumps({"mode":"dry-run","status":"pipeline_contract_validated","model_downloaded":False,"training_run":False}, indent=2))
