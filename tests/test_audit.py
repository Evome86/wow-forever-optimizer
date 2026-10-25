import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_quests import audit

class AuditTests(unittest.TestCase):
    def sample(self):
        return {'quests':{'1':{'id':1,'name':'Sample','required_level':1,'quest_level':2,'required_races_mask':0,'required_classes_mask':None,'started_by_raw':[],'finished_by_raw':[],'objectives_raw':None,'prerequisites_raw':{}}}}
    def test_valid(self):
        self.assertEqual(audit(self.sample())['status'],'structural_pass_unverified')
    def test_mismatched_id(self):
        d=self.sample();d['quests']['1']['id']=2
        self.assertEqual(audit(d)['status'],'structural_issues_unverified')
    def test_missing_field(self):
        d=self.sample();del d['quests']['1']['required_level']
        self.assertEqual(audit(d)['status'],'structural_issues_unverified')
    def test_invalid_mask(self):
        d=self.sample();d['quests']['1']['required_races_mask']=-1
        self.assertEqual(audit(d)['status'],'structural_issues_unverified')

if __name__=='__main__': unittest.main()
