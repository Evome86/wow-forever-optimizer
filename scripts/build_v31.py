#!/usr/bin/env python3
"""Evidence-preserving level 1-60 and quest-eligibility audit for Forever."""
import argparse, collections, json
from pathlib import Path
from build_v30 import audit, PIN, refs

BANDS=((1,10),(11,20),(21,30),(31,40),(41,50),(51,60))
FIELDS=('preQuestSingle','preQuestGroup','availableStartingWith','availableUntilCompleted','disabledByQuest')

def band(value):
    if type(value) is not int: return 'UNKNOWN'
    if value <= 0: return 'ZERO_OR_NEGATIVE'
    for lo,hi in BANDS:
        if lo <= value <= hi:return f'{lo:02d}-{hi:02d}'
    return '61_PLUS'

def scalar_ref(value):
    return [value] if type(value) is int and value>0 else []

def analyze(quests):
    breakdown={k:{'all':0,'new_90k':0,'legacy':0} for k in [f'{a:02d}-{b:02d}' for a,b in BANDS]+['ZERO_OR_NEGATIVE','61_PLUS','UNKNOWN']}
    quest_levels={k:dict(v) for k,v in breakdown.items()}
    flags=collections.Counter(); missing=[]; samples=[]; maximum={'requiredLevel':None,'questLevel':None}
    for sid,q in sorted(quests.items(),key=lambda x:int(x[0])):
        qid=int(sid); new=qid>=90000; category='new_90k' if new else 'legacy'
        for key,target in (('requiredLevel',breakdown),('questLevel',quest_levels)):
            val=q.get(key); b=band(val);target[b]['all']+=1;target[b][category]+=1
            if type(val) is int and (maximum[key] is None or val>maximum[key]['value']):maximum[key]={'value':val,'quest_id':qid}
        issues=[]
        for field in FIELDS:
            value=q.get(field)
            values=refs(value) if field in ('preQuestSingle','preQuestGroup') else scalar_ref(value)
            if value not in (None,0,{},[]) and not values:flags[f'{field}_nonempty_unparsed']+=1;issues.append(field+'_UNPARSED')
            for ref in values:
                if str(ref) not in quests:
                    flags['missing_referenced_quest']+=1
                    if len(missing)<100:missing.append({'quest_id':qid,'field':field,'referenced_id':ref})
                    issues.append(field+'_MISSING_REFERENCE')
            if values:flags[field+'_populated_quests']+=1
        if q.get('requiredRaces') in (None,0):flags['race_mask_absent_or_zero']+=1
        if q.get('requiredClasses') in (None,0):flags['class_mask_absent_or_zero']+=1
        if issues and len(samples)<100:samples.append({'quest_id':qid,'issues':sorted(set(issues))})
    return {'version':'3.1','upstream_commit':PIN,'total_quests':len(quests),'new_90k_definition':'Quest ID >= 90000; ID range alone does not establish in-game availability',
            'level_bands_required_level':breakdown,'level_bands_quest_level':quest_levels,'maxima':maximum,
            'semantic_flags':dict(sorted(flags.items())),'missing_reference_samples':missing,'issue_samples':samples,
            'prerequisite_rules':{'preQuestSingle':'ALTERNATIVES per upstream type; do not interpret as AND',
                                  'preQuestGroup':'GROUP requirements per upstream type; runtime interpretation not independently validated',
                                  'availability_fields':'tracked, but not treated as fully validated gameplay gates',
                                  'race_and_class_masks':'reported without assuming a Skyborne race bit or verified playable class'},
            'skyborne_balance_druid_route':'BLOCKED_UNTIL_RACE_MASK_AND_RUNTIME_SEMANTICS_AND_INGAME_VALIDATION',
            'semantics_verified':False,'playable_quests_verified':False,
            'next_steps':['Validate Skyborne race bit from authoritative runtime/source evidence',
                          'Test AND/OR prerequisite and availability conditions against runtime consumers',
                          'Verify representative quest availability in game',
                          'Collect quest XP, travel and combat timing before route optimization']}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',default='vendor/QuestieDB');p.add_argument('--quests',default='reports/forever-native-quests-v23.json');p.add_argument('--output-dir',default='reports');a=p.parse_args()
    source=Path(a.source_dir); path=Path(a.quests); out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    prior,_=audit(source,path)
    raw=json.loads(path.read_text(encoding='utf-8'))
    if raw.get('upstream_commit')!=PIN:raise ValueError('Unexpected upstream commit')
    report=analyze(raw['quests'])
    report['localization_summary']={k:prior['localization'].get(k) for k in ('german_names_matched','german_names_missing','coverage_percent')}
    report['upstream_semantics_evidence']=prior['consumer_source_evidence']
    report['source_based_semantics_verified']=False
    (out/'forever-v31-level-and-eligibility.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('v3.1 complete:',report['total_quests'],'quests; playable route remains BLOCKED')
if __name__=='__main__':main()
