import importlib.util
from pathlib import Path

import yaml


def _load_module(repo_root: Path):
    path = repo_root / "scripts/validate_local_model_campaign.py"
    spec = importlib.util.spec_from_file_location("validate_local_model_campaign", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_campaign_is_valid_but_not_authorized(repo_root):
    module = _load_module(repo_root)
    campaign, errors = module.validate_campaign(repo_root)
    assert not errors
    assert campaign["status"] == "prepared_not_authorized"
    assert campaign["authority"]["downloads_allowed"] is False
    assert campaign["authority"]["empirical_execution_allowed"] is False


def test_campaign_cannot_enable_downloads_without_authority(repo_root, tmp_path):
    module = _load_module(repo_root)
    campaign = yaml.safe_load((repo_root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    campaign["authority"]["downloads_allowed"] = True
    (tmp_path / "config").mkdir()
    (tmp_path / "schemas").mkdir()
    (tmp_path / "config/local_model_campaign.yml").write_text(yaml.safe_dump(campaign, sort_keys=False), encoding="utf-8")
    (tmp_path / "schemas/local_model_campaign.schema.json").write_text((repo_root / "schemas/local_model_campaign.schema.json").read_text(encoding="utf-8"), encoding="utf-8")
    _, errors = module.validate_campaign(tmp_path)
    assert "downloads_allowed must remain false before authorization" in errors
