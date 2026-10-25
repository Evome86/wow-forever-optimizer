import unittest,tempfile,json
from pathlib import Path
from scripts.audit_localization_v28 import inspect,build
class LocalizationTests(unittest.TestCase):
 def test_numeric_keys(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'deDE.lua';p.write_text('return { [92595] = "Die Windformer", [93320] = "Turmverteidigung" }')
   ids,byname,info=inspect(p);self.assertEqual(ids['92595'],'Die Windformer');self.assertEqual(info['status'],'PARSED')
 def test_string_keys(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'deDE.lua';p.write_text('return { ["The Windshapers"] = "Die Windformer" }')
   ids,byname,info=inspect(p);self.assertEqual(byname['The Windshapers'],'Die Windformer')
 def test_unsupported_is_not_zero_coverage(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'deDE.lua';p.write_text('local t = {}\nsetmetatable(t, {})');self.assertEqual(inspect(p)[2]['status'],'PARSER_UNSUPPORTED')
 def test_fallback_and_gate(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);loc=root/'l10n/Forever/lookupQuests';loc.mkdir(parents=True);(loc/'deDE.lua').write_text('return {[1]="Hallo"}')
   q=root/'q.json';q.write_text(json.dumps({'quests':{'1':{'name':'Hello'},'2':{'name':'World'}}}))
   report,rows=build(root,q);self.assertEqual(report['german_names_matched'],1);self.assertEqual(rows[1]['display_deDE'],'World');self.assertFalse(report['playable_quests_verified'])
if __name__=='__main__':unittest.main()
