import importlib.util,pathlib,tempfile,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'scripts/probe_native_provider_v20.py'
spec=importlib.util.spec_from_file_location('probe',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class ProbeTests(unittest.TestCase):
 def test_no_upstream_folder(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(mod.scan(pathlib.Path(d)),(0,[],0))
 def test_provider_discovery(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'test.lua';path.write_text('function QuestieDB.GetQuestData(id)\n return id\nend\n')
   n,m,total=mod.scan(pathlib.Path(d));self.assertEqual((n,total),(1,1));self.assertEqual(m[0]['line'],1)
 def test_exclude_git(self):
  with tempfile.TemporaryDirectory() as d:
   hidden=pathlib.Path(d)/'.git';hidden.mkdir();(hidden/'test.lua').write_text('GetQuestData')
   self.assertEqual(mod.scan(pathlib.Path(d)),(0,[],0))
 def test_truncation(self):
  with tempfile.TemporaryDirectory() as d:
   (pathlib.Path(d)/'test.lua').write_text('GetQuestData\n'*10)
   n,m,total=mod.scan(pathlib.Path(d),limit=2);self.assertEqual((len(m),total),(2,10))
if __name__=='__main__':unittest.main()
