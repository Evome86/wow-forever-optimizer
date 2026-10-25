import unittest
from scripts.run_native_quest_export_v23 import decode_lines, validate

class TestExport(unittest.TestCase):
    def test_nested_data_preserved(self):
        m,q,e=decode_lines('META\tflavor\tForever\nQUEST\t94414\nVALUE\t94414\tpreQuestSingle\t{"1":92871,"2":{"3":17}}\nMETA\tcomplete\ttrue\n')
        self.assertEqual(q[94414]['preQuestSingle']['2']['3'],17)
        self.assertEqual(m['flavor'],'Forever')
        self.assertEqual(e,[])
    def test_duplicate_field_fails(self):
        with self.assertRaises(AssertionError):
            decode_lines('QUEST\t1\nVALUE\t1\tname\t"A"\nVALUE\t1\tname\t"B"\n')
    def test_invalid_json_fails(self):
        with self.assertRaises(ValueError):
            decode_lines('QUEST\t1\nVALUE\t1\tname\t{broken}\n')
    def test_incomplete_fails(self):
        with self.assertRaises(AssertionError):
            validate({'flavor':'Forever','complete':'false','quest_count':'0','error_count':'0','value_count':'0'}, {}, [])
    def test_native_errors_fails(self):
        with self.assertRaises(AssertionError):
            validate({'flavor':'Forever','complete':'true','quest_count':'1001','error_count':'1','value_count':'0'}, {}, [{'quest_id':1}])

if __name__=='__main__': unittest.main()
