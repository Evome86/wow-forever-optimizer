#!/usr/bin/env python3
"""v1.6: evidence-based race/loader/dependency audit. No Lua execution or route claims."""
import argparse, hashlib, json, re, sys
from pathlib import Path

SEEDS=(92595,92596,92860,92871,93836,94369,94414)
QUEST_FILES=('src/corrections/Forever/generated/foreverBaseQuest.lua',
             'src/corrections/Forever/foreverQuestFixes.lua')
RACE_NAMES=('ALL_HORDE','ALL_ALLIANCE','SKYBORNE_ALLIANCE','SKYBORNE_HORDE','NONE')
REF_FIELDS=('preQuestSingle','preQuestGroup','nextQuestInChain','parentQuest','breadcrumbForQuestId','breadcrumbs')
MAX_CLOSURE=150

def blocks(text, ids):
    """Top-level-ish [numeric] = { records, balancing braces; no evaluation."""
    lines=text.splitlines()
    hits=[]
    for i,s in enumerate(lines):
        m=re.match(r'^\s*\[(\d+)\]\s*=\s*\{\s*(?:--.*)?$',s)
        if not m or int(m[1]) not in ids: continue
        depth=0
        for j in range(i,min(len(lines),i+250)):
            row=re.sub(r'--.*','',lines[j])
            row=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'','""',row)
            depth+=row.count('{')-row.count('}')
            if depth==0:
                hits.append({'quest_id':int(m[1]),'line':i+1,'text':'\n'.join(lines[i:j+1])})
                break
    return hits

def refs_from_block(text):
    refs=[]
    for field in REF_FIELDS:
        for m in re.finditer(r'\[questKeys\.'+field+r'\]\s*=\s*(\{[^{}]*\}|\d+)',text):
            value=m[1]
            refs.extend({'field':field,'id':int(n)} for n in re.findall(r'\b\d+\b',value))
    return refs

def race_expressions(text):
    return [{'expression':m[1].strip(),'line_offset':text[:m.start()].count('\n')}
            for m in re.finditer(r'\[questKeys\.requiredRaces\]\s*=\s*([^,\n]+)',text)]

def build(root, overlay, imported, max_closure=MAX_CLOSURE):
    root=Path(root)
    sources={}
    for rel in QUEST_FILES:
        p=root/rel
        raw=p.read_bytes()
        sources[rel]={'text':raw.decode('utf-8'),'sha256':hashlib.sha256(raw).hexdigest()}
    # Expand only literal prerequisite references; never assert this is a complete graph.
    wanted=set(SEEDS); rounds=[]
    for _ in range(3):
        found={}
        for rel,source in sources.items():
            for b in blocks(source['text'],wanted):
                found.setdefault(str(b['quest_id']),[]).append({
                    'source':rel,'line':b['line'],'races':race_expressions(b['text']),
                    'literal_references':refs_from_block(b['text'])})
        new={r['id'] for entries in found.values() for e in entries for r in e['literal_references']}
        new={x for x in new if x not in wanted and x>0}
        if len(wanted|new)>max_closure: new=set(sorted(new)[:max(0,max_closure-len(wanted))])
        rounds.append({'examined':len(wanted),'new_reference_ids':sorted(new)})
        if not new: break
        wanted.update(new)
    found={}
    for rel,source in sources.items():
        for b in blocks(source['text'],wanted):
            found.setdefault(str(b['quest_id']),[]).append({
                'source':rel,'line':b['line'],'races':race_expressions(b['text']),
                'literal_references':refs_from_block(b['text'])})
    # Search *source declarations*, not assume any race constant's numeric meaning.
    declaration_evidence=[]
    loader_evidence=[]
    token_re=re.compile(r'\b(?:'+ '|'.join(RACE_NAMES)+r')\b')
    for p in sorted(root.rglob('*.lua')):
        rel=p.relative_to(root).as_posix()
        if 'QuestieDB' in p.parts and False: continue
        try: lines=p.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError: continue
        for i,line in enumerate(lines,1):
            if token_re.search(line) and ('=' in line or 'bit.' in line or 'lshift' in line):
                if len(declaration_evidence)<300:
                    declaration_evidence.append({'file':rel,'line':i,'text':line.strip()[:220],
                        'kind':'reference_or_definition_UNCLASSIFIED'})
            if ('foreverBaseQuest' in line or 'foreverQuestFixes' in line or 'foreverQuestTraces' in line) and rel not in QUEST_FILES:
                if len(loader_evidence)<200:
                    loader_evidence.append({'file':rel,'line':i,'text':line.strip()[:240]})
    candidates={}
    for q in sorted(wanted):
        entries=found.get(str(q),[])
        raw=imported.get('quests',{}).get(str(q))
        race=[{'source':e['source'],'line':e['line']+x['line_offset'],'expression':x['expression']}
              for e in entries for x in e['races']]
        candidates[str(q)]={'in_raw_import':raw is not None,'source_entries':entries,
            'race_expressions':race,'race_status':'UNRESOLVED_SOURCE_EXPRESSIONS',
            'route_eligible':False,'xp_verified':False}
    return {'schema_version':1,'version':'1.6','pinned_source_commit':'5c094f6e9a264f0dc54e2fde9731a37a97ed197c',
            'source_hashes':{k:v['sha256'] for k,v in sources.items()},
            'seed_ids':list(SEEDS),'closure_rounds':rounds,'candidates':candidates,
            'race_constant_evidence':declaration_evidence,'loader_references':loader_evidence,
            'v15_overlay_status':{q:overlay.get('records',{}).get(str(q),{}).get('status') for q in SEEDS},
            'interpretation':'Literal references and source snippets only. Loader order, race bitmasks and runtime eligibility are NOT verified.',
            'release_gate':'BLOCKED: no Lua runtime merge, no proven race semantics, no verified XP, no route'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default='vendor/QuestieDB')
    ap.add_argument('--overlay',default='reports/forever-overlay-v15.json')
    ap.add_argument('--imported',default='reports/forever-quests.json')
    ap.add_argument('--output',default='reports/forever-runtime-evidence-v16.json')
    a=ap.parse_args()
    overlay=json.loads(Path(a.overlay).read_text(encoding='utf-8'))
    imported=json.loads(Path(a.imported).read_text(encoding='utf-8'))
    out=build(a.root,overlay,imported)
    p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Quest IDs inspected:',len(out['candidates']))
    print('Race references:',len(out['race_constant_evidence']))
    print('Loader references:',len(out['loader_references']))
    print(out['release_gate'])
if __name__=='__main__':main()
