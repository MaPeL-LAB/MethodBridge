"""ADTC reference-hardware classification and evidence validation.

This module deliberately separates development simulation from authoritative
reference-laptop evidence. A non-reference host can be useful, but its results
must never be promoted to the final ADTC submission measurements.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
from typing import Any, Mapping, Sequence

import yaml


REFERENCE_MATCH = "reference_match"
SIMULATION_ONLY = "simulation_only"
INVALID_ENVIRONMENT = "invalid_environment"

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class HostFacts:
    architecture: str
    cpu_model: str
    physical_cores: int | None
    logical_cores: int | None
    memory_gib: float
    os_id: str
    os_version: str
    kernel: str
    gpu_names: tuple[str, ...] = ()
    discrete_gpu_present: bool = False
    swap_enabled: bool = False
    storage_gb: float | None = None
    power_profile: str | None = None
    thermal_monitor_available: bool = False


@dataclass(frozen=True)
class ClassificationResult:
    measurement_class: str
    eligible_for_submission_score: bool
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReferenceRunValidation:
    accepted: bool
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def load_profile(path: Path | str) -> dict[str, Any]:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("hardware profile must be a mapping")
    return doc


def _run_text(command: Sequence[str]) -> str:
    try:
        proc = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _read_os_release() -> tuple[str, str]:
    path = Path("/etc/os-release")
    if path.is_file():
        values: dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            values[key] = value.strip().strip('"')
        return values.get("ID", platform.system().lower()), values.get(
            "VERSION_ID", platform.release()
        )
    return platform.system().lower(), platform.mac_ver()[0] or platform.release()


def _memory_gib() -> float:
    if sysctl := shutil.which("sysctl"):
        raw = _run_text([sysctl, "-n", "hw.memsize"])
        if raw.isdigit():
            return int(raw) / (1024**3)
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        if pages > 0 and page_size > 0:
            return float(pages * page_size) / (1024**3)
    except (ValueError, OSError, AttributeError):
        pass
    return 0.0


def _cpu_model() -> str:
    path = Path("/proc/cpuinfo")
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    if sysctl := shutil.which("sysctl"):
        raw = _run_text([sysctl, "-n", "machdep.cpu.brand_string"])
        if raw:
            return raw
    return platform.processor() or platform.machine()


def _physical_cores() -> int | None:
    if sysctl := shutil.which("sysctl"):
        raw = _run_text([sysctl, "-n", "hw.physicalcpu"])
        if raw.isdigit():
            return int(raw)
    path = Path("/proc/cpuinfo")
    if path.is_file():
        pairs: set[tuple[str, str]] = set()
        physical_id = "0"
        core_id: str | None = None
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines() + [""]:
            if not line.strip():
                if core_id is not None:
                    pairs.add((physical_id, core_id))
                physical_id, core_id = "0", None
            elif line.lower().startswith("physical id") and ":" in line:
                physical_id = line.split(":", 1)[1].strip()
            elif line.lower().startswith("core id") and ":" in line:
                core_id = line.split(":", 1)[1].strip()
        if pairs:
            return len(pairs)
    return None


def _gpu_inventory() -> tuple[tuple[str, ...], bool]:
    names: list[str] = []
    if lspci := shutil.which("lspci"):
        for line in _run_text([lspci]).splitlines():
            lower = line.lower()
            if any(token in lower for token in ("vga compatible", "3d controller", "display controller")):
                names.append(line.strip())
    elif system_profiler := shutil.which("system_profiler"):
        raw = _run_text([system_profiler, "SPDisplaysDataType"])
        for line in raw.splitlines():
            if "Chipset Model:" in line:
                names.append(line.split(":", 1)[1].strip())

    integrated_tokens = (
        "intel uhd",
        "intel iris",
        "iris xe",
        "amd radeon graphics",
        "radeon vega",
        "apple m",
        "integrated",
    )
    discrete_tokens = (
        "nvidia",
        "geforce",
        "quadro",
        "tesla",
        "rtx",
        "gtx",
        "radeon rx",
        "radeon pro",
        "arc a",
    )
    discrete = any(
        any(token in name.lower() for token in discrete_tokens)
        and not any(token in name.lower() for token in integrated_tokens)
        for name in names
    )
    return tuple(names), discrete


def _swap_enabled() -> bool:
    path = Path("/proc/meminfo")
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("SwapTotal:"):
                parts = line.split()
                return len(parts) >= 2 and parts[1].isdigit() and int(parts[1]) > 0
    if sysctl := shutil.which("sysctl"):
        raw = _run_text([sysctl, "-n", "vm.swapusage"])
        match = re.search(r"total\s*=\s*([0-9.]+)M", raw)
        if match:
            return float(match.group(1)) > 0
    return False


def _storage_gb() -> float | None:
    try:
        return shutil.disk_usage("/").total / (1000**3)
    except OSError:
        return None


def _thermal_monitor_available() -> bool:
    return bool(shutil.which("sensors")) or Path("/sys/class/thermal").is_dir()


def detect_host() -> HostFacts:
    os_id, os_version = _read_os_release()
    gpu_names, discrete = _gpu_inventory()
    storage = _storage_gb()
    return HostFacts(
        architecture=platform.machine().lower(),
        cpu_model=_cpu_model(),
        physical_cores=_physical_cores(),
        logical_cores=os.cpu_count(),
        memory_gib=round(_memory_gib(), 3),
        os_id=os_id.lower(),
        os_version=os_version,
        kernel=platform.release(),
        gpu_names=gpu_names,
        discrete_gpu_present=discrete,
        swap_enabled=_swap_enabled(),
        storage_gb=round(storage, 3) if storage is not None else None,
        power_profile=None,
        thermal_monitor_available=_thermal_monitor_available(),
    )


def _architecture_matches(value: str, profile: Mapping[str, Any]) -> bool:
    allowed = {str(item).lower() for item in profile["architecture"]["accepted_values"]}
    return value.lower() in allowed


def _cpu_matches(cpu_model: str, profile: Mapping[str, Any]) -> bool:
    return any(
        re.search(pattern, cpu_model, flags=re.IGNORECASE)
        for pattern in profile["cpu"]["allowed_model_patterns"]
    )


def _os_matches(facts: HostFacts, profile: Mapping[str, Any]) -> bool:
    expected = profile["operating_system"]
    return (
        facts.os_id.lower() == str(expected["id"]).lower()
        and facts.os_version.startswith(str(expected["version"]))
    )


def classify_host(facts: HostFacts, profile: Mapping[str, Any]) -> ClassificationResult:
    reasons: list[str] = []
    warnings: list[str] = []

    essential = {
        "architecture": facts.architecture,
        "cpu_model": facts.cpu_model,
        "memory_gib": facts.memory_gib,
        "os_id": facts.os_id,
        "os_version": facts.os_version,
    }
    missing = [key for key, value in essential.items() if value in ("", None, 0, 0.0)]
    if missing:
        return ClassificationResult(
            INVALID_ENVIRONMENT,
            False,
            tuple(f"missing_or_invalid:{key}" for key in missing),
        )

    if facts.discrete_gpu_present:
        return ClassificationResult(INVALID_ENVIRONMENT, False, ("discrete_gpu_present",))

    if not _architecture_matches(facts.architecture, profile):
        reasons.append("architecture_not_reference")
    if not _cpu_matches(facts.cpu_model, profile):
        reasons.append("cpu_not_reference")
    if not _os_matches(facts, profile):
        reasons.append("os_not_reference")

    memory = profile["memory"]
    if not (
        float(memory["installed_gib_min"])
        <= facts.memory_gib
        <= float(memory["installed_gib_max"])
    ):
        reasons.append("installed_memory_not_reference")

    min_storage = float(profile["storage"]["minimum_gb"])
    if facts.storage_gb is not None and facts.storage_gb < min_storage:
        reasons.append("storage_below_reference")

    if facts.swap_enabled:
        warnings.append("swap_enabled; strict measured run must disable swap")
    if not facts.thermal_monitor_available:
        warnings.append("thermal_monitor_unavailable")

    if reasons:
        return ClassificationResult(SIMULATION_ONLY, False, tuple(reasons), tuple(warnings))

    return ClassificationResult(REFERENCE_MATCH, True, (), tuple(warnings))


def make_attestation(
    facts: HostFacts,
    classification: ClassificationResult,
    profile: Mapping[str, Any],
    *,
    runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    host = asdict(facts)
    host["gpu_names"] = list(facts.gpu_names)
    return {
        "schema_version": "1.0.0",
        "profile_id": profile["profile_id"],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "measurement_class": classification.measurement_class,
        "eligible_for_submission_score": classification.eligible_for_submission_score,
        "host": host,
        "runtime": dict(runtime or {}),
        "reasons": list(classification.reasons),
        "warnings": list(classification.warnings),
        "limitations": (
            []
            if classification.measurement_class == REFERENCE_MATCH
            else [
                "Results from this host are development evidence only and must not "
                "be promoted to final ADTC performance, efficiency, or thermal claims."
            ]
        ),
    }


def write_json(path: Path | str, doc: Mapping[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_reference_run(
    record: Mapping[str, Any], profile: Mapping[str, Any]
) -> ReferenceRunValidation:
    blockers: list[str] = []
    warnings: list[str] = []

    if record.get("measurement_class") != REFERENCE_MATCH:
        blockers.append("host_not_reference_match")
    if record.get("eligible_for_submission_score") is not True:
        blockers.append("run_not_eligible_for_submission_score")

    host = record.get("host") or {}
    facts = HostFacts(
        architecture=str(host.get("architecture", "")),
        cpu_model=str(host.get("cpu_model", "")),
        physical_cores=host.get("physical_cores"),
        logical_cores=host.get("logical_cores"),
        memory_gib=float(host.get("memory_gib", 0) or 0),
        os_id=str(host.get("os_id", "")),
        os_version=str(host.get("os_version", "")),
        kernel=str(host.get("kernel", "")),
        gpu_names=tuple(host.get("gpu_names") or ()),
        discrete_gpu_present=bool(host.get("discrete_gpu_present")),
        swap_enabled=bool(host.get("swap_enabled")),
        storage_gb=(float(host["storage_gb"]) if host.get("storage_gb") is not None else None),
        power_profile=host.get("power_profile"),
        thermal_monitor_available=bool(host.get("thermal_monitor_available")),
    )
    host_result = classify_host(facts, profile)
    if host_result.measurement_class != REFERENCE_MATCH:
        blockers.extend(f"host:{item}" for item in host_result.reasons)
    if facts.swap_enabled:
        blockers.append("swap_enabled_during_strict_run")

    runtime = record.get("runtime") or {}
    if runtime.get("model_format") != "GGUF":
        blockers.append("model_format_not_gguf")
    if int(runtime.get("gpu_layers", -1)) != 0:
        blockers.append("gpu_offload_enabled")
    if runtime.get("network_disabled") is not True:
        blockers.append("network_not_disabled")
    if not _SHA40.fullmatch(str(runtime.get("llama_cpp_commit", ""))):
        blockers.append("invalid_llama_cpp_commit")
    if not _SHA40.fullmatch(str(runtime.get("profiler_commit", ""))):
        blockers.append("invalid_profiler_commit")
    if not _SHA256.fullmatch(str(runtime.get("model_sha256", ""))):
        blockers.append("invalid_model_sha256")
    if runtime.get("accuracy_skipped") is True:
        blockers.append("accuracy_stage_skipped")

    runs = list(record.get("measured_runs") or [])
    required_runs = int(profile["repetition"]["measured_runs"])
    if len(runs) < required_runs:
        blockers.append(f"insufficient_measured_runs:{len(runs)}<{required_runs}")
    if int(record.get("warmup_runs", 0)) < int(profile["repetition"]["warmup_runs"]):
        blockers.append("warmup_run_missing")

    official_ram = float(profile["memory"]["official_peak_rss_limit_gib"])
    target_ram = float(profile["memory"]["engineering_target_peak_rss_gib"])
    official_temp = float(profile["thermal"]["official_limit_celsius"])
    target_temp = float(profile["thermal"]["engineering_target_celsius"])

    expected_model = runtime.get("model_sha256")
    expected_llama = runtime.get("llama_cpp_commit")
    expected_profiler = runtime.get("profiler_commit")

    for index, run in enumerate(runs, start=1):
        prefix = f"run_{index}"
        if run.get("completed") is not True:
            blockers.append(f"{prefix}:incomplete")
        if run.get("crashed") is True:
            blockers.append(f"{prefix}:crashed")
        if run.get("oom") is True:
            blockers.append(f"{prefix}:oom")
        if run.get("thermal_throttled") is True:
            blockers.append(f"{prefix}:thermal_throttled")
        peak = float(run.get("peak_rss_gib", 999))
        temp = float(run.get("max_temperature_celsius", 999))
        if peak > official_ram:
            blockers.append(f"{prefix}:peak_rss_exceeds_{official_ram:g}_gib")
        elif peak > target_ram:
            warnings.append(f"{prefix}:peak_rss_above_engineering_target")
        if temp > official_temp:
            blockers.append(f"{prefix}:temperature_exceeds_{official_temp:g}_c")
        elif temp > target_temp:
            warnings.append(f"{prefix}:temperature_above_engineering_target")
        if run.get("model_sha256") != expected_model:
            blockers.append(f"{prefix}:model_digest_mismatch")
        if run.get("llama_cpp_commit") != expected_llama:
            blockers.append(f"{prefix}:llama_cpp_commit_mismatch")
        if run.get("profiler_commit") != expected_profiler:
            blockers.append(f"{prefix}:profiler_commit_mismatch")
        if run.get("network_disabled") is not True:
            blockers.append(f"{prefix}:network_not_disabled")
        if int(run.get("gpu_layers", -1)) != 0:
            blockers.append(f"{prefix}:gpu_offload_enabled")
        if run.get("accuracy_skipped") is True:
            blockers.append(f"{prefix}:accuracy_stage_skipped")

    blockers = list(dict.fromkeys(blockers))
    warnings = list(dict.fromkeys(warnings))
    return ReferenceRunValidation(not blockers, tuple(blockers), tuple(warnings))
