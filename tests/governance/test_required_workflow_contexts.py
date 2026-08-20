from pathlib import Path

import yaml


REQUIRED_WORKFLOWS = {
    ".github/workflows/ci.yml": "CI",
    ".github/workflows/data-governance.yml": "Data governance",
    ".github/workflows/schema-validation.yml": "Schema validation",
    ".github/workflows/submission-readiness.yml": "Submission readiness",
    ".github/workflows/repository-integrity.yml": "Repository integrity",
}


def _load_github_workflow(path: Path) -> dict:
    document = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert isinstance(document, dict)
    assert "on" in document
    assert True not in document
    return document


def test_required_workflows_emit_exact_unique_check_contexts(repo_root):
    observed_contexts = []

    for relative_path, required_context in REQUIRED_WORKFLOWS.items():
        workflow = _load_github_workflow(repo_root / relative_path)
        assert workflow["name"] == required_context
        assert workflow["on"] == {
            "pull_request": "",
            "push": {"branches": ["main"]},
        }
        assert workflow["permissions"] == {"contents": "read"}
        assert set(workflow["jobs"]) == {"validate"}
        assert workflow["jobs"]["validate"]["name"] == required_context
        assert workflow["jobs"]["validate"]["runs-on"] == "ubuntu-latest"
        observed_contexts.append(workflow["jobs"]["validate"]["name"])

    assert observed_contexts == list(REQUIRED_WORKFLOWS.values())
    assert len(observed_contexts) == len(set(observed_contexts)) == 5
