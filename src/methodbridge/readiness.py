from pathlib import Path, PureWindowsPath
from .contracts import ReadinessResult
from .data import load_json, load_yaml


MODEL_SELECTION_STATE_ARTIFACT = "config/model_selection_state.yml"
UNRESOLVED_MODEL_ARTIFACT = "metadata.json#/_runtime/model_path"
PROFILER_ARTIFACT = "artifacts/profiler/final.json"


def _repository_relative_identifier(value: object) -> str | None:
    """Return a safe portable artifact identifier, never a local path."""
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    windows_path = PureWindowsPath(value)
    if (
        path.is_absolute()
        or windows_path.drive
        or ".." in path.parts
        or value.startswith("~")
        or "://" in value
        or "\\" in value
        or "\x00" in value
    ):
        return None
    return path.as_posix()


def evaluate_readiness(root: Path) -> ReadinessResult:
    """Evaluate final submission readiness using fail-closed evidence gates.

    Repository structure, simulation-proxy runs, a preferred documentary
    candidate, or an automated proxy score can never satisfy the protected final
    model gate. Readiness requires an attributable human-approved finalist and
    the exact evidence-bound artifact described by that decision.
    """
    blockers: list[str] = []
    evidence: dict[str, str] = {}

    metadata_path = root / "metadata.json"
    metadata = load_json(metadata_path)
    metadata_raw = metadata_path.read_text(encoding="utf-8")
    if "REQUIRES_" in metadata_raw:
        blockers.append("metadata/download placeholders remain")

    selection_path = root / MODEL_SELECTION_STATE_ARTIFACT
    if not selection_path.is_file():
        blockers.append("model selection state missing")
        selection: dict = {}
    else:
        selection = load_yaml(selection_path) or {}
        evidence["model_selection_state"] = MODEL_SELECTION_STATE_ARTIFACT

    if selection.get("status") != "human_approved_finalist":
        blockers.append("final model not human-approved")

    final_selection = selection.get("final_selection") or {}
    required_selection_fields = (
        "candidate_id",
        "source_model",
        "source_revision",
        "gguf_sha256",
        "quantization",
        "runtime_configuration",
    )
    if any(not final_selection.get(field) for field in required_selection_fields):
        blockers.append("final model evidence binding incomplete")

    approval = final_selection.get("human_approval") or {}
    if approval.get("status") != "recorded" or not all(
        approval.get(field) for field in ("actor", "timestamp", "decision_reference")
    ):
        blockers.append("final model approval record incomplete")

    model_identifier = _repository_relative_identifier(
        metadata.get("_runtime", {}).get("model_path")
    )
    evidence["model_path"] = model_identifier or UNRESOLVED_MODEL_ARTIFACT
    model_path = root / model_identifier if model_identifier else None
    if model_path is None or not model_path.is_file():
        blockers.append("final GGUF missing")

    profiler_path = root / PROFILER_ARTIFACT
    evidence["profiler_path"] = PROFILER_ARTIFACT
    if not profiler_path.is_file():
        blockers.append("official participant profiler output missing")

    eligibility_path = root / "governance/ELIGIBILITY_AND_ENTRANT_GATE.md"
    eligibility = eligibility_path.read_text(encoding="utf-8")
    if "Status:** unresolved" in eligibility or "**Status:** unresolved" in eligibility:
        blockers.append("eligibility unresolved")

    return ReadinessResult(ready=not blockers, blockers=blockers, evidence=evidence)
