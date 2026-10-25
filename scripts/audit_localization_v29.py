#!/usr/bin/env python3
"""Read QuestieDB Forever deDE lookup names by numeric quest ID.
Only the first string in [id] = {"title", {...}} is a quest name.
Never conflate parser failure with zero translated quests.
"""
import argparse,csv,json,re
from pathlib import Path

ENTRY = re.compile(r'\[\s*(\d+)\s*\]\s*=\s*\{\s*"((?:\\.|[^"\\])*)"\s*,\s*\{',re.S)
STRING = re.compile(r'"((?:\\.|[^"\\])*)"')

def unescape(s):
    def sub(m):
        c=m.group(1)
        if c.isdigit():return chr(int(c))
        return {'a':'\a','b':'\b','f':'\f','n':'\n','r':'\r','t':'\t','v':'\v','\\':'\\','"':'"',"'":"'"}.get(c,c)
    return re.sub(r'\\(\d{1,3}|[abfnrtv\\"\'])',sub,s)

def parse(path):
    if not path.is_file():return {},{'present':False,'status':'FILE_MISSING','entries':0}
    raw=path.read_text(encoding='utf-8-sig')
    # Require the known QuestieDB wrapper, not an arbitrary Lua table.
    wrapper='l10n.questLookup["deDE"] = loadstring([[return {' in raw
    ids={};duplicates=[]
    if wrapper:
        for match in ENTRY.finditer(raw):
            key=str(int(match.group(1)))
            if key in ids:duplicates.append(key)
            ids[key]=unescape(match.group(2))
    info={'present':True,'bytes':path.stat().st_size,'wrapper_recognized':wrapper,
          'entries':len(ids),'duplicate_ids':duplicates[:30],
          'status':'PARSED' if ids and wrapper and not duplicates else 'PARSER_UNSUPPORTED',
          'sample_ids':list(ids)[:10]}
    return ids,info

def build(source,quests_file):
    quests=json.loads(quests_file.read_text(encoding='utf-8'))['quests']
    ids,info=parse(source/'l10n/Forever/lookupQuests/deDE.lua')
    rows=[];matched=0
    for key in sorted(quests,key=int):
        en=quests[key].get('name') or ''
        de=ids.get(str(int(key)))
        matched+=bool(de)
        rows.append({'quest_id':key,'enUS':en,'deDE':de or '',
                     'de_source':'quest_id' if de else 'missing',
                     'display_deDE':de or en})
    if info['status']!='PARSED':status=info['status']
    else:status='COMPLETE' if matched==len(quests) else 'PARTIAL'
    report={'version':'2.9','quest_count':len(quests),'german_names_matched':matched,
            'german_names_missing':len(quests)-matched,
            'coverage_percent':round(100*matched/len(quests),2) if quests else 0,
            'source':info,'localization_status':status,
            'missing_german_sample':[{'id':r['quest_id'],'english':r['enUS']} for r in rows if not r['deDE']][:30],
            'route_eligibility_gate':'BLOCKED_SEMANTICS_AND_INGAME_VALIDATION',
            'semantics_verified':False,'playable_quests_verified':False,
            'note':'Quest ID lookup names only; no inferred translations or gameplay eligibility.'}
    return report,rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-dir',default='vendor/QuestieDB')
    p.add_argument('--quests',default='reports/forever-native-quests-v23.json')
    p.add_argument('--output-dir',default='reports')
    a=p.parse_args();report,rows=build(Path(a.source_dir),Path(a.quests))
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'forever-localization-v29.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (out/'forever-quest-names-v29.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['quest_id','enUS','deDE','de_source','display_deDE']);w.writeheader();w.writerows(rows)
    print(f"v2.9: {report['localization_status']}: {report['german_names_matched']}/{report['quest_count']}")
    if report['localization_status'] in ('PARSER_UNSUPPORTED','FILE_MISSING'):
        raise SystemExit('German localization parser failed; see uploaded diagnostic report')
if __name__=='__main__':main()
