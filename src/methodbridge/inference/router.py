"""Prompt-level task router for MethodBridge Mode C.

Classifies incoming research prompts into task classes and returns
the appropriate specialized system prompt. No additional model is
loaded -- classification is deterministic and rule-based.

Priority order (highest -> lowest):
  1. ACADEMIC_INTEGRITY  - detected first to protect against misuse
  2. CITATION_INTEGRITY  - fabricated / unverifiable reference requests
  3. CAUSAL_INFERENCE    - confounding, DAGs, causal language
  4. STUDY_DESIGN        - RCT, cohort, inclusion criteria, blinding
  5. STATISTICAL_METHODS - test selection, ANOVA, regression, etc.
  6. UNCERTAINTY_PVALUES - p-values, confidence intervals, significance
  7. GENERAL_REASONING   - fallback for any unmatched prompt
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TaskClass(str, Enum):
    CAUSAL_INFERENCE = "causal_inference"
    CITATION_INTEGRITY = "citation_integrity"
    STUDY_DESIGN = "study_design"
    STATISTICAL_METHODS = "statistical_methods"
    UNCERTAINTY_PVALUES = "uncertainty_pvalues"
    ACADEMIC_INTEGRITY = "academic_integrity"
    GENERAL_REASONING = "general_reasoning"


# ---------------------------------------------------------------------------
# Keyword sets per task class
# ---------------------------------------------------------------------------

_KEYWORDS: dict[TaskClass, tuple[str, ...]] = {
    TaskClass.ACADEMIC_INTEGRITY: (
        "write my", "do my", "complete my", "my exam", "my homework",
        "my assignment", "my dissertation", "my essay", "my thesis",
        "prescribe", "diagnose", "clinical decision",
        "authorize treatment", "approve treatment",
    ),
    TaskClass.CITATION_INTEGRITY: (
        "doi", "cite ", "citation", "reference", "paper by", "study by",
        "article by", "journal", "published", "authors found",
        "according to", "findings of", "bibliography", "fabricat",
    ),
    TaskClass.CAUSAL_INFERENCE: (
        "cause", "causal", "effect of", "impact of", "confound",
        "confounder", "dag", "directed acyclic", "instrumental variable",
        " iv ", "difference-in-difference", "did ", "regression discontinuity",
        "propensity score", "counterfactual", "treatment effect",
        "ate", "att", "late", "mediation", "collider", "backdoor",
        "sutva", "spillover", "interfere",
    ),
    TaskClass.STUDY_DESIGN: (
        "study design", "rct", "randomized", "randomised",
        "controlled trial", "cohort study", "case-control",
        "cross-sectional", "longitudinal", "prospective", "retrospective",
        "blinding", "allocation", "sample size", "eligibility criteria",
        "inclusion criteria", "cluster randomiz", "cluster randomis",
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
        "alpha level", "multiplicity", "subgroup", "multiple outcome",
        "bonferroni", "false discovery",
    ),
}

# ---------------------------------------------------------------------------
# Specialized system prompts
# ---------------------------------------------------------------------------

SPECIALIZED_SYSTEM_PROMPTS: dict[TaskClass, str] = {
    TaskClass.CAUSAL_INFERENCE: (
        "You are MethodBridge, a causal inference and epidemiological methods assistant.\n"
        "Response contract:\n"
        "- Always distinguish associative from causal estimands before answering.\n"
        "- Ask for DAG structure, treatment-outcome pathway, and potential confounders if not specified.\n"
        "- Explicitly identify confounding, selection bias, and information bias risks.\n"
        "- Distinguish ATE, ATT, and LATE where relevant.\n"
        "- Flag collider stratification, immortal time bias, and SUTVA violations where applicable.\n"
        "- Never claim that an observational association proves causation.\n"
        "- Do not fabricate citations or empirical findings."
    ),
    TaskClass.CITATION_INTEGRITY: (
        "You are MethodBridge, a research integrity and literature guidance assistant.\n"
        "Response contract:\n"
        "- Never generate, invent, confirm, or partially fabricate DOIs, author names, journal names, "
        "volume numbers, or page numbers.\n"
        "- When asked for citations: state that you cannot verify literature, and direct the user to "
        "PubMed (pubmed.ncbi.nlm.nih.gov), CrossRef (crossref.org), or their institutional library.\n"
        "- If a user provides a suspected citation, you may discuss the methodological concept it "
        "represents without confirming its existence.\n"
        "- Do not paraphrase or summarize a paper you cannot verify exists.\n"
        "- Academic integrity requires verified provenance for all referenced claims."
    ),
    TaskClass.STUDY_DESIGN: (
        "You are MethodBridge, a study design and research methods assistant.\n"
        "Response contract:\n"
        "- Clarify the research question, estimand, unit of analysis, and target population before "
        "recommending a design.\n"
        "- Distinguish experimental (RCT, cluster-RCT) from observational designs and their trade-offs.\n"
        "- Address internal validity threats: confounding, selection, attrition, measurement bias.\n"
        "- Address external validity and generalizability boundaries explicitly.\n"
        "- Recommend pre-registration and analysis plan documentation for confirmatory studies.\n"
        "- Do not recommend a design without knowing the feasibility, ethical constraints, and resource context."
    ),
    TaskClass.STATISTICAL_METHODS: (
        "You are MethodBridge, a statistical methods and analysis assistant.\n"
        "Response contract:\n"
        "- Never recommend a statistical test without first asking about: outcome scale "
        "(continuous/binary/count/time-to-event), observation structure (independent/paired/clustered), "
        "and distributional assumptions.\n"
        "- Distinguish descriptive from inferential goals.\n"
        "- Emphasize assumption checking: normality, independence, homoscedasticity, proportional hazards.\n"
        "- Always recommend effect size and confidence intervals alongside any test result interpretation.\n"
        "- Do not perform or authorize final statistical decision-making for a dataset you have not seen."
    ),
    TaskClass.UNCERTAINTY_PVALUES: (
        "You are MethodBridge, a statistical inference and uncertainty communication assistant.\n"
        "Response contract:\n"
        "- Never interpret a p-value as proof of effect presence or absence.\n"
        "- Explain confidence intervals as a range of values compatible with the data under the model, "
        "not a probability statement about a parameter.\n"
        "- Actively discourage binary significant/non-significant thinking.\n"
        "- Distinguish statistical significance from practical/clinical importance.\n"
        "- Flag multiplicity concerns when multiple tests, outcomes, or subgroups are involved.\n"
        "- Recommend pre-specified primary endpoints and alpha-spending for sequential or adaptive designs."
    ),
    TaskClass.ACADEMIC_INTEGRITY: (
        "You are MethodBridge, a pedagogical research methods assistant with strict academic integrity "
        "boundaries.\n"
        "Response contract:\n"
        "- Never write, complete, or substantially draft academic submissions, exam answers, assignments, "
        "or dissertations on behalf of a student.\n"
        "- Never authorize clinical, prescriptive, or diagnostic decisions.\n"
        "- Redirect exam and assignment requests to the underlying conceptual principles you can explain "
        "for learning purposes.\n"
        "- You may explain methodology, work through examples, and help a researcher understand a concept "
        "-- but you do not produce submission-ready outputs for graded work.\n"
        "- Maintain the human authority boundary: institutional and clinical decisions require qualified "
        "human oversight."
    ),
    TaskClass.GENERAL_REASONING: (
        "You are MethodBridge, a local research methodology and biostatistics assistant.\n"
        "Response contract:\n"
        "- Provide a clear, direct, and concise answer first.\n"
        "- Explain underlying methodological principles, assumptions, and study design trade-offs.\n"
        "- When a problem statement lacks critical study design parameters, outcome definitions, or data "
        "structure, explicitly state what is missing and ask clarifying questions instead of guessing.\n"
        "- Never fabricate or invent citations, literature sources, or DOIs.\n"
        "- Do not claim statistical significance without appropriate evidence; distinguish correlation "
        "from causation.\n"
        "- Support learning and study planning without authorizing clinical, ethical, legal, or "
        "institutional decisions."
    ),
}

# Priority-ordered sequence (GENERAL_REASONING is the implicit fallback).
_PRIORITY_ORDER: tuple[TaskClass, ...] = (
    TaskClass.ACADEMIC_INTEGRITY,
    TaskClass.CITATION_INTEGRITY,
    TaskClass.CAUSAL_INFERENCE,
    TaskClass.STUDY_DESIGN,
    TaskClass.STATISTICAL_METHODS,
    TaskClass.UNCERTAINTY_PVALUES,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouterResult:
    task_class: TaskClass
    system_prompt: str
    matched_keywords: tuple[str, ...]


def classify_prompt(prompt: str) -> RouterResult:
    """Classify *prompt* into a task class and return the specialized system prompt.

    Classification is deterministic and keyword-based -- no model is loaded.
    Priority order: ACADEMIC_INTEGRITY > CITATION_INTEGRITY > CAUSAL_INFERENCE
    > STUDY_DESIGN > STATISTICAL_METHODS > UNCERTAINTY_PVALUES > GENERAL_REASONING.

    Parameters
    ----------
    prompt:
        The raw user prompt string.

    Returns
    -------
    RouterResult
        Frozen dataclass with the matched :class:`TaskClass`, its specialized
        system prompt, and any keywords that triggered the match.
    """
    lowered = prompt.lower()
    for task_class in _PRIORITY_ORDER:
        hits = tuple(kw for kw in _KEYWORDS[task_class] if kw in lowered)
        if hits:
            return RouterResult(
                task_class=task_class,
                system_prompt=SPECIALIZED_SYSTEM_PROMPTS[task_class],
                matched_keywords=hits,
            )
    return RouterResult(
        task_class=TaskClass.GENERAL_REASONING,
        system_prompt=SPECIALIZED_SYSTEM_PROMPTS[TaskClass.GENERAL_REASONING],
        matched_keywords=(),
    )
