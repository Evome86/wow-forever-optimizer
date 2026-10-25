import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_runtime_v32 import scan,build
class TestV32(unittest.TestCase):
 def test_source_scan(self):
  with tempfile.TemporaryDirectory() as t:
   Path(t,'x.lua').write_text('local Skyborne = 1\n-- preQuestSingle\n')
   count,result=scan(Path(t));self.assertEqual(count,1);self.assertEqual(result['skyborne']['sample_count'],1)
 def test_gate_not_unlocked(self):
  r=build({'90001':{'name':'X','requiredRaces':0,'requiredClasses':0}},{});self.assertEqual(r['route_gate'],'BLOCKED');self.assertEqual(r['forever_90k_mask_counts']['total'],1)
if __name__=='__main__':unittest.main()
