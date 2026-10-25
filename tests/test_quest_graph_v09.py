import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_quest_graph_v09 import analyze
class Tests(unittest.TestCase):
    def setUp(self):
        self.data={"source_sha256":"abc","quests":{
            "1":{"prerequisites_raw":{"13":[2,3]}},
            "2":{"prerequisites_raw":{"15":[1]}},
            "3":{"prerequisites_raw":{"13":[999]}},
            "4":{"prerequisites_raw":{}}}}
        self.filt={"source_sha256":"abc","quest_candidates":[{"id":1},{"id":2}]}
    def test_edges_and_components(self):
        r=analyze(self.data,self.filt)
        self.assertEqual(r["candidate_reference_edge_count"],2)
        self.assertEqual(r["candidate_to_other_or_other_to_candidate_edge_count"],1)
        self.assertEqual(r["missing_reference_edge_count"],1)
        self.assertEqual(r["candidate_component_sizes_top_30"],[2])
        self.assertEqual(r["reciprocal_reference_pairs_count"],1)
    def test_hash_mismatch(self):
        self.filt["source_sha256"]="other"
        with self.assertRaises(ValueError):analyze(self.data,self.filt)
    def test_invalid_reference(self):
        self.data["quests"]["1"]["prerequisites_raw"]["12"]=[-1,True]
        r=analyze(self.data,self.filt)
        self.assertEqual(r["field_reference_analysis"]["field_12"]["counts"]["invalid_reference_values"],2)
if __name__=="__main__":unittest.main()
