import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('semantics',Path(__file__).resolve().parents[1]/'scripts'/'inspect_semantics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
META="""[12]='fieldA',[13]='fieldB',[14]='fieldC',[15]='fieldD',[16]='fieldE'"""
class TestSemantics(unittest.TestCase):
 def test_large_masks_preserved(self):
  d={'source_sha256':'x','quests':{'1':{'required_races_mask':8589934770,'required_classes_mask':1024,'prerequisites_raw':{'13':[2]}},'2':{'prerequisites_raw':{}}}}
  r=m.inspect(d,META)
  self.assertEqual(r['race_masks']['above_u32']['8589934770'],1)
  self.assertEqual(r['quest_reference_fields']['field_13']['counts']['positive_id_entries'],1)
  self.assertEqual(r['quest_reference_fields']['field_13']['missing_target_ids_sample'],{})
  self.assertFalse(r['verified_eligibility'])
 def test_unknown_reference_reported(self):
  d={'quests':{'1':{'prerequisites_raw':{'13':[999]}}}}
  r=m.inspect(d,META)
  self.assertEqual(r['quest_reference_fields']['field_13']['missing_target_ids_sample']['999'],1)
 def test_changed_metadata_is_detected(self):
  r=m.inspect({'quests':{}},"['field_13'] = 99")
  self.assertFalse(r['field_mapping']['field_13']['matches'])
if __name__=='__main__':unittest.main()
