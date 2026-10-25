import unittest,tempfile
from pathlib import Path
from scripts.audit_semantics_v34 import build,scan
class TestV34(unittest.TestCase):
 def test_missing_source_does_not_certify(self):
  r=build(Path('/no/db'),Path('/no/addon'))
  self.assertEqual(r['route_gate'],'BLOCKED')
  self.assertFalse(r['verified']['race_mask_runtime_behavior'])
 def test_targeted_context(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'consumer.lua').write_text('function allowed(mask)\n if bit.band(mask, SKYBORNE_HORDE) ~= 0 then return true end\nend\n')
   r=scan(p)
   self.assertGreater(r['total_matching_lines'],0)
   self.assertTrue(any('consumer.lua'==h['file'] for h in r['selected_excerpts']))
if __name__=='__main__':unittest.main()
