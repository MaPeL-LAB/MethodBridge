from pathlib import Path
from .contracts import ReadinessResult
from .data import load_json


def evaluate_readiness(root: Path) -> ReadinessResult:
    blockers: list[str] = []
    metadata = load_json(root / "metadata.json")
    raw = (root / "metadata.json").read_text(encoding="utf-8")
    if "REQUIRES_" in raw:
        blockers.append("metadata/download placeholders remain")
    model_path = root / metadata.get("_runtime", {}).get("model_path", "")
    if not model_path.is_file():
        blockers.append("final GGUF missing")
    if not (root / "artifacts/profiler/final.json").is_file():
        blockers.append("official participant profiler output missing")
    eligibility = (root / "governance/ELIGIBILITY_AND_ENTRANT_GATE.md").read_text(encoding="utf-8")
    if "Status:** unresolved" in eligibility or "**Status:** unresolved" in eligibility:
        blockers.append("eligibility unresolved")
    return ReadinessResult(ready=not blockers, blockers=blockers, evidence={"model_path": str(model_path)})
