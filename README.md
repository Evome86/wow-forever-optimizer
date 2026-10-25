# WoW Forever Optimizer v1.5 — Source-backed Correction Overlay

Extracts **only seven known Skyborne quest IDs** from three pinned QuestieDB Forever source files. Does not run Lua, does not pretend that trace rows are playable quest records. Extracts supported literal fields with file hashes and line numbers; quarantines unsupported expressions, multiline fields and conflicts. Existing raw quest records are not overwritten.

**Important:** This is a safe, narrowly scoped **evidence overlay**, not a complete correction engine. NPC association changes and the runtime's correction merge ordering remain unverified. No routes or XP claims.

## Install

Copy all files in this ZIP to the root of the existing GitHub repository, preserving folders. **Do not delete existing files**. Commit and push. GitHub Actions → **Forever Correction Overlay v1.5** → Run workflow. Download artifact `forever-overlay-v15`, then upload `forever-overlay-v15.json` here.

Depends on existing `scripts/import_quests.py` from v0.4.1. Pinned upstream commit `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`.
