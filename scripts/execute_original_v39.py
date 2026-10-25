#!/usr/bin/env python3
"""Run unmodified extracted Questie Lua function bodies; fail closed on missing dependencies."""
import argparse, json, re, subprocess, tempfile
from pathlib import Path
from verify_v35 import CASES, SKYBORNE_HORDE, SKYBORNE_ALLIANCE

FUNCTIONS = {
 'race': ('Modules/QuestiePlayer.lua', r'^\s*function\s+QuestiePlayer\.HasRequiredRace\s*\('),
 'single': ('Database/QuestieDB.lua', r'^\s*function\s+QuestieDB:IsPreQuestSingleFulfilled\s*\('),
 'group': ('Database/QuestieDB.lua', r'^\s*function\s+QuestieDB:IsPreQuestGroupFulfilled\s*\('),
}

def lua_literal(value):
 if value is None: return 'nil'
 if isinstance(value,bool): return 'true' if value else 'false'
 if isinstance(value,(int,float)): return str(value)
 if isinstance(value,(list,tuple)): return '{'+','.join(lua_literal(v) for v in value)+'}'
 if isinstance(value,dict): return '{'+','.join('['+lua_literal(k)+']='+lua_literal(v) for k,v in sorted(value.items()))+'}'
 raise ValueError(value)

