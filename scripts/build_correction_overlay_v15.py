#!/usr/bin/env python3
"""Conservative source-backed Forever quest overlay; does not execute Lua or assert playability."""
import argparse, hashlib, json, re
from pathlib import Path

TARGETS=(92595,92596,92860,92871,93836,94369,94414)
FILES=('src/corrections/Forever/traces/foreverQuestTraces.lua',
       'src/corrections/Forever/generated/foreverBaseQuest.lua',
       'src/corrections/Forever/foreverQuestFixes.lua')
ALLOWED={'name','questLevel','requiredLevel','objectivesText','startedBy_add','finishedBy_add',
         'startedBy_remove','finishedBy_remove','requiredRaces','requiredClasses',
         'preQuestSingle','preQuestGroup','nextQuestInChain','exclusiveTo','breadcrumbs'}

def source_blocks(text, target_ids=TARGETS):
    """Line-oriented, bounded entry capture; only entries at their own start line."""
    lines=text.splitlines()
    starts=[]
    for i,line in enumerate(lines):
        m=re.match(r'^\s*\[(\d+)\]\s*=\s*\{\s*(?:--.*)?$',line)
        if m and int(m.group(1)) in target_ids: starts.append((i,int(m.group(1))))
    result=[]
    for start,qid in starts:
        # Nested braces in values: balance while ignoring quoted strings and line comments.
        depth=0; finish=None
        for j in range(start,min(len(lines),start+150)):
            s=re.sub(r'--.*$','',lines[j]);s=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','""',s)
            depth+=s.count('{')-s.count('}')
            if depth==0:finish=j;break
        if finish is None:raise ValueError(f'Unclosed target entry {qid} at line {start+1}')
        result.append((qid,start+1,lines[start:finish+1]))
    return result

def literal(value):
    """Allow only JSON-like Lua literals, never expressions or Lua code."""
    value=value.strip().rstrip(',').strip()
    if re.fullmatch(r'-?\d+',value):return int(value)
    if re.fullmatch(r'"(?:\\.|[^"\\])*"',value):return json.loads(value)
    if value in ('nil','true','false'):return {'nil':None,'true':True,'false':False}[value]
    if re.fullmatch(r'\{[\s\d{},-]*\}',value):
        # Convert nested, numeric-only Lua arrays via the existing strict parser.
        from import_quests import Parser
        p=Parser(value);v=p.value()
        if p.t[0]!='EOF':raise ValueError('Trailing tokens')
        return v
    if value.startswith('{') and value.endswith('}'):
        # Strings in arrays are supported by the same non-executing parser.
        from import_quests import Parser
        p=Parser(value);v=p.value()
        if p.t[0]!='EOF':raise ValueError('Trailing tokens')
        return v
    raise ValueError('Unsupported Lua expression')

def parse_entry(lines):
    fields={};uncertain=[]
    for row in lines[1:-1]:
        s=row.strip()
        if not s or s.startswith('--'):continue
        m=re.match(r'^\[questKeys\.(\w+)\]\s*=\s*(.*)$',s)
        if not m:
            uncertain.append({'reason':'unparsed_line','text':s[:160]});continue
        key,value=m.groups()
        if key not in ALLOWED:
            uncertain.append({'reason':'unknown_or_unhandled_field','field':key});continue
        try:fields[key]=literal(value.split(' --')[0])
        except Exception:uncertain.append({'reason':'unsupported_expression_or_multiline','field':key,'text':value[:160]})
    return fields,uncertain

def build(root,imported):
    root=Path(root)
    records={str(q):{'quest_id':q,'in_raw_import':str(q) in imported['quests'],
                      'evidence_fields':{},'source_patches':[],'conflicts':[],
                      'status':'SOURCE_ONLY_UNVERIFIED'} for q in TARGETS}
    provenance=[]
    for rel in FILES:
        path=root/rel
        if not path.is_file():raise FileNotFoundError(path)
        data=path.read_bytes();text=data.decode('utf-8');digest=hashlib.sha256(data).hexdigest()
        provenance.append({'path':rel,'sha256':digest})
        for qid,line,lines in source_blocks(text):
            fields,warnings=parse_entry(lines)
            r=records[str(qid)]
            patch={'file':rel,'line':line,'sha256':digest,'fields':fields,'warnings':warnings}
            r['source_patches'].append(patch)
            for k,v in fields.items():
                if k in r['evidence_fields'] and r['evidence_fields'][k]!=v:
                    r['conflicts'].append({'field':k,'prior':r['evidence_fields'][k],'new':v,'file':rel})
                else:r['evidence_fields'][k]=v
    for r in records.values():
        r['source_patches_count']=len(r['source_patches'])
        r['eligible_for_route']=False
        r['xp_verified']=False
        r['runtime_corrections_applied']=False
        r['reason']='Source literals are evidence, not a verified runtime merge, eligibility or XP.'
    return {'schema_version':1,'source_provenance':provenance,'raw_quest_count':len(imported['quests']),
            'target_count':len(TARGETS),'records':records,
            'merge_policy':'Evidence-only. No Lua executed. No unsupported expressions evaluated. Conflicts retained, never silently overridden.',
            'npc_links':'NPC questStarts/questEnds and _add/_remove NOT merged in v1.5; require separate validated NPC-key semantics.',
            'route_generated':False,'release_gate':'BLOCKED: runtime merge, starter eligibility, prerequisites and XP not verified'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='vendor/QuestieDB');ap.add_argument('--input',default='reports/forever-quests.json');ap.add_argument('--output',default='reports/forever-overlay-v15.json');a=ap.parse_args()
    imported=json.loads(Path(a.input).read_text(encoding='utf-8'))
    result=build(a.root,imported)
    p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Source-backed entries:',sum(bool(r['source_patches']) for r in result['records'].values()),'/',len(TARGETS))
    print(result['release_gate'])
if __name__=='__main__':main()
