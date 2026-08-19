# ADTC profiler integration

## Frozen contract

Profiler commit: `ac2e137dca65ea3b09d997774f17dd8907b489fb`  
llama.cpp commit: `0329fcdac8c2477c2dda1d5e43fd2e3616b99655`

The local bake-off must not invent an alternative score. It must:

1. verify the exact model SHA-256 and GGUF header;
2. invoke the pinned official profiler in participant mode;
3. preserve stdout, stderr, return code and machine declaration;
4. retain raw quality responses separately from performance measurements;
5. distinguish local diagnostics from official profiler results;
6. stop on crash, OOM, malformed output, unsupported architecture, or unsafe thermal behavior;
7. rerun the exact finalist from a clean checkout and clean model download.

Audit-mode behavior remains organizer-controlled. Final profiler results are unavailable until local candidate execution.
