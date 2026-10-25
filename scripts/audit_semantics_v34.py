#!/usr/bin/env python3
"""Targeted source-path inventory. Never equate matching code with proven in-game eligibility."""
import argparse,json,re,subprocess
from pathlib import Path

TARGETS={
 "race_masks": [r"SKYBORNE_HORDE",r"SKYBORNE_ALLIANCE",r"requiredRaces",r"bit\.band",r"bit32\.band",r"bitAnd"],
 "prerequisites": [r"preQuestSingle",r"preQuestGroup",r"IsQuestFlaggedCompleted",r"IsQuestCompleted",r"GetQuestCompletion",r"completedQuests"],
}
SKIP={".git","tests","test","node_modules","locales","translations","l10n",".types"}
def scan(root,limit=120):
 if not root.is_dir():return {"present":False,"matches":[],"files_scanned":0}
 hits=[];count=0
 for f in sorted(root.rglob("*")):
  if not f.is_file() or f.suffix.lower() not in (".lua",".toc",".xml"):continue
  if any(s.lower() in SKIP for s in f.relative_to(root).parts):continue
  if f.stat().st_size>2000000:continue
  count+=1;lines=f.read_text(encoding="utf-8",errors="replace").splitlines()
  for i,line in enumerate(lines):
   categories=[k for k,ps in TARGETS.items() if any(re.search(p,line,re.I) for p in ps)]
   if not categories:continue
   # Rank executable checks and consumer calls above metadata and data records.
   score=(8 if re.search(r"(?:if|elseif|return|function|local|and|or|band\s*\()",line) else 0)+(5 if "QuestieQuest" in str(f) or "QuestiePlayer" in str(f) else 0)-(6 if "/data/" in str(f).lower() or "/generated/" in str(f).lower() else 0)
   hits.append({"file":str(f.relative_to(root)),"line":i+1,"categories":categories,"score":score,"text":line.strip()[:350],"context":"\n".join(f"{j+1}: {lines[j][:240]}" for j in range(max(0,i-7),min(len(lines),i+8)))})
 hits.sort(key=lambda h:(-h["score"],h["file"],h["line"]))
 return {"present":True,"files_scanned":count,"total_matching_lines":len(hits),"selected_excerpts":hits[:limit],"selected_count":min(len(hits),limit)}
def build(db,addon):
 result={"version":"3.4","scope":"targeted runtime code paths and test fixtures; not in-game verification","sources":{"questiedb":scan(db),"questie_addon":scan(addon)},"verified":{"skyborne_mask_constants":False,"race_mask_runtime_behavior":False,"prerequisite_runtime_behavior":False,"horde_skyborne_druid_playability":False},"route_gate":"BLOCKED","manual_verification_protocol":["Confirm checked-out addon is the actual Forever build and pin its commit","Inspect selected source excerpts and follow function calls to all consumers","Execute isolated runtime tests with Horde Skyborne race ID 96 and masks 8589934592, 4294967296, 0, combined masks","Execute prerequisite tests for zero, one, multiple alternative singles, multiple grouped prerequisites, and both fields populated","Compare test outcomes to actual in-game Questie and quest log; record quest IDs and screenshots","Only promote proven rules to the route engine; measure XP and travel before ranking"]}
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--db",default="vendor/QuestieDB");ap.add_argument("--addon",default="vendor/Questie");ap.add_argument("--output",default="reports/forever-v34-runtime-codepaths.json");a=ap.parse_args()
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(build(Path(a.db),Path(a.addon)),indent=2,ensure_ascii=False)+"\n",encoding="utf-8");print("v3.4 targeted evidence written",out)
if __name__=="__main__":main()
