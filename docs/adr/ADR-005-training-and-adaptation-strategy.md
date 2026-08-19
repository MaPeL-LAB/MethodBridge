# Training and adaptation

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Immediate large SFT
- Preference optimization first
- The selected bounded option

## Decision

Prefer prompt-only conditioning; fine-tune only when held-out gaps justify it.

## Consequences

Reduces schedule, forgetting, and licence risk.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
