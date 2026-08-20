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


def _write_campaign_contract(repo_root: Path, target: Path, campaign: dict) -> None:
    (target / "config").mkdir()
    (target / "schemas").mkdir()
    (target / "config/local_model_campaign.yml").write_text(
        yaml.safe_dump(campaign, sort_keys=False), encoding="utf-8"
    )
    for relative in (
        "config/base_model_candidates.yml",
        "config/model_candidate_policy.yml",
        "schemas/local_model_campaign.schema.json",
    ):
        destination = target / relative
        destination.write_text((repo_root / relative).read_text(encoding="utf-8"), encoding="utf-8")


def test_campaign_is_valid_for_development_only_r_and_d(repo_root):
    module = _load_module(repo_root)
    campaign, errors = module.validate_campaign(repo_root)
    assert not errors
    assert campaign["status"] == "authorized_for_local_execution"
    assert campaign["authority"]["eligibility_gate"] == "unresolved"
    assert campaign["authority"]["human_execution_authorization"] == {
        "status": "recorded",
        "actor": "Marothi Peter Letsoalo",
        "timestamp": "2026-08-20T12:33:58+02:00",
        "decision_reference": "EXEC-001",
    }
    assert campaign["authority"]["downloads_allowed"] is True
    assert campaign["authority"]["empirical_execution_allowed"] is True
    assert module.development_r_and_d_authorized(campaign) is True


def test_campaign_cannot_enable_development_without_complete_exec_001(repo_root, tmp_path):
    module = _load_module(repo_root)
    campaign = yaml.safe_load((repo_root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    campaign["authority"]["human_execution_authorization"]["decision_reference"] = None
    _write_campaign_contract(repo_root, tmp_path, campaign)
    _, errors = module.validate_campaign(tmp_path)
    assert "recorded human execution authorization is incomplete" in errors
    assert "downloads_allowed requires a complete EXEC-001 human record" in errors
    assert "empirical_execution_allowed requires a complete EXEC-001 human record" in errors


def test_campaign_rejects_credentialed_candidate_even_with_human_record(repo_root, tmp_path):
    module = _load_module(repo_root)
    campaign = yaml.safe_load((repo_root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    _write_campaign_contract(repo_root, tmp_path, campaign)
    registry_path = tmp_path / "config/base_model_candidates.yml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registry["candidates"][0]["access"] = "credentials_required"
    registry_path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    _, errors = module.validate_campaign(tmp_path)

    assert (
        "campaign candidate requires non-public or credentialed access: qwen25_1_5b_instruct"
        in errors
    )


def test_campaign_rejects_floating_candidate_revision(repo_root, tmp_path):
    module = _load_module(repo_root)
    campaign = yaml.safe_load((repo_root / "config/local_model_campaign.yml").read_text(encoding="utf-8"))
    _write_campaign_contract(repo_root, tmp_path, campaign)
    registry_path = tmp_path / "config/base_model_candidates.yml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registry["candidates"][0]["revision"] = "main"
    registry_path.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    _, errors = module.validate_campaign(tmp_path)

    assert "campaign candidate lacks an exact lowercase commit revision: qwen25_1_5b_instruct" in errors
