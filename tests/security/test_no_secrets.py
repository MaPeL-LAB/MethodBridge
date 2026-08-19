import re

def test_no_common_secret_patterns(repo_root):
    patterns=[re.compile(r"AKIA[0-9A-Z]{16}"), re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")]
    findings=[]
    for path in repo_root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() in {".png",".jpg",".jpeg",".zip",".bundle"}:
            continue
        text=path.read_text(errors="ignore")
        if any(p.search(text) for p in patterns):
            findings.append(str(path.relative_to(repo_root)))
    assert findings == []
