# WoW Forever Optimizer v2.3 — Full native quest export

Overlay the archive at the root of `Evome86/wow-forever-optimizer` (preserve existing files), commit/push, then manually run GitHub Actions workflow **Forever Full Native Quest Export v2.3**.

Download artifact `forever-native-quest-v23`. Upload `forever-native-export-v23-report.json`, `forever-native-quests-v23.json` and `.log` here; TSV optional. Large JSON may be zipped when uploading.

The script invokes the **actual QuestieDB Forever Source loader** and iterates `Quest.GetAllIds()`; each quest is read via the same ID-keyed accessors proven in v2.2. All nested Lua tables are serialized without artificial depth/element limits; numeric Lua table indices become JSON object keys to avoid holes and ambiguity. SHA256 of the raw native export is recorded. The exporter fails closed on missing fields, mismatched counts, duplicate IDs, provider errors, unexpected race-mask regressions, and wrong upstream commit.

**Not yet a verified playable route:** `effective_quest_values_verified=false` and route eligibility is blocked until faction/race/class/quest-chain semantics, conditional quest availability, and location/XP models are validated. `GetAllIds()` must enumerate the expected data; if its output shape differs, the workflow will fail and emit a report rather than silently output partial data.
