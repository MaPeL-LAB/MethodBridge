from methodbridge.readiness import evaluate_readiness

def test_bootstrap_is_blocked(repo_root):
    result=evaluate_readiness(repo_root)
    assert not result.ready
    assert "final GGUF missing" in result.blockers
    assert "eligibility unresolved" in result.blockers
