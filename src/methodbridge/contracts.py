from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    family: str
    prompt: str
    expected_key_points: tuple[str, ...]
    prohibited_errors: tuple[str, ...]
    bootstrap_executable: bool

@dataclass
class ReadinessResult:
    ready: bool
    blockers: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
