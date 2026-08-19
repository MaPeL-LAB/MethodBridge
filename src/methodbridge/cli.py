import argparse
import json
from pathlib import Path
from .evaluation import load_cases
from .readiness import evaluate_readiness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["case-count", "readiness"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command == "case-count":
        print(len(load_cases(root)))
        return 0
    result = evaluate_readiness(root)
    print(json.dumps({"ready": result.ready, "blockers": result.blockers, "evidence": result.evidence}, indent=2))
    return 0 if result.ready else 2

if __name__ == "__main__":
    raise SystemExit(main())
