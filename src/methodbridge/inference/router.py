"""Deterministic, boundary-aware prompt routing for MethodBridge Mode C.

The router selects a prompt contract; it does not assess answer correctness and
it does not constitute model evidence. Matching uses token/phrase boundaries so
short methodological abbreviations do not trigger inside unrelated words.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class TaskClass(str, Enum):
    CAUSAL_INFERENCE = "causal_inference"
    CITATION_INTEGRITY = "citation_integrity"
    STUDY_DESIGN = "study_design"
    STATISTICAL_METHODS = "statistical_methods"
    UNCERTAINTY_PVALUES = "uncertainty_pvalues"
    ACADEMIC_INTEGRITY = "academic_integrity"
    GENERAL_REASONING = "general_reasoning"


_KEYWORDS: dict[TaskClass, tuple[str, ...]] = {
    TaskClass.ACADEMIC_INTEGRITY: (
        "write my", "do my", "complete my", "my exam", "my homework",
        "my assignment", "my dissertation", "my essay", "my thesis",
        "prescribe", "diagnose", "clinical decision",
        "authorize treatment", "approve treatment",
    ),
    TaskClass.CITATION_INTEGRITY: (
        "doi", "cite", "citation*", "reference*", "paper by", "study by",
        "article by", "journal", "published", "authors found",
        "according to", "findings of", "bibliography", "fabricat*",
    ),
    TaskClass.CAUSAL_INFERENCE: (
        "cause*", "causal", "effect of", "impact of", "confound*", "dag", "directed acyclic", "instrumental variable",
        "iv", "difference-in-difference", "did", "regression discontinuity",
        "propensity score", "counterfactual", "treatment effect",
        "ate", "att", "late", "mediation", "collider", "backdoor",
        "sutva", "spillover", "interfere*",
    ),
    TaskClass.STUDY_DESIGN: (
        "study design", "rct", "randomized", "randomised",
        "controlled trial", "cohort study", "case-control",
        "cross-sectional", "longitudinal", "prospective", "retrospective",
        "blinding", "allocation", "sample size", "eligibility criteria",
        "inclusion criteria", "cluster randomiz*", "cluster randomis*",
    ),
    TaskClass.STATISTICAL_METHODS: (
        "which test", "what test", "what statistical", "which statistical",
        "statistical test", "what analysis", "analyze my data",
        "how do i analyze", "how should i analyze",
        "t-test", "anova", "logistic regression", "survival analysis",
        "kaplan", "cox model", "mixed model", "multilevel",
        "hierarchical model", "bayesian", "mann-whitney", "wilcoxon",
        "chi-squared", "fisher's exact", "non-parametric",
    ),
    TaskClass.UNCERTAINTY_PVALUES: (
        "p-value", "p value", "p = 0", "p=0",
        "significant", "significance", "confidence interval",
        "null hypothesis", "type i error", "type ii error",
        "false positive", "false negative", "reject the null",
        "alpha level", "multiplicity", "subgroup", "multiple outcome*",
        "bonferroni", "false discovery",
    ),
}


SPECIALIZED_SYSTEM_PROMPTS: dict[TaskClass, str] = {
    TaskClass.CAUSAL_INFERENCE: (
        "You are MethodBridge, a causal inference and epidemiological methods assistant.\n"
        "Response contract:\n"
        "- Distinguish associative from causal estimands before answering.\n"
        "- Ask for the treatment-outcome pathway and potential confounders when missing.\n"
        "- Identify confounding, selection bias, information bias, and relevant causal assumptions.\n"
        "- Never claim that an observational association proves causation.\n"
        "- Do not fabricate citations or empirical findings."
    ),
    TaskClass.CITATION_INTEGRITY: (
        "You are MethodBridge, a research integrity and literature guidance assistant.\n"
        "Response contract:\n"
        "- Never invent or confirm unverified DOIs, authors, journals, volumes, or pages.\n"
        "- Direct users to authoritative indexes or their institutional library for verification.\n"
        "- Discuss a methodological concept without pretending an unverified paper exists.\n"
        "- Academic integrity requires traceable provenance for referenced claims."
    ),
    TaskClass.STUDY_DESIGN: (
        "You are MethodBridge, a study design and research methods assistant.\n"
        "Response contract:\n"
        "- Clarify the research question, estimand, unit of analysis, and target population.\n"
        "- Compare experimental and observational designs and their validity trade-offs.\n"
        "- Address confounding, selection, attrition, measurement bias, and generalizability.\n"
        "- Do not recommend a design without feasibility and ethical context."
    ),
    TaskClass.STATISTICAL_METHODS: (
        "You are MethodBridge, a statistical methods and analysis assistant.\n"
        "Response contract:\n"
        "- Ask about the outcome scale, observation structure, inferential goal, and assumptions.\n"
        "- Distinguish descriptive from inferential aims.\n"
        "- Recommend diagnostics and effect sizes with uncertainty.\n"
        "- Do not authorize a final analysis decision from incomplete information."
    ),
    TaskClass.UNCERTAINTY_PVALUES: (
        "You are MethodBridge, a statistical inference and uncertainty communication assistant.\n"
        "Response contract:\n"
        "- Never interpret a p-value as proof of presence or absence of an effect.\n"
        "- Explain confidence intervals as values compatible with the data under the model.\n"
        "- Discourage binary significant/non-significant thinking.\n"
        "- Distinguish statistical significance from practical importance and flag multiplicity."
    ),
    TaskClass.ACADEMIC_INTEGRITY: (
        "You are MethodBridge, a pedagogical research methods assistant with strict academic-integrity boundaries.\n"
        "Response contract:\n"
        "- Do not write or complete assessed submissions, exams, assignments, or dissertations for a user.\n"
        "- Redirect the user to concepts, worked examples, and formative learning support.\n"
        "- Do not diagnose, prescribe, or authorize clinical or institutional decisions.\n"
        "- Preserve accountable human authority."
    ),
    TaskClass.GENERAL_REASONING: (
        "You are MethodBridge, a local research methodology and biostatistics assistant.\n"
        "Response contract:\n"
        "- Give a direct answer, then state principles, assumptions, and trade-offs.\n"
        "- Identify missing information instead of guessing.\n"
        "- Never fabricate citations or convert uncertainty into certainty.\n"
        "- Support learning without authorizing consequential decisions."
    ),
}

_PRIORITY_ORDER: tuple[TaskClass, ...] = (
    TaskClass.ACADEMIC_INTEGRITY,
    TaskClass.CITATION_INTEGRITY,
    TaskClass.CAUSAL_INFERENCE,
    TaskClass.STUDY_DESIGN,
    TaskClass.STATISTICAL_METHODS,
    TaskClass.UNCERTAINTY_PVALUES,
)


@dataclass(frozen=True)
class RouterResult:
    task_class: TaskClass
    system_prompt: str
    matched_keywords: tuple[str, ...]
    candidate_classes: tuple[TaskClass, ...]
    ambiguous: bool
    confidence: str


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    value = keyword.strip().lower()
    prefix = value.endswith("*")
    if prefix:
        value = value[:-1]
    escaped = re.escape(value).replace(r"\ ", r"\s+")
    suffix = r"\w*" if prefix else r"(?!\w)"
    return re.compile(rf"(?<!\w){escaped}{suffix}", re.IGNORECASE)


def _matching_keywords(prompt: str, task_class: TaskClass) -> tuple[str, ...]:
    return tuple(
        keyword.rstrip("*")
        for keyword in _KEYWORDS[task_class]
        if _keyword_pattern(keyword).search(prompt)
    )


def classify_prompt(prompt: str) -> RouterResult:
    """Choose the highest-priority matching prompt contract.

    Multiple matching classes are exposed as ambiguity rather than silently
    pretending the rule-based classification is certain.
    """
    matches: list[tuple[TaskClass, tuple[str, ...]]] = []
    for task_class in _PRIORITY_ORDER:
        hits = _matching_keywords(prompt, task_class)
        if hits:
            matches.append((task_class, hits))

    if not matches:
        return RouterResult(
            task_class=TaskClass.GENERAL_REASONING,
            system_prompt=SPECIALIZED_SYSTEM_PROMPTS[TaskClass.GENERAL_REASONING],
            matched_keywords=(),
            candidate_classes=(TaskClass.GENERAL_REASONING,),
            ambiguous=False,
            confidence="fallback",
        )

    selected, hits = matches[0]
    classes = tuple(task_class for task_class, _ in matches)
    return RouterResult(
        task_class=selected,
        system_prompt=SPECIALIZED_SYSTEM_PROMPTS[selected],
        matched_keywords=hits,
        candidate_classes=classes,
        ambiguous=len(classes) > 1,
        confidence="high" if len(classes) == 1 else "ambiguous_priority_resolution",
    )
