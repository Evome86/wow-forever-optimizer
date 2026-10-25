#!/usr/bin/env python3
"""Evidence-only Forever starter and correction audit. No Lua execution or inferred quest eligibility."""
import argparse,hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter

TARGETS=(92595,92596,92860,92871,93836,94369,94414)
KEYWORDS=('Zephras','Windshaper','Skyborne','questKeys.requiredRaces','questKeys.preQuestSingle','questKeys.preQuestGroup')

def sha(b):return hashlib.sha256(b).hexdigest()
def excerpts(path,lines,terms,window=3,limit=100):
    matched=[i for i,line in enumerate(lines) if any(t.lower() in line.lower() for t in terms)]
    ranges=[]
    for i in matched[:limit]:
        a=max(0,i-window);b=min(len(lines),i+window+1)
        if ranges and a<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],max(b,ranges[-1][1]))
        else:ranges.append((a,b))
    return [{'start_line':a+1,'end_line':b,'text':'\n'.join(f'{k+1}: {lines[k]}' for k in range(a,b))} for a,b in ranges],len(matched)

def audit(root, imported, max_files=1200):
    root=Path(root)
    quest_ids={int(x) for x in imported['quests']}
    files=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix in ('.lua','.md','.toc','.xml') and '.git' not in p.parts)
    if len(files)>max_files:raise ValueError('File safety cap exceeded')
    evidence=[];location_counts=Counter();errors=[]
    for p in files:
        relative=p.relative_to(root).as_posix()
        if p.stat().st_size>4_000_000:
            errors.append({'file':relative,'reason':'over 4MB; not scanned'});continue
        data=p.read_bytes()
        try:lines=data.decode('utf-8').splitlines()
        except UnicodeDecodeError:
            errors.append({'file':relative,'reason':'non UTF-8'});continue
        # Quest IDs are bounded numeric tokens; source line numbers and surrounding code retained.
        target_terms=[str(i) for i in TARGETS]
        hits=[(i+1,sorted({q for q in TARGETS if re.search(r'(?<!\d)'+str(q)+r'(?!\d)',line)})) for i,line in enumerate(lines) if any(re.search(r'(?<!\d)'+str(q)+r'(?!\d)',line) for q in TARGETS)]
        key_context=(relative in ('src/meta/questMeta.lua','src/api.lua','docs/api.md','docs/forever-data.md','src/corrections/Forever/foreverQuestFixes.lua') or 'Forever' in relative and ('Quest' in relative or 'quest' in relative))
        snippets,matched=excerpts(relative,lines,target_terms+list(KEYWORDS) if key_context else target_terms,window=3,limit=65)
        if hits or (key_context and matched):
            evidence.append({'file':relative,'sha256':sha(data),'line_count':len(lines),'target_hits':[{'line':n,'quest_ids':ids} for n,ids in hits[:250]],'total_target_hit_lines':len(hits),'matching_lines_total':matched,'snippets':snippets,'snippets_truncated':matched>65})
            for _,ids in hits:
                for q in ids:location_counts[q]+=1
    correction= root/'src/corrections/Forever/foreverQuestFixes.lua'
    correction_status={'present':correction.is_file(),'executed':False,'patches_applied':False}
    if correction.is_file():correction_status['sha256']=sha(correction.read_bytes())
    return {'schema_version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'import_sha256':imported.get('source_sha256'),'quest_count':len(quest_ids),
      'target_quests':[{'id':q,'present_in_raw_import':q in quest_ids,'source_hit_lines':location_counts[q]} for q in TARGETS],
      'files_scanned':len(files),'files_with_evidence':len(evidence),'evidence':evidence,'scan_warnings':errors,
      'corrections':correction_status,'runtime_quest_availability_verified':False,
      'release_gate':'BLOCKED: source mentions are not executed corrections; starter availability, prerequisites, XP and route unverified'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('vendor/QuestieDB'));ap.add_argument('--input',type=Path,default=Path('reports/forever-quests.json'));ap.add_argument('--output',type=Path,default=Path('reports/forever-starter-v14.json'));a=ap.parse_args()
    data=json.loads(a.input.read_text(encoding='utf-8'))
    result=audit(a.root,data)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Source files:',result['files_scanned'],'| evidence files:',result['files_with_evidence']);print('Starter IDs:',result['target_quests']);print(result['release_gate'])
if __name__=='__main__':main()
