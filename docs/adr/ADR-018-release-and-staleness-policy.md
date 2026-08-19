# Release and staleness

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Reuse old profiler results after changes
- Defer the decision or make no change
- The selected bounded option

## Decision

Bind releases to exact model, dataset, toolchain, config, and profiler evidence; material changes make evidence stale.

## Consequences

Prevents outdated evidence from supporting a new candidate.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
