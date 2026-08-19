# Hidden-prompt robustness

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Tune only for two public prompts
- Defer the decision or make no change
- The selected bounded option

## Decision

Freeze a broad 60-case suite before training and exclude public prompts from training.

## Consequences

Reduces memorization and benchmark leakage.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
