import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_runtime_semantics_v17 import extract_blocks,build

class TestV17(unittest.TestCase):
    def fixture(self,root):
        for name in ('src/corrections/Forever/generated/foreverBaseQuest.lua','src/corrections/Forever/foreverQuestFixes.lua'):
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('[94414] = {\n [questKeys.requiredRaces] = raceIDs.NONE,\n},\n')
    def test_quest_block(self):
        s='[94414] = {\n [questKeys.requiredRaces] = raceIDs.NONE,\n},\n'
        self.assertEqual(extract_blocks(s,{94414})[0]['end_line'],3)
    def test_gate_and_race_definition(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            p=root/'src/raceConstants.lua';p.write_text('SKYBORNE_HORDE = 8589934592,\n')
            x=build(root);self.assertTrue(x['race_declaration_candidates']);self.assertIn('BLOCKED',x['release_gate']);self.assertFalse(x['errors'])
    def test_no_unrelated_none_noise(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            p=root/'src/npcFixes.lua';p.write_text('npcFlags.NONE = 0\n')
            self.assertEqual(build(root)['race_declaration_candidates'],[])
    def test_missing_files_fail_fast(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'a.lua').write_text('x=1')
            with self.assertRaisesRegex(RuntimeError,'Missing required'):build(root)
    def test_vendor_path_is_not_filtered(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'vendor/QuestieDB';self.fixture(root)
            self.assertGreater(build(root)['source_file_count'],0)
if __name__=='__main__':unittest.main()
