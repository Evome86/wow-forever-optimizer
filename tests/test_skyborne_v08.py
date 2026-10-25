import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from filter_skyborne_v08 import classify, build_report, HORDE_SKYBORNE, ALLIANCE_SKYBORNE, DRUID

class TestFilter(unittest.TestCase):
    def q(self, **kwargs):
        return {'id': 1, 'name': 'Test', 'required_races_mask': HORDE_SKYBORNE,
                'required_classes_mask': DRUID, 'required_level': 1, 'quest_level': 5, **kwargs}

    def test_horde_skyborne_druid(self):
        self.assertEqual(classify(self.q())[0], 'candidate_unverified')

    def test_alliance_excluded(self):
        q = self.q(); q['required_races_mask'] = ALLIANCE_SKYBORNE | 77
        self.assertEqual(classify(q)[0], 'excluded_race')

    def test_horde_combined_mask(self):
        q = self.q(); q['required_races_mask'] = HORDE_SKYBORNE | 178
        self.assertEqual(classify(q)[0], 'candidate_unverified')

    def test_class_excluded(self):
        q = self.q(); q['required_classes_mask'] = 8
        self.assertEqual(classify(q)[0], 'excluded_class')

    def test_zero_and_missing_masks_preliminary(self):
        q = self.q(); q['required_races_mask'] = 0; q['required_classes_mask'] = None
        self.assertEqual(classify(q)[0], 'candidate_unverified')

    def test_minimum_level(self):
        q = self.q(); q['required_level'] = 31
        self.assertEqual(classify(q)[0], 'excluded_required_level')

    def test_negative_quest_level_review(self):
        q = self.q(); q['quest_level'] = -1
        self.assertEqual(classify(q)[0], 'candidate_special_quest_level')

    def test_unknown_mask_not_silently_included(self):
        q = self.q(); q['required_races_mask'] = None
        self.assertEqual(classify(q)[0], 'unknown_race_mask')

    def test_output(self):
        result = build_report({'quests': {'1': self.q()}, 'source_sha256': 'abc'})
        self.assertEqual(result['counts']['candidate_unverified'], 1)
        self.assertEqual(len(result['quest_candidates']), 1)

if __name__ == '__main__':
    unittest.main()
