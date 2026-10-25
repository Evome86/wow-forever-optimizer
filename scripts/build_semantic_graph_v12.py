#!/usr/bin/env python3
"""Build a TYPED raw-data quest graph and audit Forever corrections without executing Lua.
Not a corrected runtime database, not an eligibility or leveling-route proof.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

FIELDS = {'12':'preQuestGroup', '13':'preQuestSingle', '14':'childQuests',
          '15':'inGroupWith', '16':'exclusiveTo'}
OTHER = {'22':'nextQuestInChain', '25':'parentQuest', '27':'breadcrumbForQuestId', '28':'breadcrumbs'}
EXPECTED_SHA = 'd5be8516877505334f02073826ea0f22a394ddbf604bb5a33f5a39de5bb1ee87'
SKYBORNE_BIT = 1 << 33

def ids(value):
    if not isinstance(value, list):
        return []
    return [x for x in value if type(x) is int and x > 0]

def correction_blocks(text):
    """Audit top-level numeric quest entries via anchored headers, not a Lua parser.
    Braces and nested structures make applying patches unsafe: return snippets only.
    """
    headers = list(re.finditer(r'^\s{8}\[(\d+)\]\s*=\s*\{[^\n]*', text, re.M))
    result = []
    for n, match in enumerate(headers):
        end = headers[n+1].start() if n+1 < len(headers) else min(len(text), match.end()+4000)
        body = text[match.start():end]
        fields = sorted(set(re.findall(r'\[questKeys\.([A-Za-z][A-Za-z0-9_]*)\]', body)))
        if fields:
            result.append({'quest_id': int(match.group(1)), 'source_line': text.count('\n',0,match.start())+1,
                           'fields_mentioned':fields, 'skyborne_text_mentioned':bool(re.search(r'SKYBORNE|Skyborne|Zephras|Windshaper',body,re.I))})
    return result

def build(data, correction_text):
    if data.get('source_sha256') != EXPECTED_SHA:
        raise ValueError('Quest source SHA differs from pinned dataset')
    quests = data['quests']
    valid = {int(k) for k in quests}
    edges=[]; field_counts=Counter(); bad_values=[]
    for key,q in quests.items():
        qid=int(key)
        for field,name in FIELDS.items():
            raw=q.get('prerequisites_raw',{}).get(field)
            if raw is not None and not isinstance(raw,list):
                bad_values.append({'quest_id':qid,'field':field,'type':type(raw).__name__})
            for target in ids(raw):
                field_counts[name]+=1
                edges.append({'quest_id':qid,'referenced_quest_id':target,'field':int(field),'relation':name,
                              'target_in_import':target in valid,
                              'interpretation':'raw relation; NOT necessarily a required completion edge'})
    patches=correction_blocks(correction_text)
    patch_fields=Counter(f for p in patches for f in p['fields_mentioned'])
    skyborne=[p for p in patches if p['skyborne_text_mentioned']]
    mask_legacy = [int(k) for k,q in quests.items() if q.get('required_races_mask') in (77,178)]
    return {'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'source_sha256':data['source_sha256'], 'quest_count':len(quests),
            'raw_typed_edges':edges, 'raw_edge_counts':dict(sorted(field_counts.items())),
            'invalid_field_shapes':bad_values,
            'additional_semantic_fields':OTHER,
            'additional_semantic_fields_imported':False,
            'correction_audit':{'source':'src/corrections/Forever/foreverQuestFixes.lua',
                'source_sha256':hashlib.sha256(correction_text.encode()).hexdigest(),
                'entries_detected_heuristically':len(patches),
                'field_mentions_by_entry':dict(sorted(patch_fields.items())),
                'skyborne_keyword_entries':skyborne,
                'entry_inventory':patches,
                'patches_applied':False,
                'reason':'Lua corrections can use expressions, add/remove operations, and nested tables; regex cannot safely evaluate or apply them.'},
            'raw_legacy_faction_mask_quests':{'count':len(mask_legacy),'sample':mask_legacy[:30]},
            'eligibility':'UNVERIFIED: no corrected runtime quest data',
            'xp':'UNVERIFIED','route':'NOT GENERATED',
            'release_gate':'BLOCKED: corrections not applied, extra fields not imported, XP/travel unknown'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=Path('reports/forever-quests.json'))
    p.add_argument('--corrections',type=Path,default=Path('vendor/QuestieDB/src/corrections/Forever/foreverQuestFixes.lua'))
    p.add_argument('--output',type=Path,default=Path('reports/forever-semantic-graph-v12.json'))
    a=p.parse_args()
    data=json.loads(a.input.read_text(encoding='utf-8'))
    result=build(data,a.corrections.read_text(encoding='utf-8'))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('quests:',result['quest_count'],'typed edges:',len(result['raw_typed_edges']))
    print('correction entries:',result['correction_audit']['entries_detected_heuristically'])
    print('gate:',result['release_gate'])
if __name__=='__main__':main()
