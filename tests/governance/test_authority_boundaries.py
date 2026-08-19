from methodbridge.governance import requires_human_approval

def test_protected_decisions_require_human():
    assert requires_human_approval("final_model")
    assert requires_human_approval("submission_authorization")
    assert not requires_human_approval("format_markdown")
