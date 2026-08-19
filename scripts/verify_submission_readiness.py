#!/usr/bin/env python3
from pathlib import Path
import json
from methodbridge.readiness import evaluate_readiness
ROOT=Path(__file__).resolve().parents[1]
result=evaluate_readiness(ROOT)
print(json.dumps({"ready":result.ready,"blockers":result.blockers,"evidence":result.evidence}, indent=2))
raise SystemExit(0 if result.ready else 2)
