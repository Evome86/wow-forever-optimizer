#!/usr/bin/env python3
"""Fail-closed evidence export: native runtime tests + exact correction blocks.

This is deliberately NOT an effective quest-value exporter until a callable
QuestieDB provider has been independently established.
"""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'vendor' / 'QuestieDB'
OUT = ROOT / 'reports'
COMMIT = '5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
IDS = [92595,92596,92646,92840,92850,92860,92871,92947,93089,93090,93320,93737,93738,93746,93835,93836,93958,94369,94411,94413,94414,94946,95349,99260]
PATHS = [
 'src/corrections/Forever/generated/foreverBaseQuest.lua',
 'src/corrections/Forever/traces/foreverQuestTraces.lua',
 'src/corrections/Forever/foreverQuestFixes.lua',
 'data/Forever/foreverQuestDB.lua',
]

def blocks(text, quest_id):
    """Return bounded source snippets for keyed entries; never parse as final values."""
    lines = text.splitlines()
    pat = re.compile(r'(?<!\d)\[\s*' + str(quest_id) + r'\s*\]\s*=')
    found = []
    for n, line in enumerate(lines):
        if pat.search(line):
            start = max(0,n-2)
            end = min(len(lines),n+32)
            found.append({'line':n+1,'excerpt':'\n'.join(lines[start:end]),'excerpt_truncated':end<len(lines)})
    return found

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    result = {'version':'1.9','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source_commit_expected':COMMIT,'quest_ids':IDS,
              'effective_quest_values_verified':False,'effective_quests':{},
              'reason':'Upstream native-source tests verify precedence, not a quest-specific resolved-value export API.',
              'source_evidence':{},'errors':[]}
    try:
        rev=subprocess.run(['git','rev-parse','HEAD'],cwd=SOURCE,capture_output=True,text=True,check=True).stdout.strip()
        result['source_commit_actual']=rev
        if rev!=COMMIT: raise RuntimeError('QuestieDB commit mismatch: '+rev)
        for path in PATHS:
            f=SOURCE/path
            if not f.is_file(): raise FileNotFoundError(str(f))
            data=f.read_bytes()
            text=data.decode('utf-8',errors='replace')
            entries={str(q):blocks(text,q) for q in IDS}
            result['source_evidence'][path]={'sha256':hashlib.sha256(data).hexdigest(),
                'bytes':len(data),'entries':{k:v for k,v in entries.items() if v}}
        proc=subprocess.run(['lua5.1','emulator/native-source.test.lua'],cwd=SOURCE,
                            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',timeout=180)
        (OUT/'forever-native-v19.log').write_text(proc.stdout,encoding='utf-8')
        result['native_runtime_test']={'exit_code':proc.returncode,'passed':proc.returncode==0,
                                       'log_file':'reports/forever-native-v19.log'}
        if proc.returncode: result['errors'].append('Upstream native-source tests failed')
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
    result['evidence_ready']=not result['errors'] and result.get('native_runtime_test',{}).get('passed',False)
    result['route_eligibility_gate']='BLOCKED_NO_EFFECTIVE_QUEST_EXPORT'
    (OUT/'forever-quest-evidence-v19.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'version':result['version'],'evidence_ready':result['evidence_ready'],
                      'effective_quest_values_verified':False,'errors':result['errors'],
                      'quest_ids':len(IDS)},indent=2))
    return 0 if result['evidence_ready'] else 1

if __name__=='__main__':sys.exit(run())
