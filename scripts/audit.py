#!/usr/bin/env python3
"""Inventory QuestieDB Forever source candidates; not a quest parser."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

root = Path(os.environ.get('QUESTIEDB_ROOT', 'vendor/QuestieDB'))
if not root.is_dir():
    raise SystemExit(f'Missing QuestieDB checkout: {root}')
files = []
for path in sorted(root.rglob('*')):
    if not path.is_file() or '.git' in path.parts:
        continue
    relative = path.relative_to(root).as_posix()
    if 'forever' not in relative.lower() and 'camelot' not in relative.lower():
        continue
    data = path.read_bytes()
    files.append({'path': relative, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
if not files:
    raise SystemExit('No Forever/Camelot-named files found; audit cannot proceed.')
output = {
    'schema_version': 1,
    'source': 'Questie/QuestieDB',
    'source_commit': os.environ.get('QUESTIEDB_COMMIT', 'unknown'),
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'status': 'inventory_only',
    'verified_quest_count': None,
    'verified_xp_curve': False,
    'verified_class_race_faction_rules': False,
    'verified_travel_graph': False,
    'candidate_file_count': len(files),
    'files': files,
}
out = Path('data/source-audit.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Audited {len(files)} Forever/Camelot candidate files at {output}')
