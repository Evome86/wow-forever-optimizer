import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_v35 import has_race,prerequisites,CASES
class TestV35(unittest.TestCase):
 def test_fixtures(self):
  for name,actual,expected in CASES:
   with self.subTest(name=name):self.assertEqual(actual,expected)
 def test_invalid_mask(self):
  with self.assertRaises(ValueError):has_race(-1)
 def test_invalid_prerequisite(self):
  with self.assertRaises(ValueError):prerequisites(group=[0])
if __name__=='__main__':unittest.main()
