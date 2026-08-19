# Agent instructions

Read `GOVERNANCE.md`, `BOOTSTRAP_STATUS.md`, `governance/PROTECTED_DECISIONS.md`, accepted ADRs, and `BUILD_CHECKLIST.md` before editing.

Agents must:

- work on one bounded checklist phase at a time;
- inspect existing schemas and tests before changing code;
- preserve the offline, `llama.cpp`, GGUF, and 8 GB laptop constraints;
- keep held-out evaluation cases out of training data;
- preserve source licence and provenance fields;
- fail closed when model URLs, hashes, credentials, or eligibility facts are missing;
- update status and decision records truthfully;
- stop when an accountable human decision is required.

Agents must never:

- commit GGUF weights, credentials, participant data, confidential materials, or private evaluation cases;
- fabricate benchmarks, licences, approvals, citations, user interviews, or profiler evidence;
- weaken tests to obtain a pass;
- silently broaden the project into a cloud application, multi-agent system, or clinical decision tool;
- describe a smoke model as the MethodBridge candidate;
- mark the repository submission ready without the final GGUF and official profiler evidence.
