import unittest
from scripts.build_semantic_graph_v12 import build, correction_blocks, EXPECTED_SHA
class GraphTests(unittest.TestCase):
    def test_typed_edges_are_not_prerequisite_claims(self):
        d={'source_sha256':EXPECTED_SHA,'quests':{'10':{'prerequisites_raw':{'12':[1,2],'13':[3],'16':[4]}}}}
        r=build(d,'')
        self.assertEqual(len(r['raw_typed_edges']),4)
        self.assertEqual(r['raw_edge_counts']['exclusiveTo'],1)
        self.assertFalse(r['correction_audit']['patches_applied'])
    def test_sha_fail_closed(self):
        with self.assertRaises(ValueError):build({'source_sha256':'wrong','quests':{}},'')
    def test_correction_audit_only(self):
        text='    return {\n        [92595] = { -- Skyborne\n            [questKeys.requiredRaces] = raceIDs.SKYBORNE_HORDE,\n        },\n'
        found=correction_blocks(text)
        self.assertEqual(found[0]['quest_id'],92595)
        self.assertIn('requiredRaces',found[0]['fields_mentioned'])
if __name__=='__main__':unittest.main()