def extract_start(path,pattern):
 if not path.is_file(): raise FileNotFoundError(str(path))
 lines=path.read_text(encoding='utf-8',errors='replace').splitlines()
 hits=[i for i,line in enumerate(lines) if re.search(pattern,line)]
 if len(hits)!=1: raise ValueError(f'{path}: expected exactly one definition, got {len(hits)}')
 return hits[0]+1

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--addon',default='vendor/Questie')
 p.add_argument('--out',default='reports/forever-v39-original-lua.json')
 p.add_argument('--commit-file',default='addon-commit-v39.txt')
 p.add_argument('--lua',default='lua5.1')
 p.add_argument('--source-evidence',default='reports/forever-v39-source-context.json')
 args=p.parse_args()
 addon=Path(args.addon); results=[]; definitions={}; failures=[]
 for key,(rel,pattern) in FUNCTIONS.items():
  path=addon/rel
  try: definitions[key]={'path':str(path),'line':extract_start(path,pattern)}
  except Exception as exc: failures.append(f'{key}: {exc}')
 commit=Path(args.commit_file).read_text().strip() if Path(args.commit_file).exists() else None
 if not failures:
  # These are *inputs* to the original functions, not replacement implementations.
  # WoW APIs not explicitly mocked remain undefined and cause a BLOCKED test.
  cases=[
   ('race_unrestricted_none','race',None,[],{}),('race_unrestricted_zero','race',0,[],{}),
   ('race_horde','race',SKYBORNE_HORDE,[],{}),('race_alliance','race',SKYBORNE_ALLIANCE,[],{}),
   ('race_both','race',SKYBORNE_HORDE+SKYBORNE_ALLIANCE,[],{}),
   ('race_other_low_bit','race',1,[],{}),
   ('race_horde_with_low_bit','race',SKYBORNE_HORDE+1,[],{}),
   ('race_horde_with_higher_bit','race',SKYBORNE_HORDE+17179869184,[],{}),
   ('prereq_empty','both',([],[]),[],{}),
   ('single_or_pass','single',[101,102],[102],{}),
   ('single_or_fail','single',[101,102],[103],{}),
   ('group_and_pass','group',[101,102],[101,102],{}),
   ('group_and_fail','group',[101,102],[101],{}),
   ('combined_pass','both',([101,102],[201,202]),[102,201,202],{}),
   ('combined_fail','both',([101,102],[201,202]),[102,201],{}),
   ('negative_group_exact_pass','group',[-101],[101],{}),
   ('negative_group_exact_fail','group',[-101],[102],{101:[102]}),
   ('positive_group_exclusive_pass','group',[101],[102],{101:[102]}),
   ('positive_group_exclusive_fail','group',[101],[103],{101:[102]}),
  ]
  assert [x[0] for x in cases]==[x[0] for x in CASES]
  lines=["local unpack=unpack", "local function extract(path,start)",
   " local f=assert(io.open(path,'r')); local lines={}; for line in f:lines() do lines[#lines+1]=line end; f:close()",
   " local source=''; for i=start,#lines do", "  source=source..lines[i]..'\\n'",
   "  local prefix='local playerRaceFlag=8589934592; local playerRaceFlagX2=2*playerRaceFlag\\n'",
   "  local fn,err=loadstring(prefix..source,'@'..path..':'..start)",
   "  if fn then return fn end",
   "  if not string.find(err or '','<eof>',1,true) then error(err) end",
   " end; error('incomplete function: '..path)","end",
   "QuestiePlayer={}; QuestieDB={}; Questie={db={char={complete={}}}}",
   "-- These are controlled inputs to the ORIGINAL functions, not replacements for their logic.",
   "local playerRaceFlag=8589934592",
   "local playerRaceFlagX2=2*playerRaceFlag",
   "local function report(name,status,value)",
   " local v=tostring(value or ''):gsub('[\\r\\n\\t]',' ')",
   " io.write(name..'\\t'..status..'\\t'..v..'\\n') end",
   ]
  for key in FUNCTIONS:
   d=definitions[key]
   lines.append(f"local ok_{key},err_{key}=pcall(extract({lua_literal(str(d['path'])) if False else '['+'=['+str(d['path'])+']=]'}, {d['line']}))")
   lines.append(f"if not ok_{key} then io.stderr:write('{key} load: '..tostring(err_{key})..'\\n') end")
  # Minimal known interfaces. Missing real dependencies must produce an error, not a substituted result.
  lines += ["QuestieDB.QueryQuestSingle=function(id,field) if field=='exclusiveTo' then return QuestieDB.exclusives[id] end error('Unexpected QueryQuestSingle field: '..tostring(field)) end",
   "local function reset(done,exclusives)",
    " QuestiePlayer.raceId=96; QuestiePlayer.race=96; QuestiePlayer.raceMask=8589934592",
    " Questie.db.char.complete={}; for _,id in ipairs(done) do Questie.db.char.complete[id]=true end",
    " QuestieDB.exclusives=exclusives",
    "end",
    "local function execute(kind,value)",
    " if kind=='race' then return QuestiePlayer.HasRequiredRace(value) end",
    " if kind=='single' then return QuestieDB:IsPreQuestSingleFulfilled(value) end",
    " if kind=='group' then return QuestieDB:IsPreQuestGroupFulfilled(value) end",
    " return QuestieDB:IsPreQuestSingleFulfilled(value[1]) and QuestieDB:IsPreQuestGroupFulfilled(value[2]) end",
   ]
  for name,kind,val,done,exclusive in cases:
   literal='{'+lua_literal(val[0])+','+lua_literal(val[1])+'}' if kind=='both' else lua_literal(val)
   lines += [f"reset({lua_literal(done)},{lua_literal(exclusive)})",f"do local ok,result=pcall(execute,'{kind}',{literal})",
             f" if ok and type(result)=='boolean' then report('{name}','EXECUTED',result) else report('{name}',ok and 'NON_BOOLEAN' or 'ERROR',result) end end"]
  script='\n'.join(lines)+'\n'
  try:
   with tempfile.TemporaryDirectory() as tmp:
    runner=Path(tmp)/'runner.lua';runner.write_text(script)
    proc=subprocess.run([args.lua,str(runner)],capture_output=True,text=True,timeout=40)
   output={}
   for row in proc.stdout.splitlines():
    parts=row.split('\t',2)
    if len(parts)==3: output[parts[0]]=parts[1:]
   for name,expected,unused in CASES:
    status,value=output.get(name,('NOT_RUN','no result'))
    actual={'true':True,'false':False}.get(value) if status=='EXECUTED' else None
    results.append({'name':name,'reference_expected':unused,'lua_status':status,
                    'lua_actual':actual,'parity':actual==unused if actual is not None else None,
                    'error':value if status!='EXECUTED' else None})
   if proc.returncode: failures.append(f'Lua exited {proc.returncode}: {proc.stderr[:1500]}')
   elif proc.stderr: failures.append('Lua loader warnings: '+proc.stderr[:1500])
  except Exception as exc: failures.append(f'Lua execution failed: {exc}')
 executed=sum(x['lua_status']=='EXECUTED' for x in results)
 mismatches=[x['name'] for x in results if x['parity'] is False]
 gate='PASS_ISOLATED_FUNCTION_PARITY_ONLY' if executed==19 and not mismatches and not failures else 'BLOCKED_INCOMPLETE_OR_MISMATCH'
 report={'version':'3.9','type':'source_verified_isolated_lua_execution','addon_commit':commit,
         'definitions':definitions,'tests':results,'executed':executed,'total':19,
         'mismatches':mismatches,'errors':failures + [t['name']+': '+str(t['error']) for t in results if t['lua_status'] != 'EXECUTED'],'runtime_error_count':sum(t['lua_status'] in ('ERROR','NON_BOOLEAN','NOT_RUN') for t in results),'technical_gate':gate,
         'ingame_gate':'BLOCKED_NOT_VERIFIED','route_gate':'BLOCKED',
         'mock_inputs':{'playerRaceFlag':8589934592,'playerRaceFlagX2':17179869184,'Questie.db.char.complete':'controlled completed quest IDs','QuestieDB.QueryQuestSingle':'exclusiveTo field only'},'mock_provenance':'SOURCE_STRUCTURES_CONFIRMED_VALUES_TEST_INPUTS','limitations':['Executes original extracted function bodies under isolated local variables and completion-state mocks; not full addon initialization.',
           'Lua local race flag is a test input derived from Skyborne Horde bit; actual player initialization and class selection not executed.',
           'Questie addon commit not proven identical to Forever client addon.',
           'No quest availability or actual game behavior certified.']}
 source_context=Path(args.source_evidence)
 if source_context.exists():report['source_context_file']=str(source_context)
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'executed':executed,'mismatches':len(mismatches),'errors':len(failures),'technical_gate':gate}))
 # A blocked evidence report is a valid workflow output, not a passing technical gate.
if __name__=='__main__':main()
