import json
from methodbridge.data import normalize_text

def test_public_prompts_not_in_train(repo_root):
    metadata=json.loads((repo_root/"metadata.json").read_text())
    public={normalize_text(p["prompt"]) for p in metadata["test_prompts"]}
    train=set()
    for path in (repo_root/"data/fixtures").glob("train_*.json"):
        train.add(normalize_text(json.loads(path.read_text())["prompt"]))
    assert not (public & train)
