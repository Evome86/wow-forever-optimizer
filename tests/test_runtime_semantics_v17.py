import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_runtime_semantics_v17 import extract_blocks,build
class TestV17(unittest.TestCase):
 def test_quest_block(self):
  s='[94414] = {\n [questKeys.requiredRaces] = raceIDs.NONE,\n},\n'
  self.assertEqual(extract_blocks(s,{94414})[0]['end_line'],3)
 def test_gate_and_race_definition(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'src/raceConstants.lua';p.parent.mkdir(parents=True);p.write_text('SKYBORNE_HORDE = 8589934592,\n')
   x=build(root);self.assertTrue(x['race_declaration_candidates']);self.assertIn('BLOCKED',x['release_gate']);self.assertTrue(x['errors'])
 def test_no_unrelated_none_noise(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'src/npcFixes.lua';p.parent.mkdir(parents=True);p.write_text('npcFlags.NONE = 0\n')
   self.assertEqual(build(d)['race_declaration_candidates'],[])
if __name__=='__main__':unittest.main()
