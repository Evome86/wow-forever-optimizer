import importlib.util, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_graph_v25 import graph, semantic_evidence
from build_eligibility_v24 import PIN

def sample():
    qs={}
    for i in range(1,5002):qs[str(i)]={'Exists':True,'name':f'Quest {i}','requiredRaces':8589934592,'requiredClasses':0,'requiredLevel':2,'requiredMaxLevel':0}
    qs['1']['preQuestSingle']={'1':2,'2':3};qs['1']['nextQuestInChain']=4
    qs['2']['requiredRaces']=0
    qs['3']['requiredRaces']=1
    return {'version':'2.3','upstream_commit':PIN,'quests':qs}
class GraphTests(unittest.TestCase):
    def test_counts_and_tiers(self):
        r=graph(sample());self.assertEqual(r['quest_count'],5001);self.assertEqual(r['tier_counts']['ZERO_RACE_MASK_UNVERIFIED'],1);self.assertEqual(r['tier_counts']['EXPLICITLY_EXCLUDED'],1)
    def test_edges_not_assumed_and(self):
        r=graph(sample());self.assertEqual(len(r['edges']),3);self.assertTrue(all(e['interpretation']=='RAW_REFERENCE_ONLY' for e in r['edges']))
    def test_gate_stays_blocked(self):self.assertFalse(graph(sample())['playable_quests_verified'])
    def test_reject_wrong_commit(self):
        d=sample();d['upstream_commit']='wrong'
        with self.assertRaises(ValueError):graph(d)
if __name__=='__main__':unittest.main()
