#!/usr/bin/env python3
import argparse, json
parser=argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
args=parser.parse_args()
if not args.dry_run:
    raise SystemExit("merge an approved adapter requires an explicitly approved empirical phase; use --dry-run to inspect the contract.")
print(json.dumps({"action":"merge an approved adapter","mode":"dry-run","executed":False,"status":"requires_empirical_phase"}, indent=2))
