#!/usr/bin/env python3
"""Strict v3.6 runtime evidence: never label source scanning or Python fixtures as Lua execution."""
import argparse, json, re, subprocess
from pathlib import Path
from verify_v35 import CASES

NAMES=['HasRequiredRace','IsPreQuestSingleFulfilled','IsPreQuestGroupFulfilled']

def find_definitions(root):
    result={n:[] for n in NAMES}
    if not root.exists(): return result
    for p in sorted(root.rglob('*.lua')):
        if any(part in {'.git','tests','test','locales'} for part in p.relative_to(root).parts):continue
        if p.stat().st_size>2_000_000:continue
        for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
            for name in NAMES:
                if re.search(r'\bfunction\s+[\w.:]*\b'+re.escape(name)+r'\s*\(',line):
                    result[name].append({'path':str(p),'line':i,'signature':line.strip()[:300]})
    return result

def build(addon,db):
    definitions={'addon':find_definitions(addon),'db':find_definitions(db)}
    cases=[{'name':name,'python_reference_passed':actual==expected,'lua_original_executed':False,'lua_comparison':'NOT_RUN'} for name,actual,expected in CASES]
    return {'version':'3.6','type':'strict_original_lua_runtime_gate',
            'sources':{'addon_path':str(addon),'db_path':str(db)},'function_definitions':definitions,
            'reference_cases':cases,'original_lua_tests_executed':0,
            'technical_gate':'BLOCKED_ORIGINAL_LUA_NOT_EXECUTED',
            'ingame_gate':'BLOCKED_NOT_VERIFIED',
            'limitations':['Function definition discovery is NOT Lua execution.',
                           'Do not assert parity until actual source functions run with isolated WoW API mocks.',
                           'Addon checkout is not guaranteed to match the Forever client build.',
                           'ExclusiveTo semantics and quest availability remain unverified.']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--addon',default='vendor/Questie');p.add_argument('--db',default='vendor/QuestieDB');p.add_argument('--out',default='reports/forever-v36-lua-runtime.json');a=p.parse_args()
    report=build(Path(a.addon),Path(a.db));out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'definitions':{source:{k:len(v) for k,v in defs.items()} for source,defs in report['function_definitions'].items()},'technical_gate':report['technical_gate']}))
if __name__=='__main__':main()
