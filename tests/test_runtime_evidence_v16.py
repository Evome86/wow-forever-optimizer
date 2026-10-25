import sys, unittest, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_runtime_evidence_v16 import blocks,refs_from_block,race_expressions,build

class TestV16(unittest.TestCase):
    def test_blocks(self):
        t='[92595] = {\n [questKeys.requiredRaces] = raceIDs.ALL_HORDE,\n},\n'
        b=blocks(t,{92595})
        self.assertEqual(len(b),1)
        self.assertEqual(race_expressions(b[0]['text'])[0]['expression'],'raceIDs.ALL_HORDE')
    def test_refs(self):
        self.assertEqual(refs_from_block('[questKeys.preQuestSingle] = { 93746, 12 },'),
                         [{'field':'preQuestSingle','id':93746},{'field':'preQuestSingle','id':12}])
    def test_no_expressions_evaluated(self):
        self.assertEqual(refs_from_block('[questKeys.preQuestSingle] = someLuaCall(42),'),[])
    def test_build_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for name in ('src/corrections/Forever/generated/foreverBaseQuest.lua','src/corrections/Forever/foreverQuestFixes.lua'):
                f=p/name;f.parent.mkdir(parents=True,exist_ok=True)
                f.write_text('[92595] = {\n [questKeys.requiredRaces] = raceIDs.ALL_HORDE,\n},\n')
            result=build(p,{'records':{}},{'quests':{}},max_closure=20)
            self.assertFalse(result['candidates']['92595']['route_eligible'])
            self.assertIn('BLOCKED',result['release_gate'])
if __name__=='__main__':unittest.main()
