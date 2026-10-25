# Forever v1.3 — Correction-sensitive audit and missing fields

Upload the files in this ZIP to the repository root, preserving `scripts/`, `tests/` and `.github/workflows/`.

Run **Actions → Forever Corrections Audit v1.3 → Run workflow**. Download the `forever-corrections-v13` artifact and upload `forever-corrections-v13.json` here.

## Scope and explicit limitation

- Extracts original raw fields **22, 25, 27, 28** from the pinned quest database, using the existing non-executing Lua literal parser.
- Records raw references and which targets exist in the import.
- Re-runs raw-only Horde Skyborne Druid level <=30 screening and flags quest IDs heuristically mentioned in `foreverQuestFixes.lua`.
- Does **not** execute or apply Lua corrections; does **not** claim corrected eligibility, XP or a playable route. Corrections can be dynamic, nested or order-sensitive; applying them via regex would fabricate accuracy.
- Keeps release gate BLOCKED until correction runtime behavior is verified. The audit output contains raw data and should not be presented as a corrected runtime database.
