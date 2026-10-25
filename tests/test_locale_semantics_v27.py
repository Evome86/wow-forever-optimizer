import importlib.util, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('v27','scripts/build_locale_semantics_v27.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestLocale(unittest.TestCase):
 def test_lookup(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'deDE.lua';p.write_text('return {\n [123] = "Grüße",\n [124] = "Hallo \\"Held\\"",\n}',encoding='utf-8')
   vals,info=m.parse_lookup(p);self.assertEqual(vals['123'],'Grüße');self.assertEqual(vals['124'],'Hallo "Held"');self.assertEqual(info['parsed_entries'],2)
 def test_missing(self):
  vals,info=m.parse_lookup(Path('/missing/not-a-file.lua'));self.assertFalse(info['present']);self.assertEqual(vals,{})
if __name__=='__main__':unittest.main()
