import json,tempfile,unittest
from pathlib import Path
from scripts.audit_localization_v29 import parse,build

class Tests(unittest.TestCase):
 def fixture(self,root):
  loc=root/'l10n/Forever/lookupQuests';loc.mkdir(parents=True)
  (loc/'deDE.lua').write_text('''if GetLocale() ~= "deDE" then\nreturn\nend\nlocal l10n = QuestieLoader:ImportModule("l10n")\nl10n.questLookup["deDE"] = loadstring([[return {\n[2] = {"Klaue von Scharfkralle", {"Bringt die Klaue."}},\n[5] = {"Jitters' knurrender Magen", {"Sprecht mit dem Koch."}},\n[93320] = {"Verteidigung des Turms", {"Eine Aufgabe"}},\n}]])\n''',encoding='utf-8')
  return loc/'deDE.lua'
 def test_real_wrapper_and_titles(self):
  with tempfile.TemporaryDirectory() as d:
   path=self.fixture(Path(d));ids,info=parse(path)
   self.assertEqual(ids['2'],'Klaue von Scharfkralle');self.assertEqual(ids['5'],"Jitters' knurrender Magen")
   self.assertEqual(ids['93320'],'Verteidigung des Turms');self.assertEqual(len(ids),3)
   self.assertEqual(info['status'],'PARSED')
 def test_fallback_and_gate(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.fixture(root)
   quests=root/'quests.json';quests.write_text(json.dumps({'quests':{'2':{'name':"Sharptalon's Claw"},'7':{'name':'Kobold Camp Cleanup'}}}))
   report,rows=build(root,quests)
   self.assertEqual(report['german_names_matched'],1)
   self.assertEqual(rows[1]['display_deDE'],'Kobold Camp Cleanup')
   self.assertFalse(report['playable_quests_verified'])
 def test_unsupported_not_zero_coverage(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'deDE.lua';p.write_text('return {[2]={"Foo",{}}}')
   self.assertEqual(parse(p)[1]['status'],'PARSER_UNSUPPORTED')
if __name__=='__main__':unittest.main()
