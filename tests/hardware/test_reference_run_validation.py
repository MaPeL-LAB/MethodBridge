from pathlib import Path

from methodbridge.hardware import load_profile, validate_reference_run


ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_profile(ROOT / "config/adtc_standard_laptop.yml")
MODEL_SHA = "a" * 64
LLAMA_SHA = "b" * 40
PROFILER_SHA = "c" * 40


def reference_record():
    host = {
        "architecture": "x86_64",
        "cpu_model": "Intel(R) Core(TM) i5-1135G7",
        "physical_cores": 4,
        "logical_cores": 8,
        "memory_gib": 7.9,
        "os_id": "ubuntu",
        "os_version": "22.04",
        "kernel": "5.15.0",
        "gpu_names": ["Intel Iris Xe Graphics"],
        "discrete_gpu_present": False,
        "swap_enabled": False,
        "storage_gb": 256.1,
        "power_profile": "balanced",
        "thermal_monitor_available": True,
    }
    runtime = {
        "model_format": "GGUF",
        "model_sha256": MODEL_SHA,
        "llama_cpp_commit": LLAMA_SHA,
        "profiler_commit": PROFILER_SHA,
        "gpu_layers": 0,
        "network_disabled": True,
        "accuracy_skipped": False,
        "runtime_args": ["-ngl", "0"],
    }
    runs = []
    for index in range(1, 4):
        runs.append(
            {
                "run_id": f"run-{index}",
                "completed": True,
                "crashed": False,
                "oom": False,
                "peak_rss_gib": 5.7,
                "steady_state_rss_gib": 5.4,
                "tokens_per_second": 10.0 + index,
                "first_token_latency_ms": 600.0,
                "max_temperature_celsius": 77.0,
                "thermal_throttled": False,
                "model_sha256": MODEL_SHA,
                "llama_cpp_commit": LLAMA_SHA,
                "profiler_commit": PROFILER_SHA,
                "gpu_layers": 0,
                "network_disabled": True,
                "accuracy_skipped": False,
            }
        )
    return {
        "schema_version": "1.0.0",
        "profile_id": "adtc-standard-laptop-2026",
        "measurement_class": "reference_match",
        "eligible_for_submission_score": True,
        "host": host,
        "runtime": runtime,
        "warmup_runs": 1,
        "measured_runs": runs,
        "limitations": [],
    }


def test_valid_reference_record_is_accepted():
    result = validate_reference_run(reference_record(), PROFILE)
    assert result.accepted is True
    assert result.blockers == ()


def test_simulation_cannot_be_final():
    record = reference_record()
    record["measurement_class"] = "simulation_only"
    record["eligible_for_submission_score"] = False
    result = validate_reference_run(record, PROFILE)
    assert result.accepted is False
    assert "host_not_reference_match" in result.blockers


def test_peak_ram_over_official_limit_blocks():
    record = reference_record()
    record["measured_runs"][0]["peak_rss_gib"] = 7.01
    result = validate_reference_run(record, PROFILE)
    assert any("peak_rss_exceeds_7_gib" in item for item in result.blockers)


def test_peak_ram_over_internal_target_warns():
    record = reference_record()
    record["measured_runs"][0]["peak_rss_gib"] = 6.2
    result = validate_reference_run(record, PROFILE)
    assert result.accepted is True
    assert "run_1:peak_rss_above_engineering_target" in result.warnings


def test_temperature_over_official_limit_blocks():
    record = reference_record()
    record["measured_runs"][0]["max_temperature_celsius"] = 85.1
    result = validate_reference_run(record, PROFILE)
    assert any("temperature_exceeds_85_c" in item for item in result.blockers)


def test_thermal_throttling_blocks():
    record = reference_record()
    record["measured_runs"][1]["thermal_throttled"] = True
    result = validate_reference_run(record, PROFILE)
    assert "run_2:thermal_throttled" in result.blockers


def test_oom_and_crash_block():
    record = reference_record()
    record["measured_runs"][0]["oom"] = True
    record["measured_runs"][1]["crashed"] = True
    result = validate_reference_run(record, PROFILE)
    assert "run_1:oom" in result.blockers
    assert "run_2:crashed" in result.blockers


def test_network_and_gpu_offload_block():
    record = reference_record()
    record["runtime"]["network_disabled"] = False
    record["runtime"]["gpu_layers"] = 1
    record["measured_runs"][0]["network_disabled"] = False
    record["measured_runs"][0]["gpu_layers"] = 1
    result = validate_reference_run(record, PROFILE)
    assert "network_not_disabled" in result.blockers
    assert "gpu_offload_enabled" in result.blockers
    assert "run_1:network_not_disabled" in result.blockers
    assert "run_1:gpu_offload_enabled" in result.blockers


def test_accuracy_skip_blocks():
    record = reference_record()
    record["runtime"]["accuracy_skipped"] = True
    record["measured_runs"][2]["accuracy_skipped"] = True
    result = validate_reference_run(record, PROFILE)
    assert "accuracy_stage_skipped" in result.blockers
    assert "run_3:accuracy_stage_skipped" in result.blockers


def test_model_digest_mismatch_blocks():
    record = reference_record()
    record["measured_runs"][1]["model_sha256"] = "d" * 64
    result = validate_reference_run(record, PROFILE)
    assert "run_2:model_digest_mismatch" in result.blockers


def test_three_measured_runs_are_required():
    record = reference_record()
    record["measured_runs"] = record["measured_runs"][:2]
    result = validate_reference_run(record, PROFILE)
    assert "insufficient_measured_runs:2<3" in result.blockers
