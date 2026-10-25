#!/usr/bin/env python3
"""Skyborne evidence discovery; deliberately does not infer race bits from large masks."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

TERMS = ('skyborne', 'windshaper', 'zephras', 'high order')
SUFFIXES = {'.lua', '.md', '.txt', '.json', '.xml', '.toc'}

def discover(quest_data, root, max_bytes=3_000_000):
    quests = quest_data['quests']
    matches = []
    for qid, quest in quests.items():
        name = str(quest.get('name') or '')
        found = [t for t in TERMS if t in name.casefold()]
        if found:
            matches.append({'quest_id': int(qid), 'name': name, 'terms': found,
                            'required_races_mask': quest.get('required_races_mask'),
                            'required_classes_mask': quest.get('required_classes_mask'),
                            'required_level': quest.get('required_level')})
    references = []
    scanned = 0
    skipped_large = 0
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        if any(p in ('.git', 'node_modules') for p in path.parts):
            continue
        if path.stat().st_size > max_bytes:
            skipped_large += 1
            continue
        scanned += 1
        try:
            with path.open('r', encoding='utf-8', errors='replace') as f:
                for number, line in enumerate(f, 1):
                    found = [t for t in TERMS if t in line.casefold()]
                    if found:
                        references.append({'file': str(path.relative_to(root)), 'line': number,
                                           'terms': found, 'excerpt': line.strip()[:300]})
                        if len(references) >= 250:
                            break
        except OSError:
            continue
        if len(references) >= 250:
            break
    masks = Counter(str(q.get('required_races_mask')) for q in quests.values()
                    if isinstance(q.get('required_races_mask'), int) and not isinstance(q.get('required_races_mask'), bool))
    high = {k: v for k, v in masks.items() if int(k) > 2**32-1}
    return {
        'schema_version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'character': {'race': 'Skyborne', 'variant': 'Windshaper Skyborne', 'faction': 'Horde',
                      'class': 'Druid', 'specialization_goal': 'Balance', 'level_target': 30,
                      'status': 'user_selected_not_source_verified'},
        'quest_count': len(quests), 'quest_name_matches': matches,
        'source_text_matches': references,
        'source_files_scanned': scanned, 'source_files_skipped_oversize': skipped_large,
        'matches_truncated': len(references) >= 250,
        'race_masks_over_u32': high,
        'unknowns': [
            'Skyborne race ID and faction-specific race bit are not established',
            'Skyborne starting zone, quest availability and class restrictions are not established',
            'Quest XP, travel and combat timings are not verified',
            'No eligibility filter or route is safe to publish yet'],
        'release_gate': 'BLOCKED: source mentions are not proof of playable Skyborne eligibility'
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, default=Path('reports/forever-quests.json'))
    ap.add_argument('--source-root', type=Path, default=Path('vendor/QuestieDB'))
    ap.add_argument('--output', type=Path, default=Path('reports/forever-skyborne-v07.json'))
    args = ap.parse_args()
    if not args.source_root.is_dir():
        ap.error('Source root missing; check pinned QuestieDB checkout')
    data = json.loads(args.input.read_text(encoding='utf-8'))
    report = discover(data, args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Quests:', report['quest_count'], '| matching quest names:', len(report['quest_name_matches']),
          '| source matches:', len(report['source_text_matches']))
    print(report['release_gate'])

if __name__ == '__main__':
    main()
