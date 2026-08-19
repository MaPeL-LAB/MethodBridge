#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
SHA=re.compile(r"^[0-9a-f]{40}$")
def main() -> int:
    errors=[]
    lock=json.loads((ROOT/"governance/upstream.lock.json").read_text())
    names=set()
    for item in lock.get("upstreams", []):
        if item.get("name") in names: errors.append(f"duplicate upstream: {item.get('name')}")
        names.add(item.get("name"))
        if not SHA.fullmatch(str(item.get("commit", ""))): errors.append(f"invalid upstream commit: {item.get('name')}")
        if item.get("status") not in {"frozen", "frozen_for_bakeoff", "frozen_for_reproduction"}: errors.append(f"unreviewed upstream status: {item.get('name')}")
    policy=yaml.safe_load((ROOT/"config/model_candidate_policy.yml").read_text())
    cfg=yaml.safe_load((ROOT/"config/base_model_candidates.yml").read_text())
    ids=set(); priorities=set(); admitted=set(policy["bakeoff_admitted_states"])
    for c in cfg.get("candidates", []):
        cid=c.get("id")
        if cid in ids: errors.append(f"duplicate candidate: {cid}")
        ids.add(cid)
        if c.get("priority") in priorities: errors.append(f"duplicate priority: {c.get('priority')}")
        priorities.add(c.get("priority"))
        if not SHA.fullmatch(str(c.get("revision", ""))): errors.append(f"candidate lacks exact revision: {cid}")
        if c.get("license") not in policy["allowed_licenses"]: errors.append(f"unreviewed licence: {cid}")
        if c.get("access") != "public_no_credentials": errors.append(f"candidate is not public without credentials: {cid}")
        if c.get("admission") not in policy["admission_states"]: errors.append(f"invalid admission: {cid}")
        if c.get("admission") == "documentary_watch" and c.get("priority", 0) <= 5: errors.append(f"watch candidate incorrectly prioritized: {cid}")
    if len(cfg.get("candidates", [])) < 5: errors.append("fewer than five candidates")
    if not any(c.get("admission") == "documentary_watch" for c in cfg["candidates"]): errors.append("no architecture-watch candidate")
    if not any(c.get("admission") in admitted for c in cfg["candidates"]): errors.append("no admitted empirical candidates")
    profiler=json.loads((ROOT/"config/adtc_profiler.lock.json").read_text())
    expected=next(x["commit"] for x in lock["upstreams"] if x["name"]=="ADTC profiler")
    if profiler.get("commit") != expected: errors.append("profiler lock differs from upstream lock")
    if errors:
        print("Upstream and candidate validation: FAIL")
        for e in errors: print(f"- {e}")
        return 1
    print("Upstream and candidate validation: PASS")
    print(f"Upstreams: {len(lock['upstreams'])}")
    print(f"Candidates: {len(cfg['candidates'])}")
    print("Empirical admissions: " + ", ".join(c['id'] for c in cfg['candidates'] if c['admission'] in admitted))
    return 0
if __name__=="__main__": sys.exit(main())
