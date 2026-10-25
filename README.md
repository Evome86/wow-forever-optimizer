# WoW Forever Optimizer v1.6 — Runtime Evidence & Race Audit

A conservative **source evidence** audit. Searches Lua source for race constants and loader references, and expands up to three rounds of literal quest dependency IDs from the seven known Skyborne quests. Every finding includes source paths and line numbers. **Does not execute Lua, resolve bitmasks, infer loader order, certify playable quests, or calculate XP.** The 94414 `raceIDs.NONE` override remains unresolved.

## Install
Unzip at the root of your existing repository, preserving paths; keep all earlier version files (particularly `scripts/import_quests.py` and `scripts/build_correction_overlay_v15.py`). Commit. In GitHub Actions run **Forever Runtime Evidence v1.6**. Download artifact `forever-runtime-evidence-v16` and upload `forever-runtime-evidence-v16.json` to this conversation.

Pinned QuestieDB: `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`. Python standard library only.
