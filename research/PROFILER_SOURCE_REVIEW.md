# ADTC profiler and official-runtime source review

## Frozen sources

- submission template: `63ddc5422404f8ee112fc74d28e29764acd40a50`
- profiler: `ac2e137dca65ea3b09d997774f17dd8907b489fb`
- llama.cpp: `0329fcdac8c2477c2dda1d5e43fd2e3616b99655`

The profiler is the controlling measurement path, while MethodBridge's own harness provides richer diagnostic evidence. The final comparison must retain raw prompt outputs, timing, TTFT where available, tokens per second, peak/steady memory, temperature/throttling observations, command line, model hash, hardware declaration, and profiler output.

The pinned llama.cpp update includes GGUF reader size guards. This is desirable supply-chain hardening, but it does not prove candidate compatibility.

Immediately before the final run, compare official upstream heads with these pins. Do not silently update. A material difference requires a reviewed ADR or decision-log entry and a repeated compatibility gate.
