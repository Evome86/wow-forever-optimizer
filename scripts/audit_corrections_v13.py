#!/usr/bin/env python3
"""v1.3: extract missing raw fields and identify correction-sensitive quests.
No Lua correction is executed. Every correction-sensitive result is quarantined.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from import_quests import Parser, ParseError
from build_semantic_graph_v12 import correction_blocks, EXPECTED_SHA
from filter_skyborne_v08 import classify

EXTRA = {22:'nextQuestInChain',25:'parentQuest',27:'breadcrumbForQuestId',28:'breadcrumbs'}

def raw_quests(source):
    m=re.search(r'QuestieDB\.questData\s*=\s*\[\[\s*return\s*',source)
    if not m: raise ParseError('Quest data payload not found')
    end=source.find(']]',m.end())
    if end<0: raise ParseError('Unclosed quest data payload')
    p=Parser(source[m.end():end]); data=p.value()
    if p.t[0]!='EOF' or not isinstance(data,dict): raise ParseError('Unexpected quest payload shape')
    return data

def field(row, index):
    if isinstance(row,list):return row[index-1] if len(row)>=index else None
    if isinstance(row,dict):return row.get(index)
    raise ValueError('Unexpected quest row type')

def build(imported,source_bytes,fix_bytes):
    if imported.get('source_sha256')!=EXPECTED_SHA:raise ValueError('Pinned import hash mismatch')
    if hashlib.sha256(source_bytes).hexdigest()!=EXPECTED_SHA:raise ValueError('Pinned raw data hash mismatch')
    source=source_bytes.decode('utf-8'); fixes=fix_bytes.decode('utf-8')
    raw=raw_quests(source); quests=imported['quests']
    if {str(k) for k in raw}!=set(quests):raise ValueError('Raw and imported quest IDs differ')
    extra={}; counts=Counter(); refs=[]
    for qid,row in raw.items():
        fields={}
        for idx,name in EXTRA.items():
            value=field(row,idx)
            fields[name]=value
            if value is not None:
                counts[name]+=1
                if isinstance(value,int) and not isinstance(value,bool) and value>0:
                    refs.append({'from':qid,'to':value,'relation':name,'target_present':str(value) in quests})
                elif isinstance(value,list):
                    for target in value:
                        if type(target) is int and target>0:
                            refs.append({'from':qid,'to':target,'relation':name,'target_present':str(target) in quests})
        extra[str(qid)]=fields
    blocks=correction_blocks(fixes)
    # Heuristic correction blocks can over/under-match nested Lua. Never equate with verified patch scope.
    suspect={b['quest_id'] for b in blocks}
    inventory=[]; statuses=Counter(); uncertain=Counter()
    for qid,q in sorted(quests.items(),key=lambda kv:int(kv[0])):
        status,reason=classify(q)
        statuses[status]+=1
        if int(qid) in suspect:uncertain[status]+=1
        inventory.append({'quest_id':int(qid),'raw_screening':status,'correction_mentioned_heuristically':int(qid) in suspect,
                          'confidence':'UNVERIFIED' if int(qid) in suspect else 'RAW_ONLY_UNVERIFIED'})
    return {'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'source_sha256':EXPECTED_SHA,'correction_source_sha256':hashlib.sha256(fix_bytes).hexdigest(),
        'quest_count':len(quests),'extra_fields':extra,'extra_field_non_null_counts':dict(counts),
        'extra_field_references':refs,'raw_screening_counts':dict(statuses),
        'correction_audit':{'heuristic_entries':len(blocks),'heuristic_unique_quest_ids':len(suspect),
            'screening_statuses_with_heuristic_correction':dict(uncertain),
            'entries':blocks,'patches_applied':False,
            'warning':'Quest blocks are detected heuristically. Lua expressions, nested tables, merges, deletes and execution order are NOT evaluated.'},
        'quest_inventory':inventory,
        'verified_runtime_eligibility':False,'xp_verified':False,'route_generated':False,
        'release_gate':'BLOCKED: Forever Lua corrections NOT applied; raw candidates cannot be promoted to playable quests'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=Path('reports/forever-quests.json'))
    p.add_argument('--source',type=Path,default=Path('vendor/QuestieDB/data/Forever/foreverQuestDB.lua'))
    p.add_argument('--corrections',type=Path,default=Path('vendor/QuestieDB/src/corrections/Forever/foreverQuestFixes.lua'))
    p.add_argument('--output',type=Path,default=Path('reports/forever-corrections-v13.json'))
    a=p.parse_args()
    result=build(json.loads(a.input.read_text(encoding='utf-8')),a.source.read_bytes(),a.corrections.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Quests:',result['quest_count'],'correction suspects:',result['correction_audit']['heuristic_unique_quest_ids'])
    print(result['release_gate'])
if __name__=='__main__':main()
