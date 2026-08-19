# Quantization strategy

**Status:** populated bootstrap decision; reverify before final submission.

Produce Q4_K_M, Q5_K_M, and Q6_K independently from the same merged high-precision candidate. Never requantize an already quantized file.

## Verification

The controlling evidence, implementation artifact, acceptance test, and review trigger must be recorded in `research/RESEARCH_TO_DECISION_MATRIX.md`. No unmeasured result may be promoted to fact.
