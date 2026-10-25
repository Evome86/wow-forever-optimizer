# WoW Forever Optimizer v3.9 — Source-Verified Isolated Lua Harness

## Changes
- Execute original Questie Lua function bodies from pinned Questie commit `30ac9acb7107fdfdd0cfff4d1e03d9bf60b0e374`.
- Provide `playerRaceFlag=8589934592` and `playerRaceFlagX2=17179869184` in the **same Lua chunk** as extracted original functions, preserving Lua lexical scope.
- Provide `Questie.db.char.complete[questId]` for completed-quest state.
- Mock `QuestieDB.QueryQuestSingle(questId, 'exclusiveTo')` as a controlled data accessor only; original AND/OR/exclusive logic is never replaced.
- Run 19 comparison fixtures, with explicit status, result, parity and error per fixture.
- Record errors consistently in `runtime_error_count` and `errors`.
- Include addon and QuestieDB SHA files in the workflow artifact.

## How to run
Upload the overlay contents to the repository, commit, then run GitHub Actions workflow **Forever v3.9 Source-Verified Lua Harness**. Download artifact `forever-v39-original-lua-evidence` and upload `forever-v39-original-lua.json` here.

## Gate policy
`technical_gate=PASS_ISOLATED_FUNCTION_PARITY_ONLY` means only the original isolated function bodies agree with the reference fixtures. It does **not** mean full Questie addon integration, actual Forever addon build identity, complete quest eligibility or in-game availability. `ingame_gate` and `route_gate` always remain `BLOCKED` in v3.9.

## Local verification
`python3 -m unittest discover -s tests -p 'test_*.py' -q` (31 tests passed during packaging). Actual Lua 5.1 original-function execution requires GitHub checkout and Lua installation in the workflow.
