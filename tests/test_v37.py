import unittest
from scripts.execute_original_v37 import FUNCTIONS, extract_start
from pathlib import Path
import tempfile
class V37Tests(unittest.TestCase):
 def test_all_functions_have_unique_targets(self):
  self.assertEqual(len(FUNCTIONS),3)
  self.assertEqual(len({v[0] for v in FUNCTIONS.values()}),2)
 def test_exact_definition(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'t.lua';p.write_text('function QuestiePlayer.HasRequiredRace(requiredRaces)\n return true\nend\n')
   self.assertEqual(extract_start(p,FUNCTIONS['race'][1]),1)
 def test_missing_source_fails(self):
  with self.assertRaises(FileNotFoundError):extract_start(Path('/missing/questie.lua'),FUNCTIONS['race'][1])
