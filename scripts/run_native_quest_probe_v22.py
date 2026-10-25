#!/usr/bin/env python3
"""Capture and validate native Source Quest accessor evidence, without inventing values."""
import json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
UP=ROOT/'vendor/QuestieDB'
SHA='5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
IDS={94414,92595,92596,92646,92840,92850,92860,92871,92947,93089,93090,93320,93737,93738,93746,93835,93836,93958,94369,94411,94413,94946,95349,99260}
def parse(text):
    methods=[];values=[];errors=[];meta={}
    for line in text.splitlines():
        parts=line.split('\t')
        if parts[0]=='META' and len(parts)==3:meta[parts[1]]=parts[2]
        elif parts[0]=='METHOD' and len(parts)==3:methods.append({'name':parts[1],'kind':parts[2]})
        elif parts[0]=='VALUE' and len(parts)==5:
            values.append({'quest_id':int(parts[1]),'accessor':parts[2],'type':parts[3],'value_repr':parts[4]})
        elif parts[0]=='ERROR' and len(parts)>=4:errors.append({'quest_id':int(parts[1]),'accessor':parts[2],'message':'\t'.join(parts[3:])})
    return meta,methods,values,errors
def run():
    out=ROOT/'reports';out.mkdir(exist_ok=True)
    report={'version':'2.2','upstream_commit_expected':SHA,'errors':[],'effective_quest_values_verified':False,
            'route_eligibility_gate':'BLOCKED_UNTIL_ACCESSOR_SEMANTICS_VALIDATED','test_quest_ids':sorted(IDS)}
    try:
        sha=subprocess.run(['git','rev-parse','HEAD'],cwd=UP,capture_output=True,text=True,check=True).stdout.strip()
        report['upstream_commit_actual']=sha
        if sha!=SHA:raise RuntimeError('upstream SHA mismatch')
        source=(ROOT/'scripts/native_quest_probe_v22.lua').read_bytes()
        # Run inside upstream cwd, so relative Source TOC paths resolve exactly as native tests.
        probe=UP/'_forever_optimizer_native_probe_v22.lua'
        try:
            probe.write_bytes(source)
            proc=subprocess.run(['lua5.1',probe.name],cwd=UP,capture_output=True,text=True,timeout=180)
        finally:
            probe.unlink(missing_ok=True)
        (out/'forever-native-quest-v22.log').write_text(proc.stdout+'\nSTDERR:\n'+proc.stderr,encoding='utf-8')
        report['native_probe_exit_code']=proc.returncode
        if proc.returncode:raise RuntimeError('native probe failed: '+proc.stderr[-1200:])
        meta,methods,values,accessor_errors=parse(proc.stdout)
        report.update({'native_metadata':meta,'quest_accessor_methods':methods,'quest_accessor_values':values,
                       'accessor_invocation_errors':accessor_errors})
        if meta.get('flavor')!='Forever' or meta.get('complete')!='true':raise RuntimeError('incomplete native output')
        if not methods:raise RuntimeError('no quest accessors found')
        if any(x['quest_id'] not in IDS for x in values):raise RuntimeError('unexpected quest id')
        if accessor_errors:raise RuntimeError(f'{len(accessor_errors)} accessor invocation errors')
        for field in ('Exists','name','requiredRaces','requiredLevel','preQuestSingle','nextQuestInChain'):
            found={x['quest_id'] for x in values if x['accessor']==field}
            # Empty prerequisite values may be represented by absent entries, but scalar fields must exist.
            if field in ('Exists','name','requiredRaces','requiredLevel') and found!=IDS:
                raise RuntimeError(f'incomplete field {field}: missing {sorted(IDS-found)}')
        masks={x['quest_id']:int(x['value_repr']) for x in values if x['accessor']=='requiredRaces'}
        if masks.get(94414)!=0:raise RuntimeError('quest 94414 race mask changed; review required')
        report['native_quest_fields_verified']=True
        # Captured values are actual provider returns. Their eligibility semantics remain unverified.
        report['native_provider_values_captured']=bool(values)
    except Exception as e:report['errors'].append(f'{type(e).__name__}: {e}')
    report['probe_passed']=not report['errors']
    (out/'forever-native-quest-v22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'probe_passed':report['probe_passed'],'errors':report['errors'],
                      'captured_values':len(report.get('quest_accessor_values',[])),
                      'effective_quest_values_verified':False},indent=2))
    return 0 if report['probe_passed'] else 1
if __name__=='__main__':sys.exit(run())
