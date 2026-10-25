import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_starter_v14 import audit,TARGETS
class StarterTests(unittest.TestCase):
 def test_exact_numeric_boundaries_and_provenance(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'src/corrections/Forever').mkdir(parents=True)
   (root/'src/corrections/Forever/foreverQuestFixes.lua').write_text('[92595] = { -- Skyborne\n  [questKeys.requiredRaces] = 8589934592\n}\n-- 192595 must not match\n',encoding='utf-8')
   result=audit(root,{'source_sha256':'test','quests':{'92596':{}}})
   self.assertEqual(result['target_quests'][0]['source_hit_lines'],1)
   self.assertFalse(result['target_quests'][0]['present_in_raw_import'])
   self.assertTrue(result['target_quests'][1]['present_in_raw_import'])
   self.assertFalse(result['corrections']['patches_applied'])
   self.assertIn('sha256',result['evidence'][0])
 def test_no_unsupported_promotion(self):
  with tempfile.TemporaryDirectory() as d:
   r=audit(Path(d),{'quests':{}})
   self.assertFalse(r['runtime_quest_availability_verified'])
   self.assertEqual(len(r['target_quests']),len(TARGETS))
if __name__=='__main__':unittest.main()
