"""Fail-closed MethodBridge inference executors.

The repository supports two deliberately separate execution paths:

* ``simulation_proxy`` is a canned, deterministic contract-test double. It never
  loads a model and may only be used when explicitly acknowledged by the caller.
* ``llama_cpp`` executes an actual GGUF through ``llama-cli`` after checking the
  exact model digest and pinned runtime commit supplied by the caller.

Neither path automatically selects a model or creates official ADTC performance
or efficiency evidence. Qualified semantic adjudication and the official profiler
remain separate gates.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Sequence

from .router import classify_prompt

METHODBRIDGE_SYSTEM_PROMPT = (
    "You are MethodBridge, a local research methodology and biostatistics assistant.\n"
    "Your response contract:\n"
    "- Provide a clear, direct, and concise answer first.\n"
    "- Explain underlying methodological principles, assumptions, and study design trade-offs.\n"
    "- When a problem statement lacks critical study design parameters, outcome definitions, "
    "or data structure, explicitly state what is missing and ask clarifying questions instead of guessing.\n"
    "- Never fabricate or invent citations, literature sources, or DOIs.\n"
    "- Do not claim statistical significance without appropriate evidence; distinguish correlation from causation.\n"
    "- Support learning and study planning without authorizing clinical, ethical, legal, or institutional decisions."
)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


class InferenceConfigurationError(ValueError):
    """Raised when a requested execution does not satisfy the evidence contract."""


class InferenceExecutionError(RuntimeError):
    """Raised when an actual model process fails or times out."""


@dataclass(frozen=True)
class InferenceResult:
    candidate_id: str
    prompt: str
    mode: str
    response: str
    response_sha256: str
    executor_kind: str
    evidence_class: str
    prompt_template: str
    measured: bool
    eligible_as_model_output_evidence: bool
    eligible_for_model_selection: bool
    eligible_for_submission_score: bool
    model_sha256: str | None
    llama_cpp_commit: str | None
    tokens_prompt: int | None
    tokens_generated: int | None
    time_to_first_token_ms: float | None
    total_time_ms: float | None
    throughput_tps: float | None
    peak_rss_mb: float | None
    notes: tuple[str, ...]


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_chatml_prompt(
    prompt: str,
    mode: str = "native",
    system_prompt: str | None = None,
) -> str:
    """Format an input for the currently documented ChatML candidate path."""
    if mode in ("contract", "methodbridge_contract", "routed", "mode_c"):
        selected = system_prompt or METHODBRIDGE_SYSTEM_PROMPT
        return (
            f"<|im_start|>system\n{selected}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
    if mode != "native":
        raise InferenceConfigurationError(f"unsupported prompt mode: {mode}")
    return f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"


def _simulation_proxy_response(prompt: str, mode: str) -> str:
    """Return deterministic canned text for plumbing tests only.

    This function deliberately does not inspect, load, or execute a model.
    """
    lowered = prompt.lower()
    if mode in ("contract", "methodbridge_contract", "mode_c", "routed"):
        if any(term in lowered for term in ("doi", "citation", "reference", "paper by", "fabricated")):
            return (
                "Direct answer: I cannot verify or invent citations or DOIs. "
                "Use an authoritative literature index and provide the verified source "
                "before relying on a bibliographic claim."
            )
        if any(term in lowered for term in ("which test", "what statistical test", "how should i analyze")):
            return (
                "Direct answer: A test cannot be selected responsibly until the outcome scale, "
                "observation structure, inferential goal, and assumptions are specified. "
                "Clarify whether observations are independent, paired, repeated, or clustered, "
                "and report effect sizes and uncertainty alongside any test."
            )
        if any(term in lowered for term in ("write my", "complete my", "my exam", "my assignment", "my homework")):
            return (
                "Direct answer: I cannot produce submission-ready assessed work. "
                "I can explain the underlying methodological principles and work through a separate example."
            )
        if any(term in lowered for term in ("prescribe", "diagnose", "authorize treatment")):
            return (
                "Direct answer: I cannot diagnose, prescribe, or authorize treatment. "
                "A qualified human professional must retain clinical authority."
            )
        if any(term in lowered for term in ("causal", "observational", "confound", "p-value", "confidence interval")):
            return (
                "Direct answer: An observational association does not by itself establish causation. "
                "Interpret the estimate with its uncertainty, identify confounding and selection risks, "
                "state the estimand, and avoid a binary significant/not-significant conclusion."
            )
        return (
            "Direct answer: The scenario requires a bounded methodological assessment. "
            "State the research question, estimand, design, assumptions, missing information, "
            "and the decisions that require qualified human review."
        )

    # Native proxy is intentionally weak so tests can exercise comparison plumbing.
    if any(term in lowered for term in ("doi", "fabricated")):
        return "Here is an unverified example DOI: 10.1000/example."
    if any(term in lowered for term in ("write my", "my exam")):
        return "Here is a submission-ready answer."
    if "which test" in lowered:
        return "Use a t-test."
    if any(term in lowered for term in ("causal", "observational")):
        return "The observed association proves the intervention caused the outcome."
    return "Run a regression and interpret the result."


def run_simulation_proxy(
    prompt: str,
    *,
    candidate_id: str,
    mode: str,
    explicit_acknowledgement: bool = False,
    system_prompt: str | None = None,
) -> InferenceResult:
    """Run the deterministic simulation proxy after explicit acknowledgement."""
    if not explicit_acknowledgement:
        raise InferenceConfigurationError(
            "simulation proxy is disabled by default; pass an explicit acknowledgement"
        )
    # Formatting validates the requested prompt mode. The proxy does not interpret
    # or test the supplied system prompt as a model would.
    format_chatml_prompt(prompt, mode=mode, system_prompt=system_prompt)
    response = _simulation_proxy_response(prompt, mode)
    return InferenceResult(
        candidate_id=candidate_id,
        prompt=prompt,
        mode=mode,
        response=response,
        response_sha256=_sha256_text(response),
        executor_kind="simulation_proxy",
        evidence_class="simulation_proxy",
        prompt_template="simulation_proxy",
        measured=False,
        eligible_as_model_output_evidence=False,
        eligible_for_model_selection=False,
        eligible_for_submission_score=False,
        model_sha256=None,
        llama_cpp_commit=None,
        tokens_prompt=None,
        tokens_generated=None,
        time_to_first_token_ms=None,
        total_time_ms=None,
        throughput_tps=None,
        peak_rss_mb=None,
        notes=(
            "No model was loaded or executed.",
            "Canned responses may validate plumbing only.",
            "No timing, memory, quality, retention, or ranking claim may be derived.",
        ),
    )


def run_simulation_proxy_mode_c(
    prompt: str,
    *,
    candidate_id: str,
    explicit_acknowledgement: bool = False,
) -> InferenceResult:
    routed = classify_prompt(prompt)
    result = run_simulation_proxy(
        prompt,
        candidate_id=candidate_id,
        mode="mode_c",
        explicit_acknowledgement=explicit_acknowledgement,
        system_prompt=routed.system_prompt,
    )
    return InferenceResult(
        **{
            **result.__dict__,
            "mode": f"mode_c:{routed.task_class.value}",
            "notes": result.notes
            + (
                "The deterministic router was exercised, but routed model behaviour was not tested.",
            ),
        }
    )


def _resolve_binary(value: str | Path) -> str:
    candidate = str(value)
    if Path(candidate).is_file():
        return str(Path(candidate).resolve())
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    raise InferenceConfigurationError(f"llama.cpp executable not found: {candidate}")


def run_llama_cpp_inference(
    prompt: str,
    *,
    candidate_id: str,
    mode: str,
    model_path: Path,
    expected_model_sha256: str,
    llama_cpp_commit: str,
    llama_cli: str | Path = "llama-cli",
    prompt_template: str,
    context_size: int = 2048,
    temperature: float = 0.0,
    max_tokens: int = 256,
    timeout_seconds: int = 180,
    system_prompt: str | None = None,
    extra_args: Sequence[str] = (),
) -> InferenceResult:
    """Execute an actual GGUF with a digest-bound ``llama-cli`` process.

    This function captures real model output, but it does not produce official
    ADTC throughput, memory, or thermal evidence. Those metrics must come from
    the pinned official profiler on an eligible reference host.
    """
    model_path = model_path.expanduser().resolve()
    if not model_path.is_file():
        raise InferenceConfigurationError(f"GGUF does not exist: {model_path}")
    if model_path.suffix.lower() != ".gguf":
        raise InferenceConfigurationError("model path must end in .gguf")
    expected = expected_model_sha256.lower()
    if not _HEX64.fullmatch(expected):
        raise InferenceConfigurationError("expected model SHA-256 must be 64 lowercase hex characters")
    if not _HEX40.fullmatch(llama_cpp_commit.lower()):
        raise InferenceConfigurationError("llama.cpp commit must be a full 40-character SHA")
    actual = sha256_file(model_path)
    if actual != expected:
        raise InferenceConfigurationError(
            f"GGUF SHA-256 mismatch: expected {expected}, observed {actual}"
        )

    binary = _resolve_binary(llama_cli)
    if prompt_template != "chatml":
        raise InferenceConfigurationError(
            "unsupported or unverified prompt template; currently only explicit chatml is allowed"
        )
    formatted = format_chatml_prompt(prompt, mode=mode, system_prompt=system_prompt)
    command = [
        binary,
        "--model",
        str(model_path),
        "--prompt",
        formatted,
        "--ctx-size",
        str(context_size),
        "--temp",
        str(temperature),
        "--n-predict",
        str(max_tokens),
        "--gpu-layers",
        "0",
        "--no-display-prompt",
        "--log-disable",
        *extra_args,
    ]

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise InferenceExecutionError(
            f"llama.cpp inference exceeded {timeout_seconds} seconds"
        ) from exc
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    if completed.returncode != 0:
        tail = (completed.stderr or "").strip()[-500:]
        raise InferenceExecutionError(
            f"llama.cpp exited with code {completed.returncode}: {tail}"
        )
    response = completed.stdout.strip()
    if not response:
        raise InferenceExecutionError("llama.cpp returned an empty response")

    return InferenceResult(
        candidate_id=candidate_id,
        prompt=prompt,
        mode=mode,
        response=response,
        response_sha256=_sha256_text(response),
        executor_kind="llama_cpp",
        evidence_class="local_real_model_output",
        prompt_template=prompt_template,
        measured=True,
        eligible_as_model_output_evidence=True,
        eligible_for_model_selection=False,
        eligible_for_submission_score=False,
        model_sha256=actual,
        llama_cpp_commit=llama_cpp_commit.lower(),
        tokens_prompt=None,
        tokens_generated=None,
        time_to_first_token_ms=None,
        total_time_ms=round(elapsed_ms, 3),
        throughput_tps=None,
        peak_rss_mb=None,
        notes=(
            "An actual digest-bound GGUF process produced this response.",
            "Qualified semantic review is still required before model selection.",
            "Official ADTC profiler evidence is required for scoreable performance, memory, and thermal claims.",
        ),
    )


def run_candidate_inference(
    prompt: str,
    *,
    candidate_id: str,
    mode: str,
    model_path: Path,
    expected_model_sha256: str,
    llama_cpp_commit: str,
    llama_cli: str | Path = "llama-cli",
    prompt_template: str,
    context_size: int = 2048,
    temperature: float = 0.0,
    max_tokens: int = 256,
    timeout_seconds: int = 180,
    system_prompt: str | None = None,
) -> InferenceResult:
    """Compatibility entry point for real, fail-closed ``llama.cpp`` inference."""
    return run_llama_cpp_inference(
        prompt,
        candidate_id=candidate_id,
        mode=mode,
        model_path=model_path,
        expected_model_sha256=expected_model_sha256,
        llama_cpp_commit=llama_cpp_commit,
        llama_cli=llama_cli,
        prompt_template=prompt_template,
        context_size=context_size,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        system_prompt=system_prompt,
    )


def run_candidate_inference_mode_c(
    prompt: str,
    *,
    candidate_id: str,
    model_path: Path,
    expected_model_sha256: str,
    llama_cpp_commit: str,
    llama_cli: str | Path = "llama-cli",
    prompt_template: str,
    context_size: int = 2048,
    temperature: float = 0.0,
    max_tokens: int = 256,
    timeout_seconds: int = 180,
) -> InferenceResult:
    """Run real GGUF inference with the deterministic Mode C prompt router."""
    routed = classify_prompt(prompt)
    result = run_llama_cpp_inference(
        prompt,
        candidate_id=candidate_id,
        mode="mode_c",
        model_path=model_path,
        expected_model_sha256=expected_model_sha256,
        llama_cpp_commit=llama_cpp_commit,
        llama_cli=llama_cli,
        prompt_template=prompt_template,
        context_size=context_size,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
        system_prompt=routed.system_prompt,
    )
    return InferenceResult(
        **{
            **result.__dict__,
            "mode": f"mode_c:{routed.task_class.value}",
            "notes": result.notes
            + (
                f"Router class: {routed.task_class.value}; ambiguous={routed.ambiguous}.",
            ),
        }
    )
