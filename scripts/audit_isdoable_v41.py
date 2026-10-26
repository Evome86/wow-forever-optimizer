#!/usr/bin/env python3
"""Fail-closed static audit of the complete upstream IsDoable body; no runtime eligibility claims."""
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def audit(path, addon_sha=None, db_sha=None):
    lines=Path(path).read_text(encoding="utf-8",errors="replace").splitlines()
    starts=[i for i,s in enumerate(lines) if re.match(r"^function\s+QuestieDB\.IsDoable\s*\(",s)]
    if len(starts)!=1: raise ValueError("Expected exactly one IsDoable definition")
    start=starts[0]
    # Stop at next top-level declaration. Capture full source, including comments and nested branches.
    end=next((i for i in range(start+1,len(lines)) if re.match(r"^(?:function\s+|local function\s+)",lines[i])),len(lines))
    body=lines[start:end]
    if not any(s.strip()=="end" for s in body): raise ValueError("No end marker in extracted source")
    patterns={
      "completed":r"completedQuests|\.complete\[", "hidden":r"hiddenQuests|charhidden|hidden\[",
      "race":r"requiredRaces|checkRace", "class":r"requiredClasses|checkClass",
      "single":r"preQuestSingle|IsPreQuestSingleFulfilled", "group":r"preQuestGroup|IsPreQuestGroupFulfilled",
      "exclusive":r"exclusiveTo|ExclusiveQuest", "level":r"requiredLevel|questLevel|playerLevel|GetPlayerLevel",
      "questlog":r"currentQuestlog", "event":r"event|Event", "profession":r"profession|Profession",
      "reputation":r"reputation|Reputation", "daily_repeatable":r"daily|Daily|repeatable|Repeatable"
    }
    matches={k:[{'line':start+i+1,'text':s.strip()} for i,s in enumerate(body) if re.search(p,s)] for k,p in patterns.items()}
    calls=sorted(set(re.findall(r"\b(?:QuestieDB|QuestiePlayer|Questie|QuestieCompat)[:.]([A-Za-z_]\w*)\s*\(","\n".join(body))))
    data={'version':'4.1','kind':'static_source_audit_only','addon_commit':addon_sha,'db_commit':db_sha,
      'source_path':str(path),'source_start_line':start+1,'source_end_line':end,
      'source_sha256':hashlib.sha256(("\n".join(body)+"\n").encode()).hexdigest(),
      'source_lines':[{'line':start+i+1,'text':s} for i,s in enumerate(body)],
      'condition_evidence':matches,'referenced_methods':calls,
      'isdoable_executed':False,'eligibility_certified':False,'technical_gate':'BLOCKED_ISDOABLE_NOT_EXECUTED',
      'ingame_gate':'BLOCKED_NOT_VERIFIED','route_gate':'BLOCKED',
      'next':'Map all dependencies, construct controlled scenarios and execute original IsDoable before any eligibility claims.'}
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--addon',default='vendor/Questie');p.add_argument('--out',default='reports/forever-v41-isdoable-audit.json');p.add_argument('--addon-sha');p.add_argument('--db-sha');a=p.parse_args()
    path=Path(a.addon)/'Database/QuestieDB.lua';result=audit(path,a.addon_sha,a.db_sha)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'source_lines':len(result['source_lines']),'methods':len(result['referenced_methods']),'gate':result['technical_gate']}))
if __name__=='__main__':main()
