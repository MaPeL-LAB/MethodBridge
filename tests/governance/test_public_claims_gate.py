import importlib.util
from pathlib import Path


def _load(repo_root: Path):
    path = repo_root / "scripts/validate_public_claims.py"
    spec = importlib.util.spec_from_file_location("validate_public_claims", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_public_claim_surfaces_are_fail_closed(repo_root):
    module = _load(repo_root)
    assert module.validate(repo_root) == []


def test_historical_unsupported_claim_pattern_is_rejected(repo_root, tmp_path):
    module = _load(repo_root)
    for relative in module.PUBLIC_FILES:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Submission ready: No. No final model. Simulation proxy.\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "Submission ready: No. No final model. Simulation proxy. Qwen3-1.7B winner at 26.8 TPS.\n",
        encoding="utf-8",
    )
    (tmp_path / "metadata.json").write_text(
        '{"model":{"quantization":"REQUIRES_EMPIRICAL_SELECTION"}}\n',
        encoding="utf-8",
    )
    errors = module.validate(tmp_path)
    assert "unsupported throughput" in errors
    assert "premature winner claim" in errors
