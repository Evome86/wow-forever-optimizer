#!/usr/bin/env python3
"""Evidence-preserving quest graph and target candidate tiers; no in-game playability assertions."""
import argparse, collections, csv, hashlib, json, pathlib, re
from build_eligibility_v24 import audit, ids, PIN
EDGE_FIELDS=('preQuestSingle','preQuestGroup','exclusiveTo','inGroupWith','childQuests','breadcrumbs')
SCALAR_LINKS=('nextQuestInChain','parentQuest','breadcrumbForQuestId','disabledByQuest','availableStartingWith','availableUntilCompleted')
SKY=1<<33

def graph(native):
    eligibility=audit(native)
    qs=native['quests']; states={str(q['id']):q for q in eligibility['quests']}
    edges=[]; unresolved=[]; inbound=collections.Counter()
    for source,row in sorted(qs.items(),key=lambda kv:int(kv[0])):
        for field in EDGE_FIELDS:
            for target in ids(row.get(field)):
                edge={'from':int(source),'to':target,'field':field,'target_present':str(target) in qs,'interpretation':'RAW_REFERENCE_ONLY'}
                edges.append(edge)
                if str(target) not in qs: unresolved.append(edge)
                inbound[str(target)]+=1
        for field in SCALAR_LINKS:
            val=row.get(field)
            if type(val) is int and val>0:
                edge={'from':int(source),'to':val,'field':field,'target_present':str(val) in qs,'interpretation':'RAW_REFERENCE_ONLY'}
                edges.append(edge)
                if str(val) not in qs: unresolved.append(edge)
                inbound[str(val)]+=1
    rows=[]; counts=collections.Counter()
    for q in eligibility['quests']:
        raw=qs[str(q['id'])]
        if q['status']=='EXCLUDED_BY_EXPLICIT_FIELDS': tier='EXPLICITLY_EXCLUDED'
        elif q['race_state']=='MASK_INCLUDES_SKYBORNE': tier='EXPLICIT_RACE_MATCH_UNVERIFIED'
        else: tier='ZERO_RACE_MASK_UNVERIFIED'
        counts[tier]+=1
        rows.append({'id':q['id'],'name':q['name'],'zone':q['zoneOrSort'],'required_level':q['requiredLevel'],
                     'quest_level':q['questLevel'],'tier':tier,'blockers':q['explicit_blockers'],
                     'unknown':q['unverified_conditions'],'preQuestSingle':ids(raw.get('preQuestSingle')),
                     'preQuestGroup':ids(raw.get('preQuestGroup')),'exclusiveTo':ids(raw.get('exclusiveTo')),
                     'startedBy':raw.get('startedBy'),'finishedBy':raw.get('finishedBy'),
                     'incoming_reference_count':inbound[str(q['id'])]})
    # Explicit examples are diagnostics, not a recommended route.
    examples={str(i):next((r for r in rows if r['id']==i),None) for i in (92595,92871,93320,93958,94414,95349)}
    return {'version':'2.5','source_version':'2.3','upstream_commit':PIN,'target':eligibility['target'],
            'playable_quests_verified':False,'route_eligibility_gate':'BLOCKED_SEMANTICS_AND_INGAME_VALIDATION',
            'interpretation':'Raw quest references are NOT proven AND/OR prerequisite logic; candidates are NOT confirmed playable.',
            'quest_count':len(rows),'edge_count':len(edges),'unresolved_reference_count':len(unresolved),
            'tier_counts':dict(counts),'examples':examples,'quests':rows,'edges':edges,'unresolved_references':unresolved}

def semantic_evidence(root):
    """Collect source snippets with filenames/line numbers without asserting runtime semantics."""
    patterns={'zero_mask':re.compile(r'requiredRaces|raceMask|race.*mask',re.I),
              'prerequisites':re.compile(r'preQuestSingle|preQuestGroup',re.I),
              'availability':re.compile(r'availableStartingWith|availableUntilCompleted|disabledByQuest',re.I)}
    results={k:[] for k in patterns}; files=0
    for p in sorted(root.rglob('*.lua')):
        if any(part in ('.git','node_modules') for part in p.parts): continue
        files+=1
        try: lines=p.read_text(encoding='utf-8',errors='replace').splitlines()
        except OSError: continue
        for n,line in enumerate(lines,1):
            for name,pattern in patterns.items():
                if pattern.search(line) and len(results[name])<180:
                    results[name].append({'file':str(p.relative_to(root)),'line':n,'text':line.strip()[:250]})
    return {'source':'QuestieDB pinned source code','upstream_commit':PIN,'files_scanned':files,
            'semantics_verified':False,'note':'Search hits only; inspect call sites and validate with in-game observations before unlocking.',
            'hits':results}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default='reports/forever-native-quests-v23.json');p.add_argument('--output-dir',default='reports');p.add_argument('--source-dir');a=p.parse_args()
    data=json.loads(pathlib.Path(a.input).read_text(encoding='utf-8')); result=graph(data)
    out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    result['input_sha256']=hashlib.sha256(pathlib.Path(a.input).read_bytes()).hexdigest()
    (out/'forever-graph-v25.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    summary={k:v for k,v in result.items() if k not in ('quests','edges','unresolved_references')}
    (out/'forever-graph-v25-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    with (out/'forever-candidates-v25.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['id','name','zone','required_level','quest_level','tier','blockers','unknown','preQuestSingle','preQuestGroup','exclusiveTo'])
        for r in result['quests']:
            w.writerow([r[k] for k in ('id','name','zone','required_level','quest_level','tier')]+[';'.join(r['blockers']),';'.join(r['unknown'])]+[';'.join(map(str,r[k])) for k in ('preQuestSingle','preQuestGroup','exclusiveTo')])
    if a.source_dir:
        src=pathlib.Path(a.source_dir)
        if not src.is_dir(): raise ValueError('source directory missing')
        (out/'forever-semantics-evidence-v25.json').write_text(json.dumps(semantic_evidence(src),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'quest_count':result['quest_count'],'edge_count':result['edge_count'],'tier_counts':result['tier_counts'],'gate':result['route_eligibility_gate']},indent=2))
if __name__=='__main__':main()
