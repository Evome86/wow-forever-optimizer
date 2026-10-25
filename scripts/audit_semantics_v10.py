#!/usr/bin/env python3
"""v1.0: source evidence + boundary audit; never invent prerequisite semantics."""
import argparse, hashlib, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

KEYWORDS = re.compile(r'pre.?requisite|pre.?quest|next.?quest|exclusive|breadcrumb|quest.?chain|quest.?meta|quest.?field|quest.?dependency', re.I)
def source_evidence(vendor, max_hits=160):
    roots = [vendor/"src", vendor/"data"/"Forever", vendor/"support"/"Forever"]
    hits=[]; files_scanned=0; skipped=0
    for base in roots:
        if not base.exists(): continue
        for path in sorted(base.rglob("*.lua")):
            if path.stat().st_size > 3_000_000:
                skipped+=1; continue
            files_scanned+=1
            lines=path.read_text(encoding="utf-8",errors="replace").splitlines()
            for i,line in enumerate(lines):
                if KEYWORDS.search(line):
                    if len(hits)<max_hits:
                        hits.append({"path":str(path.relative_to(vendor)), "line":i+1,
                                     "text":line.strip()[:240],
                                     "context":[s.strip()[:240] for s in lines[max(0,i-2):min(len(lines),i+3)]]})
    meta=vendor/"src/meta/questMeta.lua"
    return {"scan_roots":[str(p.relative_to(vendor)) for p in roots],
            "lua_files_scanned":files_scanned,"large_files_skipped":skipped,
            "keyword_hit_sample":hits,"keyword_hit_sample_truncated":len(hits)>=max_hits,
            "quest_meta_present":meta.is_file(),
            "quest_meta_sha256":hashlib.sha256(meta.read_bytes()).hexdigest() if meta.is_file() else None}

def analyze(quests, character, graph, vendor):
    q=quests["quests"]
    for other in (character,graph):
        if other.get("source_sha256") != quests.get("source_sha256"):
            raise ValueError("Input source hashes differ")
    candidates={int(x["id"]) for x in character["quest_candidates"]}
    excluded={int(k) for k in q}-candidates
    edges=[]; field_summary=Counter(); boundary=Counter()
    all_ids={int(k) for k in q}
    for sid_text,item in q.items():
        sid=int(sid_text)
        for field,targets in (item.get("prerequisites_raw") or {}).items():
            for target in targets or []:
                if not isinstance(target,int) or isinstance(target,bool) or target<=0: continue
                if target not in all_ids: continue
                if (sid in candidates)!=(target in candidates):
                    direction="candidate_to_excluded" if sid in candidates else "excluded_to_candidate"
                    boundary[(field,direction)]+=1
                    edges.append({"source":sid,"target":target,"raw_field":field,
                                  "direction":direction,
                                  "source_name":q[str(sid)].get("name"),
                                  "target_name":q[str(target)].get("name"),
                                  "source_required_level":q[str(sid)].get("required_level"),
                                  "target_required_level":q[str(target)].get("required_level")})
                    field_summary[field]+=1
    evidence=source_evidence(vendor)
    return {"schema_version":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "source_sha256":quests["source_sha256"],"quest_count":len(q),
            "candidate_count":len(candidates),"excluded_count":len(excluded),
            "cross_boundary_reference_count":len(edges),
            "cross_boundary_by_field_and_direction":[{"field":k[0],"direction":k[1],"count":v}
                for k,v in sorted(boundary.items())],
            "cross_boundary_edges":edges,
            "source_evidence":evidence,
            "semantics_verification":{"raw_fields_12_to_16":"UNVERIFIED",
                "evidence_policy":"Keyword matches are source pointers, NOT proof of field meaning.",
                "next_manual_check":"Review upstream definitions AND runtime consumers; document exact lines and interpretation before enabling directed edges."},
            "release_gate":"BLOCKED: prerequisite semantics, direction and alternative logic not verified"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--quests",type=Path,default=Path("reports/forever-quests.json"))
    p.add_argument("--filter",type=Path,default=Path("reports/forever-skyborne-v08.json"))
    p.add_argument("--graph",type=Path,default=Path("reports/forever-quest-graph-v09.json"))
    p.add_argument("--vendor",type=Path,default=Path("vendor/QuestieDB"))
    p.add_argument("--output",type=Path,default=Path("reports/forever-semantics-v10.json"))
    a=p.parse_args()
    data=analyze(json.loads(a.quests.read_text()),json.loads(a.filter.read_text()),
                 json.loads(a.graph.read_text()),a.vendor)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print("Cross-boundary references:",data["cross_boundary_reference_count"])
    print(data["release_gate"])
if __name__=="__main__":main()
