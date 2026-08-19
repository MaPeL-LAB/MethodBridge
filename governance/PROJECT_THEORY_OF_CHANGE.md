# Project Theory of Change

**Status:** populated draft. **Human approval not recorded.**

## Problem hypothesis

Some postgraduate students and early-career researchers in African universities
and public research institutions may lack timely, affordable, privacy-compatible
access to research-methods and statistical support. Intermittent connectivity,
cloud cost, institutional restrictions, and limited specialist mentorship may
allow basic design or interpretation problems to persist until late in a
project. The size and distribution of this need remain a user-research question.

## Primary affected group

The initial primary user is a postgraduate student or early-career researcher
who needs immediate methodological guidance on an ordinary laptop. Secondary
users may include lecturers, supervisors, research assistants, junior analysts,
and research-capacity programmes. The MVP is not designed equally for all of
these groups.

## Intervention

MethodBridge Local is a compact, fully offline scientific-reasoning model that
provides structured explanations, critiques, clarification questions,
uncertainty statements, worked examples, and escalation guidance. It is a
learning and decision-support tool, not an approving authority.

## Causal pathway

```text
licensed and traceable sources + compact base model + qualified review
        ↓
curation, benchmark freeze, candidate comparison, and conditional adaptation
        ↓
GGUF quantization and reliable offline llama.cpp execution
        ↓
structured methodological explanations, critiques, and clarification questions
        ↓
users may identify basic design and interpretation problems earlier
        ↓
users may prepare better questions for supervisors and methodologists
        ↓
with accountable human review, some plans and interpretations may become clearer
        ↓
potential contribution to stronger local research-methods capacity
```

## Direct outputs

- methodological explanations and critiques;
- explicit assumptions, missing information, and uncertainty;
- formative questions and worked examples;
- recommendations for qualified human review;
- reproducible model, benchmark, and profiler evidence.

## Intended outcomes and impact

The near-term hypothesis is that users identify basic methodological issues
earlier and engage more effectively with human support. A possible intermediate
outcome is more coherent planning and interpretation after qualified review. The
intended longer-term contribution is stronger local research-methods capacity.
None of these outcomes is established merely because the model exists or is used.

## Contribution boundary

MethodBridge contributes educational and methodological decision support. It
does not prove a study scientifically valid, cause improved research quality by
itself, replace qualified supervision, approve ethics or analysis plans, or
establish that its use produced a social or educational impact.

## Critical assumptions

1. The compact model retains sufficient general scientific reasoning.
2. Training and evaluation sources are authoritative, diverse, traceable, and legally usable.
3. Quantization does not destroy critical reasoning or abstention behaviour.
4. Users understand the model's limitations and retain access to accountable humans.
5. The model can identify insufficient information rather than fabricate an answer.
6. Offline operation is materially useful to the selected users.
7. The hidden ADTC prompts remain within the selected broad domain.

A failure of assumptions 1, 2, 3, or 5 is a model-selection stopping condition.

## Risks and unintended effects

- false confidence and delayed expert consultation;
- incorrect methodological guidance or unsupported causal claims;
- fabricated citations or outdated requirements;
- academic misconduct or deceptive completion of assessed work;
- users entering confidential or participant-level information;
- overfitting to biomedical examples or public test prompts;
- uneven language quality, stereotypes, or superficial African localization;
- catastrophic forgetting after specialization;
- confusing model output, educational outcome, and social impact.

## Human authority

Accountable humans retain authority over eligibility, source admission, dataset
licensing, the final model, tuning, quantization, public prompts, release,
submission, and all scientific, ethical, clinical, legal, regulatory, and
institutional decisions. See `governance/APPROVAL_BOUNDARIES.md` and
`governance/PROTECTED_DECISIONS.md`.

## Initial indicators

### Technical and output indicators

- held-out methodological correctness;
- unsupported causal-claim rate;
- fabricated-citation rate;
- appropriate uncertainty and abstention;
- general-capability retention;
- repeatability, throughput, TTFT, peak RAM, and thermal stability.

### Outcome indicators for later pilots

- proportion of users who identify seeded methodological problems;
- change in question quality before human supervision;
- reviewer-rated understanding rather than answer copying;
- frequency of inappropriate reliance or delayed escalation;
- accessibility and usefulness under intermittent-connectivity conditions.

## Evidence and revision

The current evidence and assumptions are recorded in the repository research and
governance registers. User demand, learning gains, time savings, and research
quality improvements have not been demonstrated. Reopen this Theory of Change
when the primary user, model capability, risk profile, or intended deployment
changes materially.
