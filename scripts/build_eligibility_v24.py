#!/usr/bin/env python3
"""v2.4: conservative evidence-based Skyborne Druid candidate audit, NOT playable quest claims."""
import argparse, collections, csv, hashlib, json, pathlib, sys
SKYBORNE = 1 << 33
DRUID = 1 << 10
PIN = '5c094f6e9a264f0dc54e2fde9731a37a97ed197c'
LINK_FIELDS = ('preQuestSingle','preQuestGroup','exclusiveTo','inGroupWith','childQuests','breadcrumbs')

def ids(value):
    if not isinstance(value,dict): return []
    result=[]
    for v in value.values():
        if type(v) is int and v > 0: result.append(v)
    return sorted(set(result))

def audit(payload, maximum=30):
    if payload.get('version')!='2.3' or payload.get('upstream_commit')!=PIN: raise ValueError('unrecognized native export/version/commit')
    qs=payload.get('quests')
    if not isinstance(qs,dict) or len(qs)<5000: raise ValueError('incomplete quest dataset')
    result=[]; counts=collections.Counter(); refs=collections.Counter()
    for key,row in sorted(qs.items(),key=lambda kv:int(kv[0])):
        qid=int(key)
        if not isinstance(row,dict) or row.get('Exists') is not True: raise ValueError(f'invalid quest {qid}')
        race=row.get('requiredRaces'); clazz=row.get('requiredClasses'); level=row.get('requiredLevel'); maximum_level=row.get('requiredMaxLevel')
        if any(type(x) is not int or x<0 for x in (race,clazz,level,maximum_level)): raise ValueError(f'invalid eligibility fields {qid}')
        if race == 0: race_state='UNKNOWN_ZERO_MASK'
        elif race & SKYBORNE: race_state='MASK_INCLUDES_SKYBORNE'
        else: race_state='MASK_EXCLUDES_SKYBORNE'
        if clazz == 0: class_state='NO_CLASS_RESTRICTION_REPORTED'
        elif clazz & DRUID: class_state='MASK_INCLUDES_DRUID'
        else: class_state='MASK_EXCLUDES_DRUID'
        if level > maximum: level_state='ABOVE_LEVEL_CAP'
        elif maximum_level and maximum_level < level: level_state='MAX_LEVEL_BELOW_REQUIRED'
        else: level_state='WITHIN_REPORTED_LEVEL_BOUNDS'
        blockers=[]; unknown=[]
        if race_state=='MASK_EXCLUDES_SKYBORNE': blockers.append('RACE_MASK_EXCLUDES_SKYBORNE')
        if class_state=='MASK_EXCLUDES_DRUID': blockers.append('CLASS_MASK_EXCLUDES_DRUID')
        if level_state!='WITHIN_REPORTED_LEVEL_BOUNDS': blockers.append(level_state)
        if race_state=='UNKNOWN_ZERO_MASK': unknown.append('RACE_ZERO_MASK_SEMANTICS_UNVERIFIED')
        # Neither availability fields nor quest chain alternatives are sufficiently verified.
        if row.get('availableStartingWith',0): unknown.append('AVAILABLE_STARTING_WITH_SEMANTICS_UNVERIFIED')
        if row.get('availableUntilCompleted',0): unknown.append('AVAILABLE_UNTIL_COMPLETED_SEMANTICS_UNVERIFIED')
        if row.get('disabledByQuest',0): unknown.append('DISABLED_BY_QUEST_SEMANTICS_UNVERIFIED')
        if row.get('parentQuest',0): unknown.append('PARENT_QUEST_SEMANTICS_UNVERIFIED')
        for field in ('preQuestSingle','preQuestGroup'):
            if ids(row.get(field)): unknown.append(field.upper()+'_COMPLETION_UNVERIFIED')
        if ids(row.get('exclusiveTo')): unknown.append('EXCLUSIVITY_UNVERIFIED')
        if row.get('requiredSpecialization',0): unknown.append('SPECIALIZATION_SEMANTICS_UNVERIFIED')
        deps={f:ids(row.get(f)) for f in LINK_FIELDS if ids(row.get(f))}
        missing={f:[v for v in vv if str(v) not in qs] for f,vv in deps.items() if any(str(v) not in qs for v in vv)}
        if missing: unknown.append('REFERENCED_QUEST_NOT_EXPORTED')
        for f,vs in deps.items(): refs[f]+=len(vs)
        status='EXCLUDED_BY_EXPLICIT_FIELDS' if blockers else 'CANDIDATE_REQUIRES_VALIDATION'
        counts[status]+=1; counts[race_state]+=1; counts[class_state]+=1; counts[level_state]+=1
        result.append({'id':qid,'name':row.get('name',''),'zoneOrSort':row.get('zoneOrSort'),'questLevel':row.get('questLevel'),
          'requiredLevel':level,'requiredMaxLevel':maximum_level,'requiredRaces':race,'requiredClasses':clazz,
          'race_state':race_state,'class_state':class_state,'level_state':level_state,'status':status,
          'explicit_blockers':blockers,'unverified_conditions':unknown,'dependency_references':deps,'missing_references':missing,
          'startedBy':row.get('startedBy'),'finishedBy':row.get('finishedBy'),
          'nextQuestInChain':row.get('nextQuestInChain'), 'questFlags':row.get('questFlags'), 'specialFlags':row.get('specialFlags')})
    return {'version':'2.4','source_version':'2.3','upstream_commit':PIN,'target':{'faction':'Horde','race':'Skyborne','race_bit':SKYBORNE,'class':'Druid','class_bit':DRUID,'level_range':[1,maximum]},
      'semantics_verified':False,'playable_quests_verified':False,'route_eligibility_gate':'BLOCKED_UNTIL_ZERO_MASK_AND_DEPENDENCY_SEMANTICS_VERIFIED',
      'interpretation':'Candidate = not excluded by explicit race/class/level masks; NOT proof of faction, chain availability, or in-game playability.',
      'counts':dict(counts),'reference_counts':dict(refs),'quests':result}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default='reports/forever-native-quests-v23.json');ap.add_argument('--output-dir',default='reports');a=ap.parse_args()
    out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    try:
        raw=pathlib.Path(a.input).read_bytes(); data=audit(json.loads(raw))
        data['input_sha256']=hashlib.sha256(raw).hexdigest()
        (out/'forever-eligibility-v24.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        with (out/'forever-eligibility-v24.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f);writer.writerow(['id','name','requiredLevel','questLevel','zoneOrSort','race_state','class_state','status','blockers','unverified_conditions','preQuestSingle','preQuestGroup'])
            for q in data['quests']:
                writer.writerow([q[k] for k in ('id','name','requiredLevel','questLevel','zoneOrSort','race_state','class_state','status')]+[';'.join(q['explicit_blockers']),';'.join(q['unverified_conditions']),';'.join(map(str,q['dependency_references'].get('preQuestSingle',[]))),';'.join(map(str,q['dependency_references'].get('preQuestGroup',[])))])
        summary={k:v for k,v in data.items() if k!='quests'}
        summary['total_quests']=len(data['quests']);summary['selected_examples']={str(q['id']):q for q in data['quests'] if q['id'] in (92595,92871,93320,93958,94414)}
        (out/'forever-eligibility-v24-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'total_quests':len(data['quests']),'counts':data['counts'],'gate':data['route_eligibility_gate']},indent=2));return 0
    except Exception as exc:
        (out/'forever-eligibility-v24-error.json').write_text(json.dumps({'error':str(exc)},indent=2)+'\n');print(str(exc),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
