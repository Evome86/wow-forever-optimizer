#!/usr/bin/env python3
"""Focused source evidence for race constants, patch loader and Skyborne quest 94414.
No Lua execution; evidence only, no eligibility claims.
"""
import argparse, hashlib, json, re
from pathlib import Path

SYMBOLS=('SKYBORNE_HORDE','SKYBORNE_ALLIANCE','ALL_HORDE','ALL_ALLIANCE','NONE')
QUEST_FIELDS=('requiredRaces','preQuestSingle','preQuestGroup','nextQuestInChain','parentQuest','breadcrumbForQuestId','breadcrumbs')
MODULES=('ForeverBaseQuest','ForeverQuestTraces','ForeverQuestFixes')

def snippet(lines, index, radius=5):
    lo=max(0,index-radius); hi=min(len(lines),index+radius+1)
    return {'start_line':lo+1,'end_line':hi,'lines':[{'line':j+1,'text':lines[j][:400]} for j in range(lo,hi)]}

def extract_blocks(text, ids):
    lines=text.splitlines(); found=[]
    for i,line in enumerate(lines):
        m=re.match(r'^\s*\[(\d+)\]\s*=\s*\{',line)
        if not m or int(m[1]) not in ids:continue
        depth=0
        for j in range(i,min(len(lines),i+300)):
            clean=re.sub(r'--[^\n]*','',lines[j]); clean=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','""',clean)
            depth+=clean.count('{')-clean.count('}')
            if depth==0:
                found.append({'quest_id':int(m[1]),'start_line':i+1,'end_line':j+1,'lines':[{'line':k+1,'text':lines[k][:500]} for k in range(i,j+1)]})
                break
    return found

def build(root, prior=None):
    root=Path(root); files={}; errors=[]
    for p in sorted(root.rglob('*.lua')):
        rel=p.relative_to(root).as_posix()
        if any(part in ('.git','__pycache__') for part in p.relative_to(root).parts):continue
        try: s=p.read_text(encoding='utf-8')
        except (UnicodeError,OSError):continue
        files[rel]=s
    if not files:
        raise RuntimeError(f'No Lua sources found in {root.resolve()}; verify QuestieDB checkout')
    # Search relevant code only, never truncate based on unrelated NONE occurrences.
    race=[]; loaders=[]; merge=[]
    for rel,s in files.items():
        lines=s.splitlines()
        relevant_race_file=bool(re.search(r'race|constant|enum|key|mask',rel,re.I))
        for i,line in enumerate(lines):
            if relevant_race_file and re.search(r'\b(?:SKYBORNE_HORDE|SKYBORNE_ALLIANCE|ALL_HORDE|ALL_ALLIANCE)\b',line):
                race.append({'file':rel,'evidence':snippet(lines,i,3),'classification':'reference_or_declaration_not_evaluated'})
            if any(m in line for m in MODULES) or ('foreverQuestFixes' in line or 'foreverBaseQuest' in line):
                if rel not in ('src/corrections/Forever/foreverQuestFixes.lua','src/corrections/Forever/generated/foreverBaseQuest.lua'):
                    loaders.append({'file':rel,'evidence':snippet(lines,i,3)})
            if rel.startswith(('src/','emulator/','tools/')) and re.search(r'\b(?:LoadDynamic|applyCorrection|merge|Merge|correction|overwrite)\b',line) and re.search(r'quest|load|fix|data|merge|correction',rel+' '+line,re.I):
                if len(merge)<160:merge.append({'file':rel,'evidence':snippet(lines,i,2)})
    blocks=[]
    for rel in ('src/corrections/Forever/generated/foreverBaseQuest.lua','src/corrections/Forever/foreverQuestFixes.lua'):
        if rel not in files:errors.append('missing '+rel);continue
        for block in extract_blocks(files[rel],{94414,92595,92871,93836}):
            block['file']=rel
            block['field_lines']=[x for x in block['lines'] if any('questKeys.'+f in x['text'] for f in QUEST_FIELDS)]
            blocks.append(block)
    if errors:
        raise RuntimeError('Missing required QuestieDB files: ' + '; '.join(errors))
    # Exact source locations of symbolic constants; no assumption about values or NONE.
    definitions=[]
    pattern=re.compile(r'\b(?:'+ '|'.join(SYMBOLS)+r')\s*=\s*[^,}\n]+')
    for rel,s in files.items():
        if not re.search(r'race|constant|enum|key|mask',rel,re.I):continue
        lines=s.splitlines()
        for i,line in enumerate(lines):
            if pattern.search(line):definitions.append({'file':rel,'evidence':snippet(lines,i,2)})
    return {'version':'1.7','schema_version':1,'source_commit':'5c094f6e9a264f0dc54e2fde9731a37a97ed197c',
      'source_file_count':len(files),'errors':errors,'race_declaration_candidates':definitions[:150],
      'skyborne_race_symbol_references':race[:200], 'loader_evidence':loaders[:100],
      'merge_and_patch_code_search':merge,'selected_quest_source_blocks':blocks,
      'previous_v16_candidate_count':len((prior or {}).get('candidates',{})),
      'findings_status':{'race_mask':'NOT_EVALUATED','patch_precedence':'NOT_EXECUTED','quest_94414':'CONFLICT_REQUIRES_RUNTIME_TEST','route':'NOT_VERIFIED'},
      'release_gate':'BLOCKED: source evidence only; no executed Lua patch precedence or runtime quest eligibility'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='vendor/QuestieDB');p.add_argument('--previous',default='reports/forever-runtime-evidence-v16.json');p.add_argument('--output',default='reports/forever-runtime-semantics-v17.json');a=p.parse_args()
    prior=json.loads(Path(a.previous).read_text()) if Path(a.previous).exists() else None
    out=build(a.root,prior); dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('Sources:',out['source_file_count'],'Race definitions:',len(out['race_declaration_candidates']),'Loader:',len(out['loader_evidence']),'Quest blocks:',len(out['selected_quest_source_blocks']))
    print(out['release_gate'])
if __name__=='__main__':main()
