def test_toc_is_not_falsely_approved(repo_root):
    text=(repo_root/"governance/PROJECT_THEORY_OF_CHANGE.md").read_text()
    assert "human approval not recorded" in text.lower()
