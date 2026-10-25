# v1.7.1 Hotfix — QuestieDB source path filtering

Root cause: v1.7 checked `p.parts` (absolute path) for `vendor` and accidentally skipped every Lua file because QuestieDB is checked out to `vendor/QuestieDB`. Fix uses `p.relative_to(root).parts`. Missing sources now cause a failed workflow rather than a misleading empty success report. Five regression tests included.

Extract into the root of your existing repository; preserve other scripts and workflows. Run the existing **Forever Runtime Semantics v1.7** workflow again. Download `forever-runtime-semantics-v17.json` from the new run and upload it here. This is still source evidence, not Lua execution or verified route eligibility.
