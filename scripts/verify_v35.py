#!/usr/bin/env python3
"""Conservative reference-model verification. Does NOT execute the WoW client."""
import json, argparse
from pathlib import Path
SKYBORNE_HORDE = 8589934592
SKYBORNE_ALLIANCE = 4294967296

def has_race(mask, flag=SKYBORNE_HORDE):
    if mask is None or mask == 0: return True
    if type(mask) is not int or mask < 0: raise ValueError('invalid race mask')
    return mask % (flag*2) >= flag

def prerequisites(single=None, group=None, completed=(), exclusive=None):
    """Single OR, Group AND; negative group IDs demand exact completion.
    Positive group entries may be fulfilled by completed exclusive alternatives.
    """
    done=set(completed)
    exclusive=exclusive or {}
    def valid_ids(xs):
        if xs is None:return []
        if not isinstance(xs,list) or any(type(i)!=int or i==0 for i in xs):
            raise ValueError('invalid prerequisite representation')
        return xs
    s=valid_ids(single); g=valid_ids(group)
    single_ok=not s or any(q in done for q in s)
    group_ok=all((-q in done if q<0 else (q in done or bool(done.intersection(exclusive.get(q,[]))))) for q in g)
    return single_ok and group_ok

CASES=[
 ('race_unrestricted_none',has_race(None),True),
 ('race_unrestricted_zero',has_race(0),True),
 ('race_horde',has_race(SKYBORNE_HORDE),True),
 ('race_alliance',has_race(SKYBORNE_ALLIANCE),False),
 ('race_both',has_race(SKYBORNE_HORDE+SKYBORNE_ALLIANCE),True),
 ('race_other_low_bit',has_race(1),False),
 ('race_horde_with_low_bit',has_race(SKYBORNE_HORDE+1),True),
 ('race_horde_with_higher_bit',has_race(SKYBORNE_HORDE+17179869184),True),
 ('prereq_empty',prerequisites(),True),
 ('single_or_pass',prerequisites([101,102],completed=[102]),True),
 ('single_or_fail',prerequisites([101,102],completed=[103]),False),
 ('group_and_pass',prerequisites(group=[101,102],completed=[101,102]),True),
 ('group_and_fail',prerequisites(group=[101,102],completed=[101]),False),
 ('combined_pass',prerequisites([101,102],[201,202],[102,201,202]),True),
 ('combined_fail',prerequisites([101,102],[201,202],[102,201]),False),
 ('negative_group_exact_pass',prerequisites(group=[-101],completed=[101]),True),
 ('negative_group_exact_fail',prerequisites(group=[-101],completed=[102],exclusive={101:[102]}),False),
 ('positive_group_exclusive_pass',prerequisites(group=[101],completed=[102],exclusive={101:[102]}),True),
 ('positive_group_exclusive_fail',prerequisites(group=[101],completed=[103],exclusive={101:[102]}),False),
]
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='reports/forever-v35-reference-harness.json');args=p.parse_args()
    failed=[n for n,actual,expected in CASES if actual!=expected]
    report={'version':'3.5','type':'offline_reference_model','tests':[{'name':n,'pass':a==e} for n,a,e in CASES],
            'passed':len(CASES)-len(failed),'failed':failed,
            'source_evidence':{'race':'v3.4 QuestiePlayer.HasRequiredRace: modulo arithmetic',
                               'prerequisites':'v3.4 QuestieDB:IsPreQuestGroupFulfilled / IsPreQuestSingleFulfilled excerpts'},
            'limitations':['Not execution of Questie addon code','ExclusiveTo alternative semantics require direct source confirmation','Not tested in Forever game client','No quest eligibility certified'],
            'route_gate':'BLOCKED_RUNTIME_AND_INGAME_VALIDATION'}
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'failed':failed,'route_gate':report['route_gate']}))
    if failed:raise SystemExit(1)
if __name__=='__main__':main()
