# Decision log

| Date | Decision | Status | Authority |
|---|---|---|---|
| 2026-08-18 | Continue MethodBridge Local as a conditional ADTC candidate | proposed | human confirmation required |
| 2026-08-18 | Use Math & Scientific Reasoning with education pairing | bootstrap accepted | final recheck required |
| 2026-08-18 | Defer retrieval and African-language claim | bootstrap accepted | review after Gate 1 |
| 2026-08-18 | Run empirical bake-off before tuning | bootstrap accepted | technical evidence required |
| 2026-08-19 | Approve the current MethodBridge Theory of Change for governed ADTC development | approved with conditions | Marothi Peter Letsoalo |
| 2026-08-19 | Restore the fail-closed model evidence boundary and withdraw unsupported model claims | approved correction | Marothi Peter Letsoalo |
| 2026-08-20 | Authorize narrowly scoped private product R&D while contest eligibility remains unresolved | approved with conditions | Marothi Peter Letsoalo |

## GOV-001 — Theory of Change approval

- **Decision:** `approved_with_conditions`
- **Actor:** Marothi Peter Letsoalo
- **Recorded at:** `2026-08-19T06:46:08+02:00`
- **Scope:** MethodBridge Local research, benchmark review, upstream verification,
  candidate comparison, and implementation work within the current ADTC 2026
  MVP boundary.
- **Rationale:** The primary user is sufficiently bounded; the problem remains a
  stated hypothesis rather than an inflated continent-wide claim; the causal
  pathway is plausible and revisable; direct outputs, outcomes, and intended
  impact are separated; the contribution boundary and human-authority limits
  are explicit; and the assumptions, risks, indicators, stopping rules, and
  pinned governance dependency are adequate for governed development.
- **Conditions:** retain the contribution boundary; use only licensed,
  synthetic, or explicitly authorized materials; preserve accountable human
  authority; preserve the held-out evaluation boundary; keep eligibility as a
  separate hard gate; and require separate approval for final model selection,
  quantization, public prompts, release, rules acceptance, and submission.
- **Evidence:** `governance/PROJECT_THEORY_OF_CHANGE.md`,
  `governance/ASSUMPTION_REGISTER.md`, `governance/EVIDENCE_REGISTER.md`,
  `governance/RISK_AND_UNINTENDED_EFFECTS_REGISTER.md`,
  `governance/APPROVAL_BOUNDARIES.md`, `governance/PROTECTED_DECISIONS.md`,
  `governance/upstream.lock.json`, and GitHub issue #4.
- **Not authorized:** entrant eligibility, confidential-data processing,
  production or institutional use, final model release, Challenge Participation
  Agreement acceptance, Devpost submission, or any scientific, ethical,
  clinical, legal, regulatory, or institutional approval.
- **Review trigger:** a material change to the primary user, causal pathway,
  contribution boundary, protected decisions, data boundary, or intended
  deployment reopens GOV-001.

## EVID-001 — Fail-closed model evidence restoration

- **Decision:** `approved_correction`
- **Actor:** Marothi Peter Letsoalo
- **Recorded at:** `2026-08-19T19:56:27+02:00`
- **Scope:** restore truthful evidence classifications; separate simulation from
  real `llama.cpp` execution; withdraw unsupported candidate, performance,
  retention, perplexity, and quantization claims; and reconcile status and
  submission metadata.
- **Rationale:** the prior canned runner loaded no model and populated static or
  process-construction values, so its outputs could not support empirical model
  comparisons. Retaining those claims would conflict with the approved
  evidence, uncertainty, and human-authority boundaries.
- **Decision:** preserve the simulation proxy as an explicit CI test double;
  require digest-bound GGUF execution for real model-output evidence; classify
  the keyword scorer as non-authoritative; require qualified semantic review;
  and reserve official performance evidence for the pinned profiler on a
  qualifying reference host.
- **Withdrawn claims:** the previously reported multi-model pass rates,
  candidate ranking, static RSS/TPS values, perplexity deltas, reasoning
  retention, and Q5_K_M optimum/finalist wording.
- **Not authorized:** final model selection, final quantization, adaptation,
  public hosting, release, challenge-rule acceptance, or submission.
- **Evidence:** GitHub issue #15, ADR-020,
  `docs/MODEL_EVIDENCE_BOUNDARY.md`,
  `config/model_evidence_policy.yml`, and the model-evidence CI tests.
- **Review trigger:** any attempt to use simulation, documentary estimates, or
  automated proxy results as model-selection or submission evidence.

## EXEC-001 — Private product R&D execution authorization

- **Decision:** `approved_with_conditions`
- **Actor:** Marothi Peter Letsoalo
- **Recorded at:** `2026-08-20T12:33:58+02:00`
- **Scope:** continue MethodBridge as private product R&D by acquiring only exact
  reviewed candidate revisions whose licence is approved and whose public access
  requires no credentials; run Docker simulation; and run digest-bound local
  `llama.cpp` inference under the pinned campaign and evidence controls.
- **Rationale:** private product development is independent of contest entry.
  It can generate governed local engineering evidence without representing the
  entrant as eligible or registered and without creating release authority.
- **Conditions:** retain `eligibility_gate: unresolved`; preserve candidate
  licence, access, revision, and admission checks; run network-disabled
  inference; keep weights, raw outputs, private cases, credentials, and local
  paths out of source control; preserve evidence classifications; and stop on
  any campaign stopping condition.
- **Not authorized:** organizer approval; entrant eligibility; finalist or final
  quantization selection; adaptation; official profiler claims; public claims;
  hosting; release; registration; rules or Participation Agreement acceptance;
  submission; confidential-data processing; or production/institutional use.
- **Evidence:** ADR-022, `config/local_model_campaign.yml`,
  `config/model_candidate_policy.yml`, `config/base_model_candidates.yml`,
  `config/model_evidence_policy.yml`, and
  `docs/LOCAL_MODEL_EXECUTION_HANDOFF.md`.
- **Review trigger:** any expansion beyond private local R&D, change to the
  candidate/data/evidence boundary, proposed finalist or quantization decision,
  official claim, public use, hosting, release, registration, rules acceptance,
  or submission.
