import json

def test_manifest_has_entries(repo_root):
    manifest=json.loads((repo_root/"MANIFEST.json").read_text())
    assert manifest["repository"] == "methodbridge-local"
    assert len(manifest["files"]) >= 250
