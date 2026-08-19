from methodbridge.evaluation import load_cases

def test_case_counts(repo_root):
    cases=load_cases(repo_root)
    assert len(cases) == 60
    assert sum(c["bootstrap_executable"] for c in cases) == 40
