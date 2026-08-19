#!/usr/bin/env python3
from pathlib import Path
import json
from methodbridge.data import normalize_text
ROOT = Path(__file__).resolve().parents[1]
train = []
for path in sorted((ROOT / "data/fixtures").glob("train_*.json")):
    train.append(normalize_text(json.loads(path.read_text(encoding="utf-8"))["prompt"]))
eval_prompts = []
for path in sorted((ROOT / "evaluations/cases").glob("MB-*.json")):
    eval_prompts.append(normalize_text(json.loads(path.read_text(encoding="utf-8"))["prompt"]))
metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
public = [normalize_text(p["prompt"]) for p in metadata.get("test_prompts", [])]
leaks = sorted(set(train) & (set(eval_prompts) | set(public)))
print(json.dumps({"leakage_detected": bool(leaks), "leaks": leaks}, indent=2))
raise SystemExit(1 if leaks else 0)
