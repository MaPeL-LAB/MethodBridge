# Official evaluation contract

**Status:** frozen for pre-local engineering; final rules recheck still mandatory.

The submission-critical path is:

```text
public credential-free model download
        ↓
exact GGUF at metadata runtime path
        ↓
pinned llama.cpp load
        ↓
two declared public prompts + organizer hidden prompts
        ↓
quality, throughput, memory, crash, and thermal assessment
```

MethodBridge may use richer development tooling, but the scored artifact must stand alone in the official offline runtime. Retrieval, cloud APIs, private services, and alternate inference engines cannot be required for judged answers.

No unmeasured value may enter `REPORT.md` or `metadata.json`. Any official rules, schema, or profiler change reopens this contract.
