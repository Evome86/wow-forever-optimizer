import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_runtime_v33 import scan_repo,as_ids,sample_chains,build
class TestV33(unittest.TestCase):
 def test_full_counts_not_truncated(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d,'sample.lua');p.write_text('SKYBORNE_HORDE\n'*99+'preQuestGroup\n')
   s=scan_repo(Path(d),max_examples=5)
   self.assertEqual(s['patterns']['skyborne_definition']['total_matches'],99)
   self.assertEqual(len(s['patterns']['skyborne_definition']['examples']),5)
 def test_nested_ids(self):
  self.assertEqual(as_ids({'1':123,'2':{'1':456}}),[123,456])
 def test_chain_evidence_not_eligibility(self):
  q={'90001':{'name':'Q','requiredLevel':2,'preQuestSingle':{'1':7},'preQuestGroup':{'1':8}},'7':{'name':'Before'}}
  chain=sample_chains(q)['examples'][0]
  self.assertEqual(chain['missing_references'],[8]);self.assertEqual(chain['semantics'],'UNVERIFIED')
  with tempfile.TemporaryDirectory() as d:
   report=build(q,Path(d,'db'),Path(d,'addon'))
   self.assertEqual(report['route_gate'],'BLOCKED')
   self.assertFalse(report['repositories']['questie_addon']['present'])
if __name__=='__main__':unittest.main()
