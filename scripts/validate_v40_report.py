#!/usr/bin/env python3
"""Validate all original Lua comparisons; never confuse JSON null with false."""
import argparse, json
from pathlib import Path

def validate(report):
    tests=report.get('tests',[])
    errors=[]
    if len(tests)!=19: errors.append('expected 19 tests')
    if len({t.get('name') for t in tests})!=len(tests): errors.append('duplicate test names')
    for t in tests:
        name=t.get('name','?')
        if t.get('lua_status')!='EXECUTED': errors.append(f'{name}: not executed')
        if type(t.get('lua_actual')) is not bool: errors.append(f'{name}: result not boolean')
        if type(t.get('reference_expected')) is not bool: errors.append(f'{name}: reference not boolean')
        if t.get('parity') is not True: errors.append(f'{name}: parity not confirmed')
        if type(t.get('lua_actual')) is bool and type(t.get('reference_expected')) is bool and t['lua_actual'] is not t['reference_expected']:
            errors.append(f'{name}: actual mismatch')
    if report.get('runtime_error_count')!=0: errors.append('runtime errors')
    if report.get('errors'): errors.append('reported errors')
    if report.get('mismatches'): errors.append('reported mismatches')
    if report.get('unresolved'): errors.append('unresolved results')
    if report.get('confirmed_parity_count')!=19: errors.append('confirmed parity count != 19')
    if report.get('technical_gate')!='PASS_ISOLATED_FUNCTION_PARITY_ONLY': errors.append('technical gate not passed')
    if report.get('route_gate')!='BLOCKED': errors.append('route gate must remain blocked')
    if report.get('ingame_gate')!='BLOCKED_NOT_VERIFIED': errors.append('ingame gate must remain blocked')
    return errors

def main():
    p=argparse.ArgumentParser();p.add_argument('report');a=p.parse_args()
    errors=validate(json.loads(Path(a.report).read_text()))
    print(json.dumps({'validation':'PASS' if not errors else 'BLOCKED','errors':errors},indent=2))
    if errors: raise SystemExit(1)
if __name__=='__main__':main()
