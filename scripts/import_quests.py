#!/usr/bin/env python3
"""Strict, non-executing Lua table importer for QuestieDB's generated Forever quest data."""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path('vendor/QuestieDB/data/Forever/foreverQuestDB.lua')
OUTPUT = Path('reports/forever-quests.json')
REPORT = Path('reports/forever-import-report.json')
MAX_BYTES = 25_000_000

class ParseError(ValueError):
    pass

class Lexer:
    def __init__(self, text):
        self.s = text
        self.i = 0
        self.n = len(text)

    def next(self):
        s, n = self.s, self.n
        while self.i < n:
            if s[self.i].isspace():
                self.i += 1
                continue
            if s.startswith('--', self.i):
                end = s.find('\n', self.i)
                self.i = n if end == -1 else end + 1
                continue
            break
        if self.i >= n:
            return ('EOF', None)
        c = s[self.i]
        if c in '{}[]=,;':
            self.i += 1
            return (c, c)
        if c in ('"', "'"):
            quote = c
            start = self.i
            self.i += 1
            value = []
            while self.i < n:
                c = s[self.i]
                self.i += 1
                if c == quote:
                    return ('STRING', ''.join(value))
                if c == '\\':
                    if self.i >= n:
                        raise ParseError('Unterminated escape')
                    escaped = s[self.i]
                    self.i += 1
                    value.append({'n':'\n','r':'\r','t':'\t','\\':'\\','"':'"',"'":"'"}.get(escaped, escaped))
                else:
                    value.append(c)
            raise ParseError(f'Unterminated string at {start}')
        m = re.match(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?', s[self.i:])
        if m:
            self.i += len(m.group())
            val = m.group()
            return ('NUMBER', float(val) if any(x in val for x in '.eE') else int(val))
        m = re.match(r'[A-Za-z_][A-Za-z0-9_]*', s[self.i:])
        if m:
            self.i += len(m.group())
            return ('IDENT', m.group())
        raise ParseError(f'Unsupported Lua token at offset {self.i}: {s[self.i:self.i+35]!r}')

class Parser:
    def __init__(self, s):
        self.lexer = Lexer(s)
        self.t = self.lexer.next()
        self.count = 0
    def take(self, kind):
        if self.t[0] != kind:
            raise ParseError(f'Expected {kind}, got {self.t!r} near offset {self.lexer.i}')
        val = self.t[1]
        self.t = self.lexer.next()
        return val
    def value(self, depth=0):
        if depth > 80:
            raise ParseError('Maximum nesting exceeded')
        kind, val = self.t
        if kind == '{':
            return self.table(depth+1)
        if kind in ('NUMBER', 'STRING'):
            self.take(kind)
            return val
        if kind == 'IDENT' and val in ('nil', 'true', 'false'):
            self.take('IDENT')
            return {'nil': None, 'true': True, 'false': False}[val]
        raise ParseError(f'Unsupported expression {self.t!r} near offset {self.lexer.i}')
    def table(self, depth):
        self.take('{')
        arr = []
        keyed = {}
        while self.t[0] != '}':
            if self.t[0] == 'EOF':
                raise ParseError('Unterminated table')
            if self.t[0] == '[':
                self.take('[')
                key = self.value(depth)
                self.take(']')
                self.take('=')
                val = self.value(depth)
                if not isinstance(key, (int, str)):
                    raise ParseError('Invalid table key')
                if key in keyed:
                    raise ParseError(f'Duplicate keyed entry {key}')
                keyed[key] = val
            elif self.t[0] == 'IDENT':
                # Lua name=value fields (not arbitrary executable expressions).
                key = self.take('IDENT')
                self.take('=')
                if key in keyed:
                    raise ParseError(f'Duplicate keyed entry {key}')
                keyed[key] = self.value(depth)
            else:
                arr.append(self.value(depth))
            self.count += 1
            if self.count > 3_000_000:
                raise ParseError('Maximum field count exceeded')
            if self.t[0] in (',', ';'):
                self.take(self.t[0])
            elif self.t[0] != '}':
                raise ParseError(f'Expected separator, got {self.t!r}')
        self.take('}')
        if not keyed:
            return arr
        for i, val in enumerate(arr, 1):
            if i in keyed:
                raise ParseError(f'Conflicting implicit array index {i}')
            keyed[i] = val
        return keyed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=SOURCE)
    ap.add_argument('--output', type=Path, default=OUTPUT)
    ap.add_argument('--report', type=Path, default=REPORT)
    args = ap.parse_args()
    report = {'schema_version': 1, 'generated_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'failed', 'source': str(args.source), 'quest_count': 0,
              'verified_xp': False, 'verified_eligibility': False, 'warnings': []}
    try:
        raw = args.source.read_bytes()
        if len(raw) > MAX_BYTES:
            raise ParseError('Source exceeds size limit')
        source = raw.decode('utf-8')
        report['source_sha256'] = hashlib.sha256(raw).hexdigest()
        # Only data between QuestieDB.questData = [[return { ... }]] is parsed.
        match = re.search(r'QuestieDB\.questData\s*=\s*\[\[\s*return\s*', source)
        if not match:
            raise ParseError('Could not locate QuestieDB.questData = [[return ...]]; inspect actual upstream format')
        end = source.find(']]', match.end())
        if end < 0:
            raise ParseError('Unclosed questData Lua long string')
        data = source[match.end():end]
        parser = Parser(data)
        quests = parser.value()
        if parser.t[0] != 'EOF':
            raise ParseError('Unexpected trailing data in questData')
        if not isinstance(quests, dict):
            raise ParseError('Quest data must be a keyed Lua table')
        output = {}
        errors = []
        for qid, fields in quests.items():
            if not isinstance(qid, int) or qid <= 0 or not isinstance(fields, (list, dict)):
                errors.append(f'Invalid quest ID or record: {qid!r}')
                continue
            def field(index):
                if isinstance(fields, list):
                    return fields[index-1] if len(fields) >= index else None
                return fields.get(index)
            output[str(qid)] = {
                'id': qid, 'name': field(1), 'started_by_raw': field(2),
                'finished_by_raw': field(3), 'required_level': field(4),
                'quest_level': field(5), 'required_races_mask': field(6),
                'required_classes_mask': field(7), 'objectives_raw': field(10),
                'prerequisites_raw': {str(i): field(i) for i in (12, 13, 14, 15, 16)},
                'source': 'QuestieDB/data/Forever/foreverQuestDB.lua',
            }
        if errors:
            raise ParseError('; '.join(errors[:10]))
        if not output:
            raise ParseError('No quests parsed')
        report['quest_count'] = len(output)
        report['warnings'].append('Quest XP, prerequisite semantics, race/class masks and availability are NOT verified.')
        report['status'] = 'parsed_unverified'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({'schema_version': 1, 'source_sha256': report['source_sha256'],
                            'quests': output}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Parsed {len(output)} quest records (NOT gameplay-validated).')
    except (OSError, UnicodeError, ParseError) as e:
        report['error'] = str(e)
        print(f'IMPORT FAILED: {e}', file=sys.stderr)
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Report: {args.report}')
    return 0 if report['status'] == 'parsed_unverified' else 1

if __name__ == '__main__':
    sys.exit(main())
