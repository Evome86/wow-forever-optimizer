#!/usr/bin/env python3
"""Collect exact pinned-source evidence; never infer runtime semantics from raw array positions."""
import argparse, hashlib, json, re
from pathlib import Path

TARGETS = [
 'src/meta/questMeta.lua', 'docs/api.md', 'docs/forever-data.md',
 'src/corrections/Forever/foreverQuestFixes.lua',
 'src/corrections/Forever/foreverNPCFixes.lua',
 'src/corrections/Forever/foreverObjectFixes.lua',
]
PATTERN = re.compile(r'pre.?requisite|pre.?quest|next.?quest|exclusive|breadcrumb|requiredRaces|requiredClasses|SKYBORNE|92595|92596|92860|92871|93836|94369|94414|questMeta|questKeys|questFlags|raceIDs',re.I)

def extract(path, max_matches=45, radius=3):
    lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
    matches=[i for i,s in enumerate(lines) if PATTERN.search(s)]
    selected=matches[:max_matches]
    ranges=[]
    for i in selected:
        start=max(0,i-radius); end=min(len(lines),i+radius+1)
        if ranges and start<=ranges[-1][1]: ranges[-1]=(ranges[-1][0],max(end,ranges[-1][1]))
        else: ranges.append((start,end))
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'line_count':len(lines),
            'match_count':len(matches),'matches_truncated':len(matches)>max_matches,
            'excerpts':[{'start_line':a+1,'end_line':b,'lines':[{'line':j+1,'text':lines[j][:320]} for j in range(a,b)]} for a,b in ranges]}

def audit(vendor, report):
    if report.get('release_gate') is None: raise ValueError('Expected v1.0 report with release gate')
    result={'schema_version':1,'upstream_commit':'5c094f6e9a264f0dc54e2fde9731a37a97ed197c',
            'input_source_sha256':report.get('source_sha256'),
            'input_boundary_count':report.get('cross_boundary_reference_count'),
            'source_files':{},'missing_files':[],
            'interpretation':{'raw_fields_12_to_16':'UNVERIFIED until schema and consumer are jointly reviewed',
                              'correction_application':'UNVERIFIED until importer vs runtime correction handling is reviewed',
                              'skyborne_eligibility':'UNVERIFIED; raw masks may omit runtime corrections'},
            'release_gate':'BLOCKED: source excerpts require semantic review; no verified leveling route'}
    for name in TARGETS:
        p=vendor/name
        if p.is_file(): result['source_files'][name]=extract(p)
        else: result['missing_files'].append(name)
    # Explicitly look for runtime consumers across manageable Lua source files.
    consumers=[]
    for root in (vendor/'src', vendor/'support'):
        if not root.exists(): continue
        for p in sorted(root.rglob('*.lua')):
            if p.stat().st_size>1_000_000: continue
            for no,line in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1):
                if re.search(r'(pre.?quest|next.?quest|exclusive|breadcrumb|questMeta|questKeys)',line,re.I):
                    if len(consumers)<150:
                        consumers.append({'file':str(p.relative_to(vendor)),'line':no,'text':line.strip()[:240]})
    result['consumer_search']={'sample':consumers,'sample_limit':150,'not_exhaustive':len(consumers)>=150}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--vendor',type=Path,default=Path('vendor/QuestieDB'))
    p.add_argument('--previous',type=Path,default=Path('reports/forever-semantics-v10.json'))
    p.add_argument('--output',type=Path,default=Path('reports/forever-source-verification-v11.json'))
    a=p.parse_args(); result=audit(a.vendor,json.loads(a.previous.read_text(encoding='utf-8')))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Inspected source files:',len(result['source_files']),'Missing:',len(result['missing_files']))
    print(result['release_gate'])
if __name__=='__main__':main()
