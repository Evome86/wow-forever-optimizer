#!/usr/bin/env python3
"""Full, lossless native provider export; conservative route eligibility gate."""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
UP = ROOT / 'vendor' / 'QuestieDB'
SHA = '5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
FIELDS = {'Exists','name','questLevel','requiredLevel','requiredMaxLevel','requiredRaces','requiredClasses','requiredSpecialization','preQuestSingle','preQuestGroup','nextQuestInChain','startedBy','finishedBy','zoneOrSort','objectives','objectivesText','exclusiveTo','inGroupWith','childQuests','breadcrumbForQuestId','breadcrumbs','availableStartingWith','availableUntilCompleted','questFlags','specialFlags','parentQuest','disabledByQuest'}

def decode_lines(text):
    meta, quests, errors = {}, {}, []
    for n, line in enumerate(text.splitlines(), 1):
        if not line: continue
        p = line.split('\t')
        if p[0] == 'META' and len(p) == 3:
            meta[p[1]] = p[2]
        elif p[0] == 'QUEST' and len(p) == 2:
            qid = int(p[1]); assert qid not in quests, f'duplicate quest {qid}'
            quests[qid] = {}
        elif p[0] == 'VALUE' and len(p) == 4:
            qid, field = int(p[1]), p[2]
            assert qid in quests and field in FIELDS, f'invalid value line {n}'
            assert field not in quests[qid], f'duplicate field {qid}/{field}'
            quests[qid][field] = json.loads(p[3])
        elif p[0] == 'ERROR' and len(p) >= 4:
            errors.append({'quest_id': int(p[1]), 'field': p[2], 'message': '\t'.join(p[3:])})
        else:
            raise ValueError(f'unknown output line {n}: {line[:100]}')
    return meta, quests, errors

def validate(meta, quests, errors):
    assert meta.get('flavor') == 'Forever', 'wrong flavor'
    assert meta.get('complete') == 'true', 'incomplete output'
    assert int(meta['quest_count']) == len(quests) and len(quests) > 1000, 'quest count mismatch'
    assert int(meta['error_count']) == len(errors) == 0, 'native accessor errors'
    assert int(meta['value_count']) == sum(map(len, quests.values())), 'value count mismatch'
    for qid, row in quests.items():
        for f in ('Exists','name','requiredLevel','requiredRaces'):
            assert f in row, f'missing {f} for {qid}'
        assert row['Exists'] is True, f'nonexistent quest {qid}'
        assert isinstance(row['name'], str), f'invalid name {qid}'
        assert isinstance(row['requiredRaces'], int) and row['requiredRaces'] >= 0
    assert 94414 in quests and quests[94414]['requiredRaces'] == 0, 'regression quest 94414'
    assert 92595 in quests and quests[92595]['requiredRaces'] == 8589934770, 'regression quest 92595'

def run():
    out = ROOT / 'reports'; out.mkdir(exist_ok=True)
    report = {'version':'2.3','upstream_commit_expected':SHA,'errors':[],
              'effective_quest_values_verified':False,
              'route_eligibility_gate':'BLOCKED_UNTIL_ELIGIBILITY_SEMANTICS_VALIDATED'}
    raw_path = out / 'forever-native-quests-v23.tsv'
    try:
        sha = subprocess.run(['git','rev-parse','HEAD'],cwd=UP,check=True,capture_output=True,text=True).stdout.strip()
        report['upstream_commit_actual'] = sha
        assert sha == SHA, 'upstream commit mismatch'
        script = ROOT / 'scripts/native_quest_export_v23.lua'
        probe = UP / '_forever_optimizer_native_export_v23.lua'
        try:
            probe.write_bytes(script.read_bytes())
            with raw_path.open('w',encoding='utf-8') as raw:
                proc = subprocess.run(['lua5.1',probe.name],cwd=UP,stdout=raw,stderr=subprocess.PIPE,text=True,timeout=300)
        finally:
            probe.unlink(missing_ok=True)
        (out/'forever-native-quests-v23.log').write_text(f'exit_code={proc.returncode}\n'+proc.stderr,encoding='utf-8')
        report['native_exit_code'] = proc.returncode
        assert proc.returncode == 0, f'native export failed: {proc.stderr[-1200:]}'
        raw_bytes = raw_path.read_bytes()
        report['raw_sha256'] = hashlib.sha256(raw_bytes).hexdigest()
        meta, quests, errors = decode_lines(raw_bytes.decode('utf-8'))
        report['native_metadata'] = meta
        report['accessor_errors'] = errors[:20]
        validate(meta, quests, errors)
        data = {'version':'2.3','source':'QuestieDB native Forever Source loader',
                'upstream_commit':SHA,'raw_sha256':report['raw_sha256'],
                'field_semantics_verified':False,
                'quests':{str(k):v for k,v in sorted(quests.items())}}
        (out/'forever-native-quests-v23.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        report.update({'quest_count':len(quests),'field_count':sum(map(len,quests.values())),
                       'native_provider_values_captured':True,'native_quest_fields_verified':True})
    except Exception as exc:
        report['errors'].append(f'{type(exc).__name__}: {exc}')
    report['export_passed'] = not report['errors']
    (out/'forever-native-export-v23-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'export_passed':report['export_passed'],'quest_count':report.get('quest_count'), 'errors':report['errors']},indent=2))
    return 0 if report['export_passed'] else 1

if __name__ == '__main__': sys.exit(run())
