# ADTC Simulation Limitations

A constrained `linux/amd64` container on Apple Silicon or another non-reference
host is **not** an ADTC Standard Laptop.

The simulation is useful because it can reproduce several hard constraints:

- x86-64 userspace;
- Ubuntu 22.04-compatible environment;
- four-vCPU ceiling;
- 7.5 GiB container memory;
- no network during inference;
- CPU-only `llama.cpp`;
- read-only submission contents;
- bounded process count and writable storage.

It cannot reproduce:

- the reference Intel or AMD CPU microarchitecture;
- native x86 memory bandwidth and caches;
- integrated-GPU memory sharing;
- native scheduler behaviour;
- physical cooling and sustained thermals;
- thermal throttling;
- native generation throughput or time to first token.

Every simulation report must contain:

```json
{
  "measurement_class": "simulation_only",
  "eligible_for_submission_score": false
}
```

A simulation result may reject a candidate early, for example after OOM or a
load failure. It may not prove that a candidate satisfies final performance,
efficiency, or thermal requirements.
