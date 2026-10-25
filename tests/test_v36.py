import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_v36 import find_definitions,build
class RuntimeEvidenceTests(unittest.TestCase):
 def test_missing_sources_cannot_pass(self):
  with tempfile.TemporaryDirectory() as d:
   r=build(Path(d)/'addon',Path(d)/'db')
   self.assertEqual(r['original_lua_tests_executed'],0)
   self.assertTrue(r['technical_gate'].startswith('BLOCKED'))
 def test_definition_is_not_execution(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'example.lua').write_text('function QuestiePlayer.HasRequiredRace(mask) return true end\n')
   self.assertEqual(len(find_definitions(root)['HasRequiredRace']),1)
   self.assertEqual(build(root,root)['original_lua_tests_executed'],0)
if __name__=='__main__':unittest.main()
