#!/usr/bin/env python3
"""Execute upstream QuestieDB native-source tests, retaining unabridged logs."""
import datetime,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'vendor/QuestieDB'
OUT=ROOT/'reports'
OUT.mkdir(exist_ok=True)
report={'version':'1.8','generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'test_file':'emulator/native-source.test.lua','runtime_verified':False}
try:
    if not (SOURCE/'emulator/native-source.test.lua').is_file():
        raise FileNotFoundError('QuestieDB emulator/native-source.test.lua missing')
    cmd=['lua5.1','emulator/native-source.test.lua']
    p=subprocess.run(cmd,cwd=SOURCE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180,errors='replace')
    report.update(command=cmd,exit_code=p.returncode, runtime_verified=p.returncode==0, log_file='reports/forever-runtime-v18.log')
    (OUT/'forever-runtime-v18.log').write_text(p.stdout,encoding='utf-8')
    print(p.stdout[-14000:])
except Exception as exc:
    report.update(error=f'{type(exc).__name__}: {exc}',exit_code=1)
(OUT/'forever-runtime-v18.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
sys.exit(0 if report['runtime_verified'] else 1)

