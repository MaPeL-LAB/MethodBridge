#!/usr/bin/env python3
from pathlib import Path
import argparse
from methodbridge.training.pipeline import build_fixture_dataset
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--output", default="artifacts/fixture_dataset.jsonl")
args = parser.parse_args()
count = build_fixture_dataset(ROOT, ROOT / args.output)
print(f"built {count} fixture records")
