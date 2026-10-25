import tempfile,unittest
from pathlib import Path
from scripts.audit_semantics_locale_v26 import audit
class AuditTests(unittest.TestCase):
 def test_context_and_locale(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'locales').mkdir();(p/'locales/deDE.lua').write_text('name = "Deutsch"\n');(p/'quest.lua').write_text('local x=1\nrequiredRaces=0\npreQuestSingle={1}\n')
   x=audit(p)
   self.assertEqual(x['files_scanned'],2)
   self.assertEqual(x['topics']['race_zero_mask']['total_matches'],1)
   self.assertEqual(len(x['locale_inventory']),1)
   self.assertFalse(x['localized_names_verified'])
if __name__=='__main__':unittest.main()
