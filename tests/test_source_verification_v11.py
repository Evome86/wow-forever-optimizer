import tempfile, unittest
from pathlib import Path
from scripts.verify_semantics_v11 import audit, extract
class SourceVerificationTests(unittest.TestCase):
 def test_extract_line_numbers(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'a.lua';p.write_text('alpha\nrequiredRaces = 178\nomega\n')
   r=extract(p,max_matches=1,radius=0)
   self.assertEqual(r['excerpts'][0]['lines'][0]['line'],2)
 def test_missing_files_gate(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=audit(Path(tmp),{'release_gate':'BLOCKED','cross_boundary_reference_count':179,'source_sha256':'abc'})
   self.assertEqual(r['input_boundary_count'],179)
   self.assertTrue(r['missing_files'])
   self.assertIn('BLOCKED',r['release_gate'])
 def test_invalid_previous(self):
  with self.assertRaises(ValueError):audit(Path('/tmp'),{})
if __name__=='__main__':unittest.main()
