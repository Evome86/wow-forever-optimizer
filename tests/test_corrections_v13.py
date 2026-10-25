import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_corrections_v13 import raw_quests, field, build, EXPECTED_SHA

class CorrectionTests(unittest.TestCase):
    def test_extract_raw_fields(self):
        row=[None]*28
        row[21]=123;row[24]=[456];row[26]=789;row[27]=[100,101]
        text='QuestieDB.questData = [[return {[7]={' + ','.join('nil' if v is None else ('{' + ','.join(map(str,v)) + '}' if isinstance(v,list) else str(v)) for v in row) + '}}]]'
        data=raw_quests(text)
        self.assertEqual(field(data[7],22),123)
        self.assertEqual(field(data[7],25),[456])
        self.assertEqual(field(data[7],27),789)
        self.assertEqual(field(data[7],28),[100,101])
    def test_fail_closed_sha(self):
        with self.assertRaises(ValueError):build({'source_sha256':'bad','quests':{}},b'',b'')
    def test_no_patch_execution(self):
        import hashlib
        # Verify expected SHA is checked BEFORE parsing any correction.
        with self.assertRaises(ValueError):build({'source_sha256':EXPECTED_SHA,'quests':{}},b'wrong',b'[7] = {[questKeys.requiredRaces]=99}')
if __name__=='__main__':unittest.main()
