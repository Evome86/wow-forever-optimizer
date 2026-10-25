#!/usr/bin/env python3
"""Evidence-only source-context and localization inventory; no guessed translations."""
import argparse, json, re
from pathlib import Path

PATTERNS={
 'race_zero_mask':r'requiredRaces|factionRaceMasks|raceMask|raceIDs',
 'prerequisite_logic':r'preQuestSingle|preQuestGroup|nextQuestInChain',
 'availability':r'availableStartingWith|availableUntilCompleted|disabledByQuest|breadcrumb',
 'localization':r'locale|localization|deDE|enUS|GetQuestLogTitle|GetQuestInfo|GetTitle',
}
SUFFIXES={'.lua','.py','.md','.toc','.json'}
MAX_MATCHES=90

def audit(root):
 files=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in SUFFIXES and '.git' not in p.parts)
 result={'version':'2.6','source':'pinned QuestieDB repository source','semantics_verified':False,'localized_names_verified':False,'note':'Source excerpts are leads, not executable proof of quest semantics or translated names.','files_scanned':len(files),'topics':{},'locale_inventory':[]}
 for topic,pattern in PATTERNS.items():
  rx=re.compile(pattern,re.I)
  matches=[];total=0
  for file in files:
   try: lines=file.read_text(encoding='utf-8',errors='replace').splitlines()
   except OSError:continue
   for idx,line in enumerate(lines):
    if rx.search(line):
     total+=1
     if len(matches)<MAX_MATCHES:
      matches.append({'file':str(file.relative_to(root)),'line':idx+1,'context':[{'line':j+1,'text':lines[j][:300]} for j in range(max(0,idx-5),min(len(lines),idx+6))]})
  result['topics'][topic]={'total_matches':total,'samples':matches,'truncated':total>len(matches)}
 for file in files:
  rel=str(file.relative_to(root))
  if re.search(r'locale|localiz|translat|deDE|enUS',rel,re.I):
   result['locale_inventory'].append({'file':rel,'bytes':file.stat().st_size})
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source-dir',default='vendor/QuestieDB');parser.add_argument('--output',default='reports/forever-semantics-locale-v26.json');args=parser.parse_args()
 root=Path(args.source_dir);assert root.is_dir(),f'Missing pinned source: {root}'
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 data=audit(root);out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('v2.6 source files:',data['files_scanned'],'locale paths:',len(data['locale_inventory']))
 for k,v in data['topics'].items():print(k,v['total_matches'])
if __name__=='__main__':main()
