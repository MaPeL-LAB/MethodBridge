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
    assert result.evidence["model_selection_state"].endswith(
        "config/model_selection_state.yml"
    )
