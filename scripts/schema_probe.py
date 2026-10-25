#!/usr/bin/env python3
"""Read-only QuestieDB Forever schema discovery; no claims of parsed quests."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(os.environ.get('QUESTIEDB_ROOT', 'vendor/QuestieDB'))
OUT = Path(os.environ.get('PROBE_OUTPUT', 'reports/forever-schema-probe.json'))
FILES = [
 'src/meta/questMeta.lua', 'src/meta/npcMeta.lua',
 'src/meta/itemMeta.lua', 'src/meta/objectMeta.lua',
 'data/Forever/foreverQuestDB.lua',
 'data/Forever/foreverNPCDB.lua',
 'data/Forever/foreverObjectDB.lua',
 'support/Forever/QuestXP/xpDB-Classic.lua',
 'docs/api.md', 'docs/forever-validation.md',
]

def scan(rel):
    path = ROOT / rel
    if not path.is_file():
        return {'path': rel, 'exists': False}
    data = path.read_bytes()
    txt = data.decode('utf-8', errors='replace')
    lines = txt.splitlines()
    # Snippets are evidence for manual schema review, not authoritative parsed records.
    if rel.startswith('src/meta/'):
        selected = [(i + 1, line.strip()[:220]) for i, line in enumerate(lines)
                    if re.search(r'\b(keys|name|requiredLevel|minLevel|race|class|faction|xp|startedBy|finishedBy|objectives|spawns)\b', line, re.I)]
        snippets = selected[:100]
    else:
        snippets = [(i + 1, line.strip()[:220]) for i, line in enumerate(lines[:35]) if line.strip()][:20]
    return {'path': rel, 'exists': True, 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(), 'line_count': len(lines),
            'snippets': [{'line': n, 'text': t} for n, t in snippets]}

def main():
    if not ROOT.is_dir():
        raise SystemExit(f'ERROR: QuestieDB checkout missing: {ROOT}')
    entries = [scan(rel) for rel in FILES]
    required = [e for e in entries if e['path'].startswith(('src/meta/', 'data/Forever/'))]
    missing = [e['path'] for e in required if not e['exists']]
    result = {
        'schema_version': 1,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'schema_discovery_only',
        'parsed_quest_count': None,
        'verified_xp': False,
        'verified_eligibility': False,
        'files': entries,
        'missing_required_files': missing,
        'notes': 'Snippets are for inspection only; no Lua is executed and no quests are parsed.',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Schema discovery: {len(entries)} paths checked; {len(missing)} required missing')
    for e in entries:
        print(f"{'OK' if e['exists'] else 'MISSING'} {e['path']}")
    print(f'Report: {OUT}')
    if missing:
        raise SystemExit('ERROR: Required schema/source files missing: ' + ', '.join(missing))

if __name__ == '__main__':
    main()
