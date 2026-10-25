#!/usr/bin/env python3
"""Conservative, reproducible QuestieDB semantics reconnaissance. No gameplay assertions."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

FIELDS = {f'field_{i}':i for i in range(12,17)}

def inspect(data, metadata_text):
    quests = data['quests']
    if not isinstance(quests, dict): raise ValueError('quests must be a mapping')
    names = {name:int(pos) for name,pos in re.findall(r"\['([^']+)'\]\s*=\s*(\d+)", metadata_text)}
    reverse_names = {int(idx):name for idx,name in re.findall(r"\[(\d+)\]\s*=\s*'([^']+)'", metadata_text)}
    field_verification = {name:{'index':idx,'source_name':reverse_names.get(idx), 'matches': idx in reverse_names or idx in names.values()} for name,idx in FIELDS.items()}
    race = Counter(); cls = Counter(); references = {}; missing_refs = {}; examples={}
    for qid,q in quests.items():
        for field,tally in [('required_races_mask',race),('required_classes_mask',cls)]:
            value=q.get(field)
            if isinstance(value,int) and not isinstance(value,bool): tally[str(value)]+=1
        raw=q.get('prerequisites_raw') or {}
        for name,idx in FIELDS.items():
            v=raw.get(str(idx))
            if v is None: continue
            if not isinstance(v,list):
                references.setdefault(name,Counter())['non_list']+=1
                examples.setdefault(name,[])
                if len(examples[name])<5: examples[name].append({'quest_id':int(qid),'raw':v})
                continue
            references.setdefault(name,Counter())['quests_with_field']+=1
            references[name]['raw_entries']+=len(v)
            for item in v:
                if isinstance(item,int) and not isinstance(item,bool) and item>0:
                    references[name]['positive_id_entries']+=1
                    if str(item) not in quests:
                        missing_refs.setdefault(name,Counter())[str(item)]+=1
                else: references[name]['non_positive_or_non_integer_entries']+=1
            examples.setdefault(name,[])
            if len(examples[name])<5: examples[name].append({'quest_id':int(qid),'raw':v[:15]})
    q=quests.get('9321')
    return {
      'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'source_sha256':data.get('source_sha256'), 'quest_count':len(quests),
      'quest_meta_sha256':hashlib.sha256(metadata_text.encode()).hexdigest(),
      'field_mapping':field_verification,
      'race_masks':{'distinct':len(race),'above_u32':{k:v for k,v in race.items() if int(k)>2**32-1},'distribution':dict(race.most_common())},
      'class_masks':{'distinct':len(cls),'distribution':dict(cls.most_common())},
      'quest_reference_fields':{name:{'counts':dict(references.get(name,{})),'missing_target_ids_sample':dict(missing_refs.get(name,Counter()).most_common(15)),'examples':examples.get(name,[])} for name in FIELDS},
      'quest_9321':{'present':q is not None,'quest_level':q.get('quest_level') if q else None,'name':q.get('name') if q else None},
      'notes':['Field names/indexes are checked against the pinned QuestieDB source; gameplay meaning and logical operators are not proven.', 'Missing reference IDs can reflect partial datasets or special semantics; not automatically invalid.', 'Race masks above 32 bits are reported without truncation or eligibility assumptions.'],
      'verified_xp':False,'verified_eligibility':False,'verified_prerequisite_logic':False,
      'release_gate':'BLOCKED: semantic reconnaissance is not a validated leveling route'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=Path('reports/forever-quests.json'))
    parser.add_argument('--quest-meta',type=Path,default=Path('vendor/QuestieDB/src/meta/questMeta.lua'))
    parser.add_argument('--output',type=Path,default=Path('reports/forever-semantics-v06.json'))
    args=parser.parse_args()
    data=json.loads(args.input.read_text(encoding='utf-8'))
    meta=args.quest_meta.read_text(encoding='utf-8')
    result=inspect(data,meta)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Quests:',result['quest_count'],'| high race masks:',sum(result['race_masks']['above_u32'].values()))
    for name,info in result['field_mapping'].items(): print(name,info)
    print(result['release_gate'])
    if not all(f['matches'] for f in result['field_mapping'].values()):
        raise SystemExit('QuestieDB field mapping changed: inspect report before proceeding')
if __name__=='__main__':main()
