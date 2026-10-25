import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).resolve().parents[1]/'scripts/run_native_quest_probe_v21.py'
spec=importlib.util.spec_from_file_location('probe',P)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TestParser(unittest.TestCase):
 def test_parse(self):
  m,methods,values,errors=mod.parse('META\tflavor\tForever\nMETHOD\trace\tfunction\nVALUE\t94414\trace\tnumber\t0\nMETA\tcomplete\ttrue\n')
  self.assertEqual(m['flavor'],'Forever');self.assertEqual(values[0]['quest_id'],94414);self.assertFalse(errors)
 def test_ids(self):self.assertEqual(len(mod.IDS),24)
if __name__=='__main__':unittest.main()
