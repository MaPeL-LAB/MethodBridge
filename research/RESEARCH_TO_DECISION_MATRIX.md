# Research-to-decision matrix

| Finding | Decision | ADR | Artifact | Verification | Status |
|---|---|---|---|---|---|
| Official path is GGUF + llama.cpp | Reject incompatible candidates | ADR-010 | conversion/runtime scripts | exact load test | specified |
| Public access is not training permission | Source allowlist and record-level licence | ADR-006 | source registry/schema | dataset validator | implemented |
| Hidden prompts require breadth | Retention suite and no public-prompt training | ADR-013 | 60 cases/leakage test | held-out evaluation | implemented |
| 8 GB leaves little headroom | Internal 6 GB target | ADR-012 | inference config | profiler | requires empirical test |

## Recovery note

This document was recreated from the retained Deep Research report and controlling specification; it is not claimed to be byte-identical to the inaccessible original artifact.
