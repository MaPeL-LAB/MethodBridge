from __future__ import annotations

import json

import yaml


def test_model_selection_remains_unresolved(repo_root):
    state = yaml.safe_load((repo_root / "config/model_selection_state.yml").read_text())
    metadata = json.loads((repo_root / "metadata.json").read_text())
    assert state["status"] == "no_empirical_selection"
    assert state["final_selection"]["candidate_id"] is None
    assert state["final_selection"]["human_approval"]["status"] == "not_recorded"
    assert metadata["model"]["name"].startswith("REQUIRES_")
    assert metadata["model"]["quantization"].startswith("REQUIRES_")
    assert metadata["_runtime"]["model_path"] == "model/methodbridge-local-final.gguf"
    assert not (repo_root / metadata["_runtime"]["model_path"]).exists()


def test_authoritative_documents_withdraw_unsupported_claims(repo_root):
    text = "\n".join(
        (repo_root / path).read_text().lower()
        for path in ("BOOTSTRAP_STATUS.md", "REPORT.md", "MODEL_CARD.md")
    )
    assert "no final model" in text
    assert "simulation proxy" in text
    assert "automated_keyword_proxy_pass_rate" in text
    for prohibited in (
        "31.2 tps",
        "26.8 tps",
        "22.4 tps",
        "99.2%",
        "primary finalist",
        "pareto optimum",
    ):
        assert prohibited not in text


def test_private_challenger_shareable_output_omits_text(repo_root):
    source = (repo_root / "scripts/run_private_challenger.py").read_text()
    assert "response_preview" not in source
    assert '"prompt_text_exported": False' in source
    assert '"response_text_exported": False' in source
    assert '"rubric_text_exported": False' in source
