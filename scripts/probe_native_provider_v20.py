#!/usr/bin/env python3
"""Discover exact upstream QuestieDB runtime provider APIs; fail closed for effective values."""
import hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
UP=ROOT/'vendor/QuestieDB'
COMMIT='5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
IDS=(94414,92595,92871,93836)
KEYWORDS=re.compile(r'GetQuest|GetRawQuest|GetQuestData|QuestieDB\.Quest|QuestieDB\.Query|QuestieDB\.Get|LoadDynamic|LoadStatic|static.*Load|dynamic.*Load|GetData|source.*provider|provider.*source',re.I)
DEF=re.compile(r'^\s*(?:(?:local\s+)?function\s+|[\w.:]+\s*=\s*function\s*\()')

def scan(root,limit=450):
    matches=[]; scanned=0
    for p in sorted(root.rglob('*.lua')):
        if any(s in ('.git','node_modules') for s in p.relative_to(root).parts):continue
        scanned+=1
        for n,line in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1):
            if KEYWORDS.search(line):
                matches.append({'path':p.relative_to(root).as_posix(),'line':n,'text':line.strip()[:350], 'function_definition':bool(DEF.match(line))})
    return scanned,matches[:limit],len(matches)

def run():
    out=ROOT/'reports';out.mkdir(exist_ok=True)
    report={'version':'2.0','upstream_commit_expected':COMMIT,'errors':[],
            'effective_quest_values_verified':False,'effective_quests':{},
            'route_eligibility_gate':'BLOCKED_AWAITING_NATIVE_PROVIDER_CALL'}
    try:
        actual=subprocess.run(['git','rev-parse','HEAD'],cwd=UP,capture_output=True,text=True,check=True).stdout.strip()
        report['upstream_commit_actual']=actual
        if actual!=COMMIT:raise RuntimeError('upstream commit mismatch')
        needed=['emulator/native-source.test.lua','src/config.lua','src/corrections/Forever/generated/foreverBaseQuest.lua','src/corrections/Forever/foreverQuestFixes.lua']
        report['required_files_sha256']={}
        for rel in needed:
            data=(UP/rel).read_bytes()
            report['required_files_sha256'][rel]=hashlib.sha256(data).hexdigest()
        count,matches,total=scan(UP)
        report.update({'lua_files_scanned':count,'provider_candidate_total':total,'provider_candidates':matches,'provider_candidates_truncated':total>len(matches)})
        if count==0 or total==0:raise RuntimeError('no upstream Lua/provider candidates found')
        for rel in ['emulator/native-source.test.lua','src/config.lua']:
            data=(UP/rel).read_text(encoding='utf-8',errors='replace').splitlines()
            report.setdefault('upstream_entrypoints',{})[rel]=[{'line':i+1,'text':s[:400]} for i,s in enumerate(data)]
        # The complete entrypoint is necessary to implement the *actual* provider call next.
        proc=subprocess.run(['lua5.1','emulator/native-source.test.lua'],cwd=UP,capture_output=True,text=True,timeout=180)
        (out/'forever-native-v20.log').write_text(proc.stdout+'\n'+proc.stderr,encoding='utf-8')
        report['native_tests']={'exit_code':proc.returncode,'passed':proc.returncode==0}
        if proc.returncode:raise RuntimeError('native-source.test.lua failed')
    except Exception as e:report['errors'].append(f'{type(e).__name__}: {e}')
    report['probe_passed']=not report['errors']
    (out/'forever-provider-probe-v20.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'probe_passed':report['probe_passed'],'errors':report['errors'],'candidate_total':report.get('provider_candidate_total',0),'effective_values_verified':False},indent=2))
    return 0 if report['probe_passed'] else 1
if __name__=='__main__':sys.exit(run())
