import importlib.util
from pathlib import Path


def _load(repo_root: Path):
    path = repo_root / "scripts/prepare_model_release.py"
    spec = importlib.util.spec_from_file_location("prepare_model_release", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_release_gate_is_blocked_by_default(repo_root):
    module = _load(repo_root)
    release, state, errors = module.load_gate(repo_root)
    assert release["status"] == "blocked"
    assert state["status"] == "no_empirical_selection"
    assert errors
    assert any("human-approved finalist" in error for error in errors)
    assert any("release authorization remains blocked" in error for error in errors)
