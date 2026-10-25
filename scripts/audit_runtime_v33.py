#!/usr/bin/env python3
"""Questie + QuestieDB evidence inventory. Source excerpts are NOT runtime proof."""
import argparse, collections, json, re, subprocess
from pathlib import Path

PATTERNS={
 'skyborne_definition':r'\bSKYBORNE_(?:HORDE|ALLIANCE)\b',
 'skyborne_race_other':r'(?i)\bskyborne\b',
 'prerequisite_fields':r'\b(?:preQuestSingle|preQuestGroup|availableStartingWith|availableUntilCompleted|disabledByQuest|parentQuest)\b',
 'prerequisite_logic':r'(?i)\b(?:prereq(?:uisite)?|completedQuest|IsQuestCompleted|IsQuestAvailable|questAvailable|questComplete|isAvailable|hasCompletedQuest)\b',
 'race_mask_logic':r'(?i)\b(?:requiredRaces|raceMask|raceIDs|raceID|band|bit\.band|bit32\.band|bitAnd)\b',
}
SUFFIXES={'.lua','.xml','.toc'}
EXCLUDE={'.git','node_modules','tests','test','locales','translations','l10n'}

def scan_repo(root, max_examples=35):
 result={k:{'total_matches':0,'files_with_matches':0,'examples':[]} for k in PATTERNS}
 files=0
 for path in sorted(root.rglob('*')):
  if not path.is_file() or path.suffix.lower() not in SUFFIXES:continue
  if any(p.lower() in EXCLUDE for p in path.relative_to(root).parts):continue
  if path.stat().st_size>2_000_000:continue
  files+=1
  lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
  for key,pat in PATTERNS.items():
   rx=re.compile(pat); matched=[]
   for i,line in enumerate(lines):
    if rx.search(line):matched.append(i)
   if not matched:continue
   result[key]['files_with_matches']+=1
   result[key]['total_matches']+=len(matched)
   for i in matched:
    if len(result[key]['examples'])>=max_examples:break
    result[key]['examples'].append({'file':str(path.relative_to(root)),'line':i+1,'text':lines[i].strip()[:320], 'context':'\n'.join(f'{j+1}: {lines[j][:240]}' for j in range(max(0,i-4),min(len(lines),i+5)))})
 return {'files_scanned':files,'patterns':result}

def as_ids(value):
 if isinstance(value,int):return [value] if value>0 else []
 if isinstance(value,list):return sorted(set(x for v in value for x in as_ids(v)))
 if isinstance(value,dict):return sorted(set(x for v in value.values() for x in as_ids(v)))
 return []

def sample_chains(quests, limit=24):
 candidates=[]
 for sid,q in quests.items():
  if int(sid)<90000:continue
  single=as_ids(q.get('preQuestSingle'));group=as_ids(q.get('preQuestGroup'))
  if not single and not group:continue
  referenced=sorted(set(single+group));missing=[x for x in referenced if str(x) not in quests]
  candidates.append({'id':int(sid),'name':q.get('name'),'requiredLevel':q.get('requiredLevel'), 'questLevel':q.get('questLevel'),'requiredRaces_raw':q.get('requiredRaces'),'requiredClasses_raw':q.get('requiredClasses'),'preQuestSingle_raw':q.get('preQuestSingle'),'preQuestGroup_raw':q.get('preQuestGroup'),'referenced_quests':[{'id':x,'name':quests.get(str(x),{}).get('name'),'in_export':str(x) in quests} for x in referenced],'missing_references':missing,'semantics':'UNVERIFIED','in_game_playability':'UNVERIFIED'})
 candidates.sort(key=lambda x:(x['requiredLevel'] if isinstance(x['requiredLevel'],int) else 999,x['id']))
 return {'candidate_count':len(candidates),'examples':candidates[:limit]}

def rev(root):
 try:return subprocess.run(['git','rev-parse','HEAD'],cwd=root,check=True,capture_output=True,text=True).stdout.strip()
 except (OSError,subprocess.CalledProcessError):return None

def build(quests,db_root,addon_root):
 report={'version':'3.3','scope':'source evidence and test-chain selection, not eligibility certification','repositories':{},'test_quest_chains':sample_chains(quests),'verification':{'skyborne_mask_values':'UNVERIFIED','race_mask_interpretation':'UNVERIFIED','prerequisite_and_or_logic':'UNVERIFIED','in_game_playability':'UNVERIFIED'},'route_gate':'BLOCKED','next_validation':['Review definition and all runtime consumer excerpts in source report','Confirm exact mask values and boolean semantics against runtime execution, not keywords','Verify quest availability and prerequisites on Horde Skyborne Balance Druid in-game','Capture XP, travel time, combat time before optimization']}
 for key,root in [('questiedb',db_root),('questie_addon',addon_root)]:
  if root.is_dir():report['repositories'][key]={'present':True,'commit':rev(root),**scan_repo(root)}
  else:report['repositories'][key]={'present':False,'error':'Source checkout unavailable'}
 return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--quests',default='reports/forever-native-quests-v23.json');p.add_argument('--db',default='vendor/QuestieDB');p.add_argument('--addon',default='vendor/Questie');p.add_argument('--output',default='reports/forever-v33-source-and-chains.json');a=p.parse_args()
 data=json.loads(Path(a.quests).read_text(encoding='utf-8'))
 report=build(data['quests'],Path(a.db),Path(a.addon));out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('v3.3 complete: addon checkout present =',report['repositories']['questie_addon']['present'],'candidate chains =',report['test_quest_chains']['candidate_count'],'gate = BLOCKED')
if __name__=='__main__':main()
