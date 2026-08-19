# Exact-revision base-model shortlist

## Decision

The pre-local shortlist is frozen for acquisition planning, not final model selection.

| Order | Exact candidate | Admission | Purpose |
|---:|---|---|---|
| 1 | `Qwen/Qwen2.5-1.5B-Instruct@8ee93c2720648b8ffbb4942ceed829eb72978c29` | empirical primary | mature speed and compatibility baseline |
| 2 | `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | empirical primary | compact reasoning candidate |
| 3 | `HuggingFaceTB/SmolLM3-3B@0a27da171a4ef1e26230ac2b43c9dbf037957625` | empirical primary | middle-quality candidate |
| 4 | `microsoft/Phi-4-mini-instruct@cfbefacb99257ffa30c83adab238a50856ac3083` | empirical conditional | reasoning-quality upper boundary |
| 5 | `Qwen/Qwen3-4B-Instruct-2507@f5d253c7173262c9fbfd68aee1eda21bdc375fb5` | empirical conditional | non-thinking upper boundary |
| 6 | `Qwen/Qwen3.5-2B@5a34b97e5d68ab0de17d0df8e8fd30802fd9ec53` | documentary watch | new hybrid-architecture watch; not admitted yet |

Qwen3.5-2B is intentionally deferred despite its attractive scale. Its hybrid multimodal architecture and public llama.cpp issue history create a disproportionate compatibility risk for the fixed offline evaluator. A newer model is not automatically a better hackathon candidate.

No performance ranking is asserted before same-device GGUF evidence exists.
