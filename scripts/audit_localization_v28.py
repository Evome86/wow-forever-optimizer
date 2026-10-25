#!/usr/bin/env python3
"""Inspect QuestieDB localization without assuming its Lua table layout.
Never call zero parsed entries 'zero translations': report PARSER_UNSUPPORTED.
"""
import argparse,csv,json,re
from pathlib import Path

# Covers numeric quest-id keys, Lua escaped quoted values and bracket-quoted values.
NUMERIC = re.compile(r'\[\s*(\d+)\s*\]\s*=\s*(?:"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\'\\])*)\')',re.S)
QUOTED_KEY = re.compile(r'\[\s*(["\'])(.*?)\1\s*\]\s*=\s*(["\'])((?:\\.|(?!\3).)*)\3',re.S)

def lua_unescape(s):
    return re.sub(r'\\(\d{1,3}|[abfnrtv\\"\'])',lambda m:chr(int(m[1])) if m[1].isdigit() else {'a':'\a','b':'\b','f':'\f','n':'\n','r':'\r','t':'\t','v':'\v'}.get(m[1],m[1]),s)

def inspect(path):
    if not path.is_file():return {},{}, {'present':False,'status':'FILE_MISSING','parsed_entries':0}
    raw=path.read_text(encoding='utf-8-sig',errors='replace')
    entries={str(int(m[1])):lua_unescape(m[2] if m[2] is not None else m[3]) for m in NUMERIC.finditer(raw)}
    by_name={lua_unescape(m[2]):lua_unescape(m[4]) for m in QUOTED_KEY.finditer(raw)}
    # Sample source syntax, not names or content from arbitrary external data.
    examples=[line.strip()[:240] for line in raw.splitlines() if line.strip() and not line.lstrip().startswith('--')][:15]
    info={'present':True,'bytes':path.stat().st_size,'numeric_entries':len(entries),'string_key_entries':len(by_name),'status':'PARSED' if entries or by_name else 'PARSER_UNSUPPORTED','source_shape_samples':examples}
    return entries,by_name,info

def build(source,quest_file):
    quests=json.loads(quest_file.read_text(encoding='utf-8'))['quests']
    ids,byname,info=inspect(source/'l10n/Forever/lookupQuests/deDE.lua')
    rows=[];n=0;methods={'quest_id':0,'english_name':0,'missing':0}
    for key in sorted(quests,key=int):
        en=quests[key].get('name','');de=ids.get(key);method='quest_id'
        if de is None and en in byname:de=byname[en];method='english_name'
        if de is None:de='';method='missing'
        methods[method]+=1;n+=bool(de)
        rows.append({'quest_id':key,'enUS':en,'deDE':de,'de_source':method,'display_deDE':de or en})
    status='PARSER_UNSUPPORTED' if info['status']=='PARSER_UNSUPPORTED' else ('PARTIAL' if n<len(quests) else 'COMPLETE')
    report={'version':'2.8','quest_count':len(quests),'german_names_matched':n,'german_names_missing':len(quests)-n,'coverage_percent':round(100*n/len(quests),2) if quests else 0,'source':info,'match_methods':methods,'localization_status':status,'route_eligibility_gate':'BLOCKED_SEMANTICS_AND_INGAME_VALIDATION','semantics_verified':False,'playable_quests_verified':False,'note':'A source file without parsed entries is a parser failure, NOT proof of missing translations. Name-key matches may be ambiguous when English names repeat.'}
    return report,rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',default='vendor/QuestieDB');p.add_argument('--quests',default='reports/forever-native-quests-v23.json');p.add_argument('--output-dir',default='reports');a=p.parse_args()
    report,rows=build(Path(a.source_dir),Path(a.quests));out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'forever-localization-v28.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (out/'forever-quest-names-v28.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['quest_id','enUS','deDE','de_source','display_deDE']);w.writeheader();w.writerows(rows)
    print(f"v2.8 localization: {report['localization_status']} {report['german_names_matched']}/{report['quest_count']}")
    if report['localization_status']=='PARSER_UNSUPPORTED':raise SystemExit('German lookup format unrecognized; inspect artifact diagnostics; do not infer zero coverage.')
if __name__=='__main__':main()
