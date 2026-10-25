#!/usr/bin/env python3
"""Capture the actual upstream code around definitions and dependency declarations."""
import json,re,argparse,subprocess
from pathlib import Path
from execute_original_v37 import FUNCTIONS,extract_start
p=argparse.ArgumentParser();p.add_argument('--addon',default='vendor/Questie');p.add_argument('--out',default='reports/forever-v38-source-context.json');a=p.parse_args()
base=Path(a.addon);result={'version':'3.8','source':'upstream Questie addon','functions':{},'dependencies':{}}
for key,(rel,pattern) in FUNCTIONS.items():
 path=base/rel;lines=path.read_text(encoding='utf8',errors='replace').splitlines();start=extract_start(path,pattern)
 result['functions'][key]={'path':str(path),'line':start,'preceding_lines':[{'line':i+1,'text':lines[i]} for i in range(max(0,start-51),start-1)],'function_start':[{'line':i+1,'text':lines[i]} for i in range(start-1,min(len(lines),start+65))]}
for name in ('playerRaceFlagX2','Questie.IsQuestCompleted','Questie.IsQuestFlaggedCompleted','IsPreQuestGroupFulfilled','exclusiveTo'):
 hits=[]
 for path in (base/'Modules/QuestiePlayer.lua',base/'Database/QuestieDB.lua'):
  for i,line in enumerate(path.read_text(encoding='utf8',errors='replace').splitlines()):
   if name in line:hits.append({'path':str(path),'line':i+1,'text':line.strip()})
 result['dependencies'][name]=hits[:60]
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'functions':len(result['functions']),'dependency_groups':len(result['dependencies'])}))
