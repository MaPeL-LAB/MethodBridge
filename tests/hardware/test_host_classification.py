from pathlib import Path

from methodbridge.hardware import (
    HostFacts,
    INVALID_ENVIRONMENT,
    REFERENCE_MATCH,
    SIMULATION_ONLY,
    classify_host,
    load_profile,
)

ROOT = Path(__file__).resolve().parents[2]
PROFILE = load_profile(ROOT / "config/adtc_standard_laptop.yml")


def reference_facts(**overrides):
    values = dict(
        architecture="x86_64",
        cpu_model="Intel(R) Core(TM) i5-1135G7",
        physical_cores=4,
        logical_cores=8,
        memory_gib=7.9,
        os_id="ubuntu",
        os_version="22.04",
        kernel="5.15.0",
        gpu_names=("Intel Iris Xe Graphics",),
        discrete_gpu_present=False,
        swap_enabled=False,
        storage_gb=256.1,
        power_profile="balanced",
        thermal_monitor_available=True,
    )
    values.update(overrides)
    return HostFacts(**values)


def test_reference_host_is_eligible():
    result = classify_host(reference_facts(), PROFILE)
    assert result.measurement_class == REFERENCE_MATCH
    assert result.eligible_for_submission_score is True


def test_apple_silicon_is_simulation_only():
    result = classify_host(
        reference_facts(
            architecture="arm64",
            cpu_model="Apple M4 Max",
            memory_gib=64,
            os_id="darwin",
            os_version="15.6",
            storage_gb=1000,
        ),
        PROFILE,
    )
    assert result.measurement_class == SIMULATION_ONLY
    assert result.eligible_for_submission_score is False
    assert "architecture_not_reference" in result.reasons


def test_wrong_x86_cpu_is_simulation_only():
    result = classify_host(
        reference_facts(cpu_model="Intel(R) Core(TM) i9-14900HX"),
        PROFILE,
    )
    assert result.measurement_class == SIMULATION_ONLY
    assert "cpu_not_reference" in result.reasons


def test_amd_reference_series_is_accepted():
    result = classify_host(
        reference_facts(cpu_model="AMD Ryzen 5 5600U with Radeon Graphics"),
        PROFILE,
    )
    assert result.measurement_class == REFERENCE_MATCH


def test_discrete_gpu_is_invalid():
    result = classify_host(
        reference_facts(
            gpu_names=("Intel Iris Xe", "NVIDIA GeForce RTX 3060"),
            discrete_gpu_present=True,
        ),
        PROFILE,
    )
    assert result.measurement_class == INVALID_ENVIRONMENT
    assert result.eligible_for_submission_score is False


def test_missing_memory_is_invalid():
    result = classify_host(reference_facts(memory_gib=0), PROFILE)
    assert result.measurement_class == INVALID_ENVIRONMENT
