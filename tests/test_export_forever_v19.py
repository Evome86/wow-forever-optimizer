import importlib.util
import pathlib
import unittest
P=pathlib.Path(__file__).resolve().parents[1]/'scripts/export_forever_v19.py'
spec=importlib.util.spec_from_file_location('v19',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_detects_quest_key(self):
        self.assertEqual(m.blocks('abc\n[94414] = {\n  races = 1,\n}\n',94414)[0]['line'],2)
    def test_does_not_match_substring(self):
        self.assertEqual(m.blocks('[194414] = {}\n[944140] = {}',94414),[])
    def test_gate_explicit(self):
        self.assertEqual(len(m.IDS),24)
        self.assertTrue(all(p.endswith('.lua') for p in m.PATHS))
if __name__=='__main__':unittest.main()
