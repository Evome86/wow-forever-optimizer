import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_eligibility_v24 import ids,SKYBORNE,DRUID
class Tests(unittest.TestCase):
 def test_sparse_lua_indices(self): self.assertEqual(ids({'1':92860,'3':92871}),[92860,92871])
 def test_bit_constants(self): self.assertEqual(SKYBORNE,8589934592);self.assertEqual(DRUID,1024)
 def test_empty_references(self): self.assertEqual(ids({}),[])
if __name__=='__main__':unittest.main()
