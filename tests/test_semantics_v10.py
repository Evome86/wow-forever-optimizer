import unittest
from pathlib import Path
from scripts.audit_semantics_v10 import analyze

class SemanticsTests(unittest.TestCase):
    def test_cross_boundary(self):
        quests={"source_sha256":"abc","quests":{"1":{"name":"a","prerequisites_raw":{"13":[2]}},"2":{"name":"b","prerequisites_raw":{"12":[1]}}}}
        filt={"source_sha256":"abc","quest_candidates":[{"id":1}]}
        graph={"source_sha256":"abc"}
        result=analyze(quests,filt,graph,Path("/tmp/nonexistent-vendor"))
        self.assertEqual(result["cross_boundary_reference_count"],2)
        self.assertIn("BLOCKED",result["release_gate"])
    def test_hash_mismatch(self):
        with self.assertRaises(ValueError):
            analyze({"source_sha256":"a","quests":{}},{"source_sha256":"b","quest_candidates":[]},{"source_sha256":"a"},Path("/tmp"))
if __name__=="__main__":unittest.main()
