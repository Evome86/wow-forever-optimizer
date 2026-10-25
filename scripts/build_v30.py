#!/usr/bin/env python3
"""v3.0: bilingual ID-keyed export and evidence-only quest-semantics triage.
Never turns candidate quests into verified playable quests.
"""
import argparse,collections,csv,json,re
from pathlib import Path
from audit_localization_v29 import build
PIN='5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
FIELDS=('preQuestSingle','preQuestGroup','requiredRaces','availableStartingWith','availableUntilCompleted','disabledByQuest')
PRIORITY=('src/derived/requiredRaces.lua','src/meta/questMeta.lua','src/types/Quest.t.lua','src/types/Meta.t.lua')
def refs(value):
 if isinstance(value,dict):return sorted({x for x in value.values() if type(x)==int and x>0})
 if isinstance(value,list):return sorted({x for x in value if type(x)==int and x>0})
 return []
def audit(source,quest_path):
 native=json.loads(quest_path.read_text(encoding='utf8'))
 if native.get('upstream_commit')!=PIN or len(native.get('quests',{}))<5000:raise ValueError('native source/version incomplete')
 loc,rows=build(source,quest_path)
 names={str(r['quest_id']):r for r in rows}
 quests=native['quests']
 bilingual=[];counts=collections.Counter(); missing=[];focus=[]
 for qid,quest in sorted(quests.items(),key=lambda pair:int(pair[0])):
  row=names[qid];level=quest.get('requiredLevel')
  entry={'id':int(qid),'names':{'enUS':row['enUS'],'deDE':row['deDE'] or None},'name_fallback':'enUS' if not row['deDE'] else None,
         'requiredLevel':level,'questLevel':quest.get('questLevel'),'requiredRaces':quest.get('requiredRaces'),
         'requiredClasses':quest.get('requiredClasses'),'prerequisites':{f:refs(quest.get(f)) for f in ('preQuestSingle','preQuestGroup')},
         'status':'UNVERIFIED_PLAYABILITY'}
  bilingual.append(entry)
  if int(qid)>=90000:counts['forever_90k_total']+=1;counts['forever_90k_de']+=bool(row['deDE'])
  if type(level)==int and level<=30:counts['required_level_le30_total']+=1;counts['required_level_le30_de']+=bool(row['deDE'])
  if int(qid) in (92595,92871,93320,93958,94414,95349):focus.append(entry)
  for f in ('preQuestSingle','preQuestGroup'):
   for ref in refs(quest.get(f)):
    if str(ref) not in quests:missing.append({'quest_id':int(qid),'field':f,'referenced_id':ref})
 evidence={}
 for field in FIELDS:
  hits=[]
  paths=[source/p for p in PRIORITY if (source/p).is_file()]
  paths += sorted((source/'src').rglob('*.lua')) if (source/'src').is_dir() else []
  seen=set()
  for p in paths:
   if p in seen:continue
   seen.add(p)
   # Prioritize consumer logic, not assignment-only corrections.
   if '/corrections/' in p.as_posix():continue
   try:lines=p.read_text(encoding='utf8',errors='replace').splitlines()
   except OSError:continue
   for i,line in enumerate(lines):
    if re.search(r'\b'+re.escape(field)+r'\b',line):
     hits.append({'file':str(p.relative_to(source)),'line':i+1,'context':'\n'.join(f'{j+1}: {lines[j][:220]}' for j in range(max(0,i-4),min(len(lines),i+6)))})
     if len(hits)>=25:break
   if len(hits)>=25:break
  evidence[field]=hits
 report={'version':'3.0','upstream_commit':PIN,'quest_count':len(bilingual),'localization':loc,
         'segments':dict(counts),'focus_quests':focus,'missing_prerequisite_refs':missing[:100],
         'missing_prerequisite_refs_count':len(missing),'consumer_source_evidence':evidence,
         'semantic_proof':'SOURCE_SNIPPETS_ONLY','semantics_verified':False,'playable_quests_verified':False,
         'route_eligibility_gate':'BLOCKED_SEMANTICS_AND_INGAME_VALIDATION',
         'next_steps':['Inspect runtime consumers of race masks and prerequisite arrays','Verify ambiguous quest availability in game','Measure XP and travel/combat times']}
 return report,bilingual

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-dir',default='vendor/QuestieDB');ap.add_argument('--quests',default='reports/forever-native-quests-v23.json');ap.add_argument('--output-dir',default='reports');a=ap.parse_args()
 report,quests=audit(Path(a.source_dir),Path(a.quests));out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 (out/'forever-v30-diagnostics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (out/'forever-v30-bilingual-quests.json').write_text(json.dumps({'version':'3.0','upstream_commit':PIN,'quests':quests},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('v3.0',report['quest_count'],report['segments'],report['route_eligibility_gate'])
if __name__=='__main__':main()
