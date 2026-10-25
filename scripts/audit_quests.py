#!/usr/bin/env python3
"""Structural audit only. Does not claim gameplay semantic verification."""
import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ('id','name','started_by_raw','finished_by_raw','required_level','quest_level','required_races_mask','required_classes_mask','objectives_raw','prerequisites_raw')

def audit(data):
    quests = data.get('quests')
    if not isinstance(quests, dict):
        raise ValueError('quests must be an object')
    issues = []
    counts = collections.Counter()
    mask_counts = collections.Counter()
    class_counts = collections.Counter()
    levels = collections.Counter()
    missing = collections.Counter()
    ids = set()
    for key, q in quests.items():
        if not isinstance(q, dict):
            issues.append({'quest_id':key,'code':'INVALID_RECORD'}); continue
        for field in FIELDS:
            if field not in q: missing[field] += 1
        qid = q.get('id')
        if not isinstance(qid,int) or isinstance(qid,bool) or qid <= 0 or str(qid) != key or qid in ids:
            issues.append({'quest_id':key,'code':'INVALID_ID'}); continue
        ids.add(qid)
        for field in ('required_level','quest_level'):
            v = q.get(field)
            if v is None: counts[field+'_missing'] += 1
            elif not isinstance(v,int) or isinstance(v,bool) or not 0 <= v <= 100:
                issues.append({'quest_id':qid,'code':'INVALID_'+field.upper(),'value':v})
            else: levels[field] += 1
        if isinstance(q.get('required_level'),int) and q['required_level'] <= 30:
            counts['minimum_level_at_most_30'] += 1
        if q.get('name') is None: counts['name_missing'] += 1
        elif not isinstance(q['name'],str): issues.append({'quest_id':qid,'code':'INVALID_NAME'})
        for field, tally in (('required_races_mask',mask_counts),('required_classes_mask',class_counts)):
            v = q.get(field)
            if v is None: counts[field+'_missing'] += 1
            elif not isinstance(v,int) or isinstance(v,bool) or v < 0:
                issues.append({'quest_id':qid,'code':'INVALID_'+field.upper()})
            else: tally[str(v)] += 1
        for field in ('started_by_raw','finished_by_raw','objectives_raw','prerequisites_raw'):
            if q.get(field) is None: counts[field+'_missing'] += 1
        p = q.get('prerequisites_raw')
        if p is not None and not isinstance(p,dict): issues.append({'quest_id':qid,'code':'INVALID_PREREQUISITES_CONTAINER'})
    counts['quest_count'] = len(quests)
    counts['structurally_valid_id_count'] = len(ids)
    counts['issues_count'] = len(issues)
    return {'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'structural_pass_unverified' if not issues and not missing else 'structural_issues_unverified',
            'source_sha256':data.get('source_sha256'),
            'checks':dict(sorted(counts.items())), 'fields_missing':dict(sorted(missing.items())),
            'required_races_mask_distribution':dict(sorted(mask_counts.items(),key=lambda x:-x[1])),
            'required_classes_mask_distribution':dict(sorted(class_counts.items(),key=lambda x:-x[1])),
            'level_fields_present':dict(levels), 'issues':issues[:200], 'issues_truncated':len(issues)>200,
            'verified_xp':False,'verified_eligibility':False,'verified_prerequisites':False,
            'blocking_unknowns':['Quest XP not provided in imported fields',
              'Race/class mask semantics not verified against Forever definitions',
              'Prerequisite fields 12–16 not semantically verified',
              'NPC/object locations and travel graph not included in this import',
              'Quest availability and game build/version not verified'],
            'release_gate':'BLOCKED: do not calculate or publish optimized routes from this audit alone'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=Path('reports/forever-quests.json'))
    p.add_argument('--output',type=Path,default=Path('reports/forever-audit.json'))
    a=p.parse_args()
    data=json.loads(a.input.read_text(encoding='utf-8'))
    result=audit(data)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Status:',result['status'],'| Quests:',result['checks']['quest_count'],'| Issues:',result['checks']['issues_count'])
    print('Release gate:',result['release_gate'])
    if result['status'] != 'structural_pass_unverified': raise SystemExit(2)

if __name__=='__main__': main()
