# GGUF and quantization

**Status:** accepted for bootstrap; accountable review required before final submission.

## Context

MethodBridge must satisfy an offline, resource-constrained, model-centric evaluation while preserving methodological quality and human authority.

## Options considered

- Requantize sequentially
- Defer the decision or make no change
- The selected bounded option

## Decision

Convert once, then independently produce Q4_K_M, Q5_K_M, and Q6_K.

## Consequences

Supports a fair quality/resource comparison.

## Implementation and evaluation impact

The decision is represented in configuration, scripts, held-out cases, readiness checks, and the model experiment record. A conflicting empirical result or official-rule change reopens this ADR.

## Responsible authority

Final acceptance remains an accountable human decision.
