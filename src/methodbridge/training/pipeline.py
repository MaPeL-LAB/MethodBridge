from pathlib import Path
import json


def build_fixture_dataset(root: Path, output: Path) -> int:
    records = []
    for path in sorted((root / "data/fixtures").glob("train_*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    return len(records)
