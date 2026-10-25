import tempfile
import unittest
from pathlib import Path
from scripts.inspect_skyborne import discover

class TestSkyborneDiscovery(unittest.TestCase):
    def test_matches_are_evidence_not_eligibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'races.lua').write_text('Windshaper Skyborne\n', encoding='utf-8')
            data = {'quests': {'12': {'name': 'Skyborne Trial', 'required_races_mask': 4294967373}}}
            report = discover(data, Path(tmp))
            self.assertEqual(report['quest_name_matches'][0]['quest_id'], 12)
            self.assertEqual(report['race_masks_over_u32']['4294967373'], 1)
            self.assertTrue(report['release_gate'].startswith('BLOCKED'))
            self.assertEqual(len(report['source_text_matches']), 1)

    def test_absence_does_not_prove_unplayable(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = discover({'quests': {'1': {'name': 'A Simple Quest'}}}, Path(tmp))
            self.assertEqual(report['quest_name_matches'], [])
            self.assertEqual(report['source_text_matches'], [])
            self.assertTrue(report['unknowns'])

if __name__ == '__main__': unittest.main()
