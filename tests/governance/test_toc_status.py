def test_toc_approval_is_attributable_and_bounded(repo_root):
    toc = (repo_root / "governance/PROJECT_THEORY_OF_CHANGE.md").read_text()
    decision_log = (repo_root / "governance/DECISION_LOG.md").read_text()
    boundaries = (repo_root / "governance/APPROVAL_BOUNDARIES.md").read_text()
    status = (repo_root / "BOOTSTRAP_STATUS.md").read_text()

    toc_lower = toc.lower()
    log_lower = decision_log.lower()
    boundaries_lower = boundaries.lower()
    status_lower = status.lower()

    assert "approved with conditions for adtc 2026 governed development" in toc_lower
    assert "marothi peter letsoalo" in toc_lower
    assert "2026-08-19t06:46:08+02:00" in toc_lower
    assert "approval reference:** gov-001 / github issue #4" in toc_lower

    assert "`approved_with_conditions`" in decision_log
    assert "entrant eligibility remains a separate unresolved hard gate" in toc_lower
    assert "held-out evaluation boundary must be preserved" in toc_lower
    assert "does not authorize production or institutional use" in toc_lower
    assert "final model release" in toc_lower
    assert "acceptance of the challenge participation agreement" in toc_lower
    assert "submission to devpost" in toc_lower

    assert "no ci result" in boundaries_lower
    assert "can substitute for an attributable human decision" in boundaries_lower
    assert "theory of change approved with conditions" in status_lower
    assert "submission status: blocked by design" in status_lower
    assert "human approval not recorded" not in toc_lower
    assert "human approval not recorded" not in log_lower
