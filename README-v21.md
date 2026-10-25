# WOW Forever Optimizer v2.1 — Native Quest Accessor Evidence

This overlay runs the **actual QuestieDB Forever Source addon** through upstream `emulator/client.lua` and `emulator/metadata.lua`, using the same load sequence proven by `emulator/native-source.test.lua` in v2.0. It introspects the public `db.Quest` accessors and invokes read-only candidates on the 24 selected quest IDs, including **94414**.

## Run
1. Extract the ZIP into the root of `Evome86/wow-forever-optimizer` (merge files).
2. Commit and push.
3. GitHub Actions → **Forever Native Quest Accessor v2.1** → Run workflow.
4. Download artifact `forever-native-quest-v21` and upload both `forever-native-quest-v21.json` and `forever-native-quest-v21.log` here.

## Verification limits
- `native_provider_values_captured=true` means QuestieDB returned values, **not** that race-mask meaning, correction provenance, or route eligibility have been verified.
- `effective_quest_values_verified=false` remains mandatory until an accessor's schema and correction order are validated.
- No XP/hour or route recommendations are generated.
- Method errors are logged for analysis, not silently turned into quest values.
- No changes are made to the upstream checkout except a temporary Lua probe file that is removed after execution.
