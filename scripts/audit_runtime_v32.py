#!/usr/bin/env python3
"""Conservative source evidence collector: does not certify in-game eligibility."""
import argparse, collections, json, re
from pathlib import Path

TERMS = {
 'skyborne':r'(?i)skyborne|sky.borne',
 'race_keys':r'(?i)raceKeys|ALL_HORDE|ALL_ALLIANCE|raceMask|raceID|raceId',
 'prerequisites':r'preQuestSingle|preQuestGroup|availableStartingWith|availableUntilCompleted|disabledByQuest',
 'runtime_consumers':r'(?i)IsQuestAvailable|IsQuestValid|QuestAvailable|CheckPrereq|HasCompletedQuest|IsQuestCompleted',
}
EXCLUDE={'locales','l10n','translations','tests','test','node_modules','.git'}

def scan(root, max_hits=80):
 result={}; scanned=0
 for key, pattern in TERMS.items():
  matches=[]; rx=re.compile(pattern)
  for path in sorted(root.rglob('*')):
   if not path.is_file() or path.suffix.lower() not in ('.lua','.toc','.xml'):continue
   if any(x.lower() in EXCLUDE for x in path.relative_to(root).parts):continue
   if path.stat().st_size>2_000_000:continue
   if key==list(TERMS)[0]:scanned+=1
   try: lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
   except OSError:continue
   for n,line in enumerate(lines,1):
    if rx.search(line):
     if len(matches)<max_hits:
      matches.append({'file':str(path.relative_to(root)),'line':n,'snippet':line.strip()[:300], 'context':'\n'.join(f'{i+1}: {lines[i][:240]}' for i in range(max(0,n-3),min(len(lines),n+2)))})
  result[key]={'sample_count':len(matches),'truncated_at':max_hits,'matches':matches}
 return scanned,result

def build(quests, sources):
 buckets=collections.Counter();examples=[]
 for sid,q in quests.items():
  if int(sid)<90000:continue
  mask=q.get('requiredRaces'); cls=q.get('requiredClasses');
  buckets['total']+=1
  buckets['race_mask_zero_or_missing' if mask in (None,0) else 'race_mask_nonzero']+=1
  buckets['class_mask_zero_or_missing' if cls in (None,0) else 'class_mask_nonzero']+=1
  if len(examples)<25:examples.append({'quest_id':int(sid),'name':q.get('name'),'requiredRaces':mask,'requiredClasses':cls,'requiredLevel':q.get('requiredLevel'),'questLevel':q.get('questLevel')})
 return {'version':'3.2','scope':'source-level triage only','forever_90k_mask_counts':dict(buckets),'forever_90k_examples':examples,'source_evidence':sources,'skyborne_race_bit':'UNVERIFIED','prerequisite_runtime_semantics':'UNVERIFIED','in_game_playability':'UNVERIFIED','route_gate':'BLOCKED','validation_requirements':['Locate authoritative Skyborne race ID and mask definition, not merely mentions','Inspect actual runtime consumers and verify AND/OR behavior','Cross-check selected quest chains with in-game quest log and NPCs','Gather quest XP and movement/combat timings']}

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',default='vendor/QuestieDB');p.add_argument('--quests',default='reports/forever-native-quests-v23.json');p.add_argument('--output',default='reports/forever-v32-runtime-evidence.json');a=p.parse_args()
 root=Path(a.source_dir);raw=json.loads(Path(a.quests).read_text(encoding='utf-8'))
 if not root.is_dir():raise SystemExit('Missing QuestieDB source directory')
 count,sources=scan(root);report=build(raw['quests'],sources);report['files_scanned']=count;report['upstream_commit']=raw.get('upstream_commit')
 output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('v3.2 source evidence ready:',count,'files; route remains BLOCKED')
if __name__=='__main__':main()
