import re
import subprocess


def _publishable_paths(repo_root):
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return [repo_root / raw.decode("utf-8") for raw in completed.stdout.split(b"\0") if raw]


def _secret_findings(repo_root):
    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]
    findings = []
    for path in _publishable_paths(repo_root):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".zip", ".bundle"}:
            continue
        text = path.read_text(errors="ignore")
        if any(pattern.search(text) for pattern in patterns):
            findings.append(str(path.relative_to(repo_root)))
    return findings


def test_no_common_secret_patterns(repo_root):
    assert _secret_findings(repo_root) == []


def test_secret_scan_ignores_local_artifacts(repo_root):
    artifact_dir = repo_root / "artifacts/secret-validator-test-only"
    artifact_dir.mkdir(parents=True, exist_ok=False)
    ignored_secret = artifact_dir / "fixture.txt"
    try:
        ignored_secret.write_text("-----BEGIN " + "PRIVATE KEY-----\n", encoding="utf-8")
        assert _secret_findings(repo_root) == []
    finally:
        ignored_secret.unlink(missing_ok=True)
        artifact_dir.rmdir()
