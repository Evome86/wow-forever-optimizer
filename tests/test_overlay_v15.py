import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_correction_overlay_v15 import source_blocks,parse_entry,literal
class TestOverlay(unittest.TestCase):
 def test_target_and_nontarget(self):
  s='return {\n [92595] = {\n [questKeys.name] = "The Windshapers",\n [questKeys.startedBy_add] = {{251902}},\n },\n [123] = {\n [questKeys.name] = "other",\n },\n}'
  b=source_blocks(s);self.assertEqual(len(b),1);self.assertEqual(b[0][0],92595)
  f,w=parse_entry(b[0][2]);self.assertEqual(f['startedBy_add'],[[251902]]);self.assertFalse(w)
 def test_expressions_quarantined(self):
  f,w=parse_entry(['[92595] = {','[questKeys.requiredRaces] = raceIDs.SKYBORNE_HORDE + 1,','},'])
  self.assertEqual(f,{});self.assertEqual(w[0]['reason'],'unsupported_expression_or_multiline')
 def test_no_code_execution(self):
  with self.assertRaises(ValueError):literal('os.execute("anything")')
 def test_strings(self):self.assertEqual(literal('{"a", "b"}'),['a','b'])
if __name__=='__main__':unittest.main()
