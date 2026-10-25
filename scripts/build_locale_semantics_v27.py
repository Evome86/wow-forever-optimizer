#!/usr/bin/env python3
"""Coverage audit; deliberately does not infer in-game eligibility from source matches."""
import argparse, json, re, csv
from pathlib import Path

QUEST_ENTRY=re.compile(r'\[\s*(\d+)\s*\]\s*=\s*(["\'])((?:\\.|(?!\2).)*)\2\s*[,;]?', re.S)
ESCAPE=re.compile(r'\\([\\"\'nrt])')
KEYWORDS=('preQuestSingle','preQuestGroup','requiredRaces','availableStartingWith','availableUntilCompleted','disabledByQuest')

def unescape(value):
 return ESCAPE.sub(lambda m:{'n':'\n','r':'\r','t':'\t'}.get(m[1],m[1]),value)

def parse_lookup(path):
 if not path.is_file():return {},{'present':False,'parsed_entries':0,'duplicate_ids':0}
 raw=path.read_text(encoding='utf-8-sig',errors='replace'); result={};dupes=0
 for m in QUEST_ENTRY.finditer(raw):
  key=str(int(m[1]));value=unescape(m[3]);dupes+=key in result;result[key]=value
 return result,{'present':True,'parsed_entries':len(result),'duplicate_ids':dupes,'bytes':path.stat().st_size}

def evidence(root):
 hits={k:[] for k in KEYWORDS}
 # Prefer implementation files over huge generated data / lookup tables.
 for file in sorted(root.rglob('*.lua')):
  rel=file.relative_to(root).as_posix()
  if any(x in rel for x in ('/lookup','/generated/','/data/','QuestDB.lua','QuestDB/')):continue
  try: lines=file.read_text(encoding='utf-8',errors='replace').splitlines()
  except OSError:continue
  for i,line in enumerate(lines):
   for key in KEYWORDS:
    if key in line and len(hits[key])<25:
     hits[key].append({'file':rel,'line':i+1,'context':'\n'.join(f'{j+1}: {lines[j][:240]}' for j in range(max(0,i-3),min(len(lines),i+4)))})
 return hits

def build(source,quest_file):
 payload=json.loads(quest_file.read_text(encoding='utf-8'));quests=payload['quests'];ids=set(quests)
 de,de_info=parse_lookup(source/'l10n/Forever/lookupQuests/deDE.lua')
 en,en_info=parse_lookup(source/'l10n/Forever/lookupQuests/enUS.lua')
 rows=[];missing=[];matched=0; native_english=0
 for qid in sorted(ids,key=int):
  q=quests[qid]; english=q.get('name') if isinstance(q.get('name'),str) else ''
  german=de.get(qid,''); matched+=bool(german);native_english+=bool(english)
  if not german:missing.append({'id':int(qid),'english':english})
  rows.append({'quest_id':qid,'native_en_name':english,'locale_en_name':en.get(qid,''),'locale_de_name':german,'de_present':int(bool(german)),'required_races':q.get('requiredRaces'),'pre_quest_single':json.dumps(q.get('preQuestSingle'),ensure_ascii=False),'pre_quest_group':json.dumps(q.get('preQuestGroup'),ensure_ascii=False)})
 coverage={'version':'2.7','upstream_commit':payload.get('upstream_commit'),'quest_count':len(ids),'native_english_names':native_english,'german_names_matched':matched,'german_names_missing':len(ids)-matched,'german_coverage_percent':round(100*matched/len(ids),2) if ids else 0,'locale_files':{'deDE':de_info,'enUS':en_info},'locale_entry_sample':[{ 'id':int(k),'de':de[k],'native_en':quests[k].get('name','')} for k in sorted(ids & set(de),key=int)[:20]],'missing_german_sample':missing[:60], 'localization_note':'Source lookup coverage, not proof that game client displays these strings; unparsed localization expressions are not counted.', 'semantics_verified':False,'playable_quests_verified':False,'route_eligibility_gate':'BLOCKED_SEMANTICS_AND_INGAME_VALIDATION','semantics_note':'Evidence excerpts are not executable proof of AND/OR, zero-mask, or client availability. No candidate promoted to playable.', 'source_semantics_evidence':evidence(source)}
 return coverage,rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',default='vendor/QuestieDB');p.add_argument('--quests',default='reports/forever-native-quests-v23.json');p.add_argument('--output-dir',default='reports');a=p.parse_args()
 root=Path(a.source_dir);q=Path(a.quests);assert root.is_dir(),root;assert q.is_file(),q
 report,rows=build(root,q);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 (out/'forever-locale-semantics-v27.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with (out/'forever-quest-names-v27.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(f"v2.7: {report['german_names_matched']}/{report['quest_count']} German quest names ({report['german_coverage_percent']}%). Gate: {report['route_eligibility_gate']}")
if __name__=='__main__':main()
