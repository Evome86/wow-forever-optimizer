import unittest
from scripts.validate_v40_report import validate

class V40Tests(unittest.TestCase):
    def good(self):
        tests=[]
        for i in range(19):
            b=i%2==0
            tests.append({'name':f'case_{i}','lua_status':'EXECUTED','lua_actual':b,'reference_expected':b,'parity':True,'error':None})
        return {'tests':tests,'runtime_error_count':0,'errors':[],'mismatches':[],'unresolved':[],'confirmed_parity_count':19,'technical_gate':'PASS_ISOLATED_FUNCTION_PARITY_ONLY','route_gate':'BLOCKED','ingame_gate':'BLOCKED_NOT_VERIFIED'}
    def test_good(self): self.assertEqual(validate(self.good()),[])
    def test_null_not_false(self):
        d=self.good();d['tests'][1]['lua_actual']=None;d['tests'][1]['parity']=None
        self.assertTrue(validate(d))
    def test_false_parity(self):
        d=self.good();self.assertIs(d['tests'][1]['lua_actual'],False);self.assertEqual(validate(d),[])
    def test_mismatch(self):
        d=self.good();d['tests'][1]['lua_actual']=True;d['tests'][1]['parity']=False
        self.assertTrue(validate(d))
    def test_duplicate(self):
        d=self.good();d['tests'][1]['name']=d['tests'][0]['name'];self.assertTrue(validate(d))
    def test_gate(self):
        d=self.good();d['route_gate']='PASS';self.assertTrue(validate(d))
    def test_serialization_fix_present(self):
        from pathlib import Path
        s=Path('scripts/execute_original_v40.py').read_text()
        self.assertIn('tostring(value):gsub',s)
        self.assertNotIn("tostring(value or '')",s)
        self.assertIn("type(t['lua_actual']) is bool",s)

    def test_v39_real_report_rejected(self):
        import json
        from pathlib import Path
        d=json.loads(Path('tests/fixture-v39-null-regression.json').read_text())
        self.assertEqual(sum(t['lua_actual'] is None for t in d['tests']),7)
        self.assertTrue(validate(d))
