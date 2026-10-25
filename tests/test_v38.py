import unittest
from pathlib import Path
class V38Integrity(unittest.TestCase):
 def test_never_unlocks_gate_from_assumed_mocks(self):
  src=Path('scripts/execute_original_v38.py').read_text()
  self.assertIn('BLOCKED_MOCK_PROVENANCE_UNVERIFIED',src)
  self.assertNotIn("gate='PASS_SOURCE_PARITY_ONLY'",src)
 def test_source_context_captured(self):
  self.assertIn('preceding_lines',Path('scripts/source_context_v38.py').read_text())
 def test_workflow_uploads_both_reports(self):
  w=Path('.github/workflows/forever-v38.yml').read_text()
  self.assertIn('forever-v38-source-context.json',w)
  self.assertIn('forever-v38-lua-dependencies.json',w)
