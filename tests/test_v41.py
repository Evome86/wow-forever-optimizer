import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_isdoable_v41 import audit
class AuditTest(unittest.TestCase):
 def test_extract_and_fail_closed(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.lua';p.write_text('function QuestieDB.IsDoable(id)\n if completedQuests[id] then return false end\n return true\nend\nfunction Other() end\n')
   r=audit(p,'a','b');self.assertEqual(r['source_start_line'],1);self.assertEqual(r['source_end_line'],4);self.assertFalse(r['isdoable_executed']);self.assertEqual(r['route_gate'],'BLOCKED');self.assertTrue(r['condition_evidence']['completed'])
 def test_missing_definition(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.lua';p.write_text('function Else() end')
   with self.assertRaises(ValueError):audit(p)
 def test_gui_guardrails(self):
  html=(Path(__file__).resolve().parents[1]/'web/optimizer.html').read_text();js=(Path(__file__).resolve().parents[1]/'web/optimizer.js').read_text()
  self.assertIn('ROUTE GESPERRT',html);self.assertIn('NICHT VERIFIZIERT',js)
if __name__=='__main__':unittest.main()
