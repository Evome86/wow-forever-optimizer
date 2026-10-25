import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_v30 import refs,audit,PIN
class Tests(unittest.TestCase):
 def test_refs(self):
  self.assertEqual(refs({'1':92860,'2':92871}),[92860,92871]);self.assertEqual(refs(None),[])
 def test_reject_wrong_commit(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'quests.json';p.write_text(json.dumps({'upstream_commit':'wrong','quests':{}}))
   with self.assertRaises(ValueError):audit(Path(d),p)
 def test_language_is_display_only(self):
  src=(Path(__file__).resolve().parents[1]/'web/quest-language.js').read_text()
  self.assertIn('forever:language-changed',src)
  self.assertNotIn('calculateRoute(',src)
if __name__=='__main__':unittest.main()
