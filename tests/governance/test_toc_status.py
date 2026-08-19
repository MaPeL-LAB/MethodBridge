def test_toc_approval_is_attributable_and_bounded(repo_root):
    toc = (repo_root / "governance/PROJECT_THEORY_OF_CHANGE.md").read_text()
    decision_log = (repo_root / "governance/DECISION_LOG.md").read_text()
    boundaries = (repo_root / "governance/APPROVAL_BOUNDARIES.md").read_text()
    status = (repo_root / "BOOTSTRAP_STATUS.md").read_text()

    toc_lower = toc.lower()
    normalized_toc = " ".join(toc_lower.split())
    log_lower = decision_log.lower()
    boundaries_lower = boundaries.lower()
    status_lower = status.lower()

    assert "approved with conditions for adtc 2026 governed development" in normalized_toc
    assert "marothi peter letsoalo" in normalized_toc
    assert "2026-08-19t06:46:08+02:00" in normalized_toc
    assert "approval reference:** gov-001 / github issue #4" in normalized_toc

    assert "`approved_with_conditions`" in decision_log
    assert "entrant eligibility remains a separate unresolved hard gate" in normalized_toc
    assert "held-out evaluation boundary must be preserved" in normalized_toc
    assert "does not authorize production or institutional use" in normalized_toc
    assert "final model release" in normalized_toc
    assert "acceptance of the challenge participation agreement" in normalized_toc
    assert "submission to devpost" in normalized_toc

    assert "no ci result" in boundaries_lower
    assert "can substitute for an attributable human decision" in boundaries_lower
    assert "theory of change approved with conditions" in status_lower
    assert "submission status: blocked by design" in status_lower
    assert "human approval not recorded" not in toc_lower
    assert "human approval not recorded" not in log_lower
