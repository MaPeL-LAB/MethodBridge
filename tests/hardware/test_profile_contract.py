import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def test_hardware_profile_has_challenge_boundaries():
    profile = yaml.safe_load(
        (ROOT / "config/adtc_standard_laptop.yml").read_text(encoding="utf-8")
    )
    assert profile["profile_id"] == "adtc-standard-laptop-2026"
    assert profile["memory"]["official_peak_rss_limit_gib"] == 7.0
    assert profile["memory"]["engineering_target_peak_rss_gib"] == 6.0
    assert profile["thermal"]["official_limit_celsius"] == 85.0
    assert profile["thermal"]["engineering_target_celsius"] == 80.0
    assert profile["repetition"] == {
        "warmup_runs": 1,
        "measured_runs": 3,
        "use_conservative_summary": True,
    }
    assert profile["submission_boundary"]["simulation_results_eligible"] is False


def test_hardware_schemas_parse():
    for name in (
        "hardware_attestation.schema.json",
        "adtc_reference_run.schema.json",
    ):
        schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_simulation_wrapper_enforces_resource_limits():
    script = (ROOT / "scripts/run_adtc_simulated_profile.sh").read_text(
        encoding="utf-8"
    )
    for required in (
        "--platform linux/amd64",
        "--cpus=4",
        "--memory=7.5g",
        "--memory-swap=7.5g",
        "--network=none",
        "--cap-drop ALL",
        "simulation_only",
    ):
        assert required in script


def test_reference_wrapper_requires_native_gate_and_three_full_runs():
    script = (ROOT / "scripts/run_adtc_reference_profile.sh").read_text(
        encoding="utf-8"
    )
    assert "--require-reference" in script
    assert "NETWORK_DISABLED_AT_INFERENCE" in script
    assert "for run in 1 2 3" in script
    assert "--skip-accuracy" in script  # warm-up only
    assert "submission-run-$run.json" in script
