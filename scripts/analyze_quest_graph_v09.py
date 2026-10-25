#!/usr/bin/env python3
"""v0.9: empirical quest-reference topology; field meanings NOT assumed."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

FIELDS = ("12", "13", "14", "15", "16")
def analyze(quest_data, filter_data):
    quests = quest_data["quests"]
    candidates = {int(q["id"]) for q in filter_data["quest_candidates"]}
    ids = {int(k) for k in quests}
    if quest_data.get("source_sha256") != filter_data.get("source_sha256"):
        raise ValueError("Quest import and character filter use different source hashes")
    field_counts = {}
    candidate_edges = []
    external_edges = []
    missing_edges = []
    all_edges = defaultdict(set)
    by_field = {}
    for field in FIELDS:
        counts = Counter()
        examples = {"candidate_to_candidate": [], "candidate_to_excluded": [],
                    "excluded_to_candidate": [], "missing_target": []}
        for sid_text, quest in quests.items():
            sid = int(sid_text)
            raw = (quest.get("prerequisites_raw") or {}).get(field)
            if raw is None:
                continue
            if not isinstance(raw, list):
                raise ValueError(f"Non-list field {field} on quest {sid}")
            counts["quests_with_field"] += 1
            for target in raw:
                counts["entries"] += 1
                if not isinstance(target, int) or isinstance(target, bool) or target <= 0:
                    counts["invalid_reference_values"] += 1
                    continue
                counts["valid_positive_ids"] += 1
                if target not in ids:
                    counts["missing_target"] += 1
                    if len(examples["missing_target"]) < 15:
                        examples["missing_target"].append([sid, target])
                    missing_edges.append([sid, target, int(field)])
                    continue
                all_edges[sid].add(target)
                src_c, dst_c = sid in candidates, target in candidates
                label = ("candidate" if src_c else "excluded") + "_to_" + ("candidate" if dst_c else "excluded")
                counts[label] += 1
                if label in examples and len(examples[label]) < 15:
                    examples[label].append([sid, target])
                if src_c and dst_c:
                    candidate_edges.append([sid, target, int(field)])
                elif src_c != dst_c:
                    external_edges.append([sid, target, int(field)])
        by_field["field_"+field] = {"counts": dict(counts), "examples": examples}
    # Find reciprocal references without interpreting their meaning.
    reciprocal = []
    for src, targets in all_edges.items():
        for target in targets:
            if src < target and src in all_edges.get(target, set()):
                reciprocal.append([src, target])
    # Connected components on the undirected candidate-only reference graph.
    adjacency = {cid: set() for cid in candidates}
    for a,b,_ in candidate_edges:
        adjacency[a].add(b); adjacency[b].add(a)
    seen = set(); components = []
    for cid in sorted(candidates):
        if cid in seen: continue
        stack=[cid]; seen.add(cid); group=[]
        while stack:
            cur=stack.pop(); group.append(cur)
            for nxt in adjacency[cur]-seen:
                seen.add(nxt); stack.append(nxt)
        components.append(sorted(group))
    components.sort(key=lambda g:(-len(g),g[0]))
    return {
        "schema_version":1, "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":quest_data.get("source_sha256"),
        "total_quests":len(quests), "candidate_count":len(candidates),
        "field_reference_analysis":by_field,
        "candidate_reference_edge_count":len(candidate_edges),
        "candidate_to_other_or_other_to_candidate_edge_count":len(external_edges),
        "missing_reference_edge_count":len(missing_edges),
        "reciprocal_reference_pairs_count":len(reciprocal),
        "reciprocal_reference_pairs_sample":reciprocal[:50],
        "candidate_components_count":len(components),
        "candidate_component_sizes_top_30":[len(c) for c in components[:30]],
        "largest_candidate_components":[{"size":len(c),"quest_ids":c[:100],
            "truncated":len(c)>100} for c in components[:15]],
        "candidate_edges_sample":candidate_edges[:150],
        "cross_boundary_edges_sample":external_edges[:150],
        "missing_edges_sample":missing_edges[:100],
        "interpretation":{
            "fields_12_to_16":"UNVERIFIED semantics: these are raw references, not proven prerequisite edges",
            "components":"Undirected raw-reference connectivity, NOT ordered quest chains",
            "cross_boundary":"Excluded from preliminary character filter, NOT necessarily impossible prerequisite",
            "next_step":"Validate field semantics against upstream decoder/runtime and in-game behavior"},
        "release_gate":"BLOCKED: no verified prerequisite direction, alternative logic, XP, availability or route"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--quests",type=Path,default=Path("reports/forever-quests.json"))
    p.add_argument("--filter",type=Path,default=Path("reports/forever-skyborne-v08.json"))
    p.add_argument("--output",type=Path,default=Path("reports/forever-quest-graph-v09.json"))
    a=p.parse_args()
    result=analyze(json.loads(a.quests.read_text()),json.loads(a.filter.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("Candidates:",result["candidate_count"],"components:",result["candidate_components_count"])
    print(result["release_gate"])
if __name__=="__main__":main()
