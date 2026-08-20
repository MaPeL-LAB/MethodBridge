import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from methodbridge.readiness import evaluate_readiness


def test_bootstrap_is_blocked(repo_root):
    result = evaluate_readiness(repo_root)
    assert not result.ready
    assert "final model not human-approved" in result.blockers
    assert "final model evidence binding incomplete" in result.blockers
    assert "final model approval record incomplete" in result.blockers
    assert "final GGUF missing" in result.blockers
    assert "official participant profiler output missing" in result.blockers
    assert "eligibility unresolved" in result.blockers


def test_simulation_or_documentary_hypothesis_cannot_unlock_readiness(repo_root):
    result = evaluate_readiness(repo_root)
    assert result.ready is False
    assert result.evidence["model_selection_state"] == "config/model_selection_state.yml"


def test_readiness_evidence_identifiers_are_portable_and_useful(repo_root):
    result = evaluate_readiness(repo_root)

    assert result.evidence == {
        "model_selection_state": "config/model_selection_state.yml",
        "model_path": "model/methodbridge-local-final.gguf",
        "profiler_path": "artifacts/profiler/final.json",
    }
    assert all(
        not Path(identifier).is_absolute() for identifier in result.evidence.values()
    )


def test_submission_readiness_json_does_not_disclose_local_paths(repo_root):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(repo_root / "src")
    proc = subprocess.run(
        [sys.executable, "scripts/verify_submission_readiness.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )

    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["ready"] is False
    assert payload["evidence"] == {
        "model_selection_state": "config/model_selection_state.yml",
        "model_path": "model/methodbridge-local-final.gguf",
        "profiler_path": "artifacts/profiler/final.json",
    }
    assert str(repo_root) not in proc.stdout
    assert str(Path.home()) not in proc.stdout


def test_unsafe_model_paths_fail_closed_without_disclosure(repo_root, tmp_path):
    checkout = tmp_path / "checkout"
    (checkout / "config").mkdir(parents=True)
    (checkout / "governance").mkdir()
    shutil.copy2(repo_root / "metadata.json", checkout / "metadata.json")
    shutil.copy2(
        repo_root / "config/model_selection_state.yml",
        checkout / "config/model_selection_state.yml",
    )
    shutil.copy2(
        repo_root / "governance/ELIGIBILITY_AND_ENTRANT_GATE.md",
        checkout / "governance/ELIGIBILITY_AND_ENTRANT_GATE.md",
    )
    outside_artifact = tmp_path / "outside-model.bin"
    outside_artifact.write_bytes(b"not a model")
    unsafe_values = (
        str(outside_artifact.resolve()),
        "../outside-model.bin",
        r"C:\Users\private\outside-model.bin",
        r"\\private-server\share\outside-model.bin",
    )
    for unsafe_value in unsafe_values:
        metadata = json.loads(
            (checkout / "metadata.json").read_text(encoding="utf-8")
        )
        metadata["_runtime"]["model_path"] = unsafe_value
        (checkout / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )

        result = evaluate_readiness(checkout)
        serialized = json.dumps(result.evidence)

        assert "final GGUF missing" in result.blockers
        assert result.evidence["model_path"] == "metadata.json#/_runtime/model_path"
        assert unsafe_value not in serialized
        assert str(tmp_path) not in serialized
