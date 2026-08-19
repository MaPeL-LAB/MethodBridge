# Base-model selection

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Choose the newest model immediately
- Start with 7B
- The selected bounded option

## Decision

Run a five-model empirical bake-off; do not declare a documentary winner.

## Consequences

Same-device evidence replaces assumptions.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
