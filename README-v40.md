# WoW Forever Optimizer v4.0 — Boolean-Safe Original Lua Parity

## Fix
v3.9 serialized Lua `false` as an empty string through `tostring(value or '')`.
Lua `false or ''` evaluates to `''`, so the Python parser emitted JSON `null` for seven negative fixtures. v4.0 serializes with `tostring(value)` and **requires all 19** boolean results and parity checks to be exactly true before the isolated technical gate passes.

## Evidence
- Pinned addon `30ac9acb7107fdfdd0cfff4d1e03d9bf60b0e374` and QuestieDB `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`.
- Original Questie Lua function bodies extracted at runtime; no replacements for predicate logic.
- Strict independent JSON validator rejects `null`, incomplete output, mismatches, missing fixtures, duplicate names, or incorrectly opened route/ingame gates.
- Corrected source-context report version.

## Usage
Upload overlay to the root of the GitHub repository, commit, run **Forever v4.0 Boolean-Safe Lua Parity** in Actions, download `forever-v40-original-lua-evidence`, and share `forever-v40-original-lua.json`.

## Limits
A pass proves only parity of three **isolated** Questie functions for 19 synthetic fixtures at the pinned source commit. It does NOT prove full `IsDoable()` eligibility, in-game availability, exact Forever addon version, or a usable leveling route. The route remains **BLOCKED**.
