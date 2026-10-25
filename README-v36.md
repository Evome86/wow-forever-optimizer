# v3.6 – Strict Original Lua Runtime Gate (preflight)

**Status: This is a preflight / evidence-integrity release, NOT an execution harness.**

The workflow checks out the pinned QuestieDB and records the current Questie addon commit. It finds the definitions of the three target Lua functions and explicitly marks all original-Lua runtime tests **NOT_RUN**. It never upgrades the technical gate on the basis of static source inspection or Python-only tests.

This prevents false-positive claims while we prepare a genuine isolated Lua runtime harness with WoW API mocks and verified dependencies. To build that harness, inspect the exact functions and transitive dependencies in the generated `forever-v36-lua-runtime.json` and the pinned source. Until then, both gates are BLOCKED.

Run: Actions → **Forever v3.6 Original Lua Runtime Gate** → Run workflow. Download `forever-v36-lua-runtime-gate`, share `forever-v36-lua-runtime.json` and `addon-commit-v36.txt`.
