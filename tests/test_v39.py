import unittest
from pathlib import Path
from scripts.execute_original_v39 import lua_literal, FUNCTIONS

class V39HarnessTests(unittest.TestCase):
    def test_exclusive_mapping_literal(self):
        self.assertEqual(lua_literal({101:[102]}), '{[101]={102}}')
    def test_completion_structure_and_source(self):
        s=Path('scripts/execute_original_v39.py').read_text()
        self.assertIn('Questie.db.char.complete',s)
        self.assertIn('QuestieDB.QueryQuestSingle',s)
        self.assertIn('local playerRaceFlag=8589934592',s)
        self.assertIn('prefix..source',s)
    def test_original_definitions_remain_targets(self):
        self.assertEqual(set(FUNCTIONS), {'race','single','group'})
    def test_workflow_pinned(self):
        s=Path('.github/workflows/forever-v39.yml').read_text()
        self.assertIn('30ac9acb7107fdfdd0cfff4d1e03d9bf60b0e374',s)
        self.assertIn('5c094f6e9a264f0dc54e2fde9731a37a97ed197c',s)
