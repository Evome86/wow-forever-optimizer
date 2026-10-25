import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_v31 import analyze,band
class TestV31(unittest.TestCase):
 def test_bands(self):
  self.assertEqual(band(10),'01-10');self.assertEqual(band(11),'11-20');self.assertEqual(band(60),'51-60');self.assertEqual(band(61),'61_PLUS');self.assertEqual(band(None),'UNKNOWN')
 def test_counts_and_gate(self):
  quests={'1':{'requiredLevel':10,'questLevel':12,'preQuestSingle':{'1':92595}},'92595':{'requiredLevel':60,'questLevel':61,'preQuestGroup':{'1':1}}}
  r=analyze(quests)
  self.assertEqual(r['level_bands_required_level']['51-60']['new_90k'],1)
  self.assertEqual(r['level_bands_quest_level']['61_PLUS']['new_90k'],1)
  self.assertFalse(r['playable_quests_verified'])
  self.assertEqual(r['semantic_flags'].get('missing_referenced_quest',0),0)
 def test_missing_reference(self):
  r=analyze({'1':{'preQuestSingle':{'1':999}}})
  self.assertEqual(r['semantic_flags']['missing_referenced_quest'],1)
if __name__=='__main__':unittest.main()
