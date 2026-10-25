# WoW Forever Optimizer v3.3 — Questie Runtime + Test Chains

Root overlay for `Evome86/wow-forever-optimizer`. Upload ZIP contents preserving folder paths. Existing v3.2 files remain included; this is cumulative.

## Run
GitHub → Actions → **Forever v3.3 Addon Semantics and Test Chains** → Run workflow. Download artifact **forever-v33-semantics-and-chains**, and share `forever-v33-source-and-chains.json`.

## What it does
- Exports the same 5,232-quest QuestieDB Forever dataset from pinned commit `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`.
- Attempts to check out the *separate* `Questie/Questie` addon runtime source. Its actual checkout SHA is recorded; this is not a pinned Forever-specific runtime version.
- Scans both repositories, records **total** matches and file counts for Skyborne definitions, race-mask use and prerequisite logic, and preserves bounded context excerpts. No misleading truncated match counts.
- Selects up to 24 low-level 90k+ quest-chain candidates, preserving the raw prerequisite structures, referenced IDs and unresolved references. These are **test candidates**, not confirmed Horde/Druid-eligible quests.

## Critical limitations
The code scanner is static keyword evidence, not proof of the meaning of masks or AND/OR logic. Questie default-branch code might not match the Forever build. No quest is marked playable or eligible; route gate remains `BLOCKED`. The addon checkout is non-fatal so an inaccessible repository still yields a report with `present=false`. If it is absent, supply the correct Forever addon source and commit before semantic validation.
