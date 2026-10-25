#!/usr/bin/env python3
"""Conservative candidate classification; not proof of quest availability."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

HORDE_SKYBORNE = 1 << 33
ALLIANCE_SKYBORNE = 1 << 32
DRUID = 1024


def classify(q, max_level=30):
    race = q.get('required_races_mask')
    cls = q.get('required_classes_mask')
    level = q.get('required_level')
    quest_level = q.get('quest_level')
    if not isinstance(race, int) or isinstance(race, bool) or race < 0:
        return 'unknown_race_mask', 'race mask missing or invalid'
    if race != 0 and not (race & HORDE_SKYBORNE):
        return 'excluded_race', 'Horde Skyborne bit absent from nonzero race mask'
    if cls is not None:
        if not isinstance(cls, int) or isinstance(cls, bool) or cls < 0:
            return 'unknown_class_mask', 'class mask invalid'
        if cls != 0 and not (cls & DRUID):
            return 'excluded_class', 'Druid bit absent from nonzero class mask'
    if not isinstance(level, int) or isinstance(level, bool) or level < 0:
        return 'unknown_required_level', 'requiredLevel missing or invalid'
    if level > max_level:
        return 'excluded_required_level', 'requiredLevel above target'
    if quest_level is not None and (not isinstance(quest_level, int) or isinstance(quest_level, bool) or quest_level < 0):
        return 'candidate_special_quest_level', 'questLevel is a special or invalid value; requires review'
    return 'candidate_unverified', 'raw mask/requiredLevel checks passed; no correction, availability or prerequisite verification'


def build_report(data, max_level=30):
    quests = data['quests']
    results = []
    counts = Counter()
    for qid, q in sorted(quests.items(), key=lambda pair: int(pair[0])):
        status, reason = classify(q, max_level)
        counts[status] += 1
        results.append({'id': int(qid), 'name': q.get('name'), 'status': status, 'reason': reason,
                        'required_level': q.get('required_level'), 'quest_level': q.get('quest_level'),
                        'required_races_mask': q.get('required_races_mask'),
                        'required_classes_mask': q.get('required_classes_mask'),
                        'prerequisites_raw': q.get('prerequisites_raw')})
    return {'schema_version': 1, 'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'source_sha256': data.get('source_sha256'),
            'character': {'race': 'Windshaper Skyborne', 'faction': 'Horde', 'race_id': 96,
                          'race_bit': HORDE_SKYBORNE, 'class': 'Druid', 'class_bit': DRUID,
                          'specialization_goal': 'Balance', 'target_level': max_level},
            'quest_count': len(quests), 'counts': dict(sorted(counts.items())),
            'quest_candidates': [r for r in results if r['status'].startswith('candidate_')],
            'exceptions_sample': [r for r in results if not r['status'].startswith('candidate_')][:80],
            'semantics': {'zero_race_mask': 'treated as unrestricted ONLY for preliminary screening',
                          'missing_class_mask': 'treated as unrestricted ONLY for preliminary screening',
                          'required_level': 'minimum acceptance level, NOT quest level or route order',
                          'quest_level': 'not used as a hard exclusion for level <= target',
                          'corrections': 'NOT applied: baked source vs runtime corrections require separate validation',
                          'prerequisites': 'NOT evaluated',
                          'zone': 'NOT inferred from quest names or faction mask',
                          'xp': 'NOT verified'},
            'release_gate': 'BLOCKED: candidates are not verified playable quests and not an optimized route'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, default=Path('reports/forever-quests.json'))
    ap.add_argument('--output', type=Path, default=Path('reports/forever-skyborne-v08.json'))
    args = ap.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    report = build_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Quests:', report['quest_count'], '| counts:', report['counts'])
    print(report['release_gate'])

if __name__ == '__main__':
    main()
