# v3.7 — Original Lua function execution (fail closed)

Workflow **Forever v3.7 Execute Original Lua** checks out the exact Questie addon SHA reported in v3.6 (`30ac9acb7107fdfdd0cfff4d1e03d9bf60b0e374`) and the pinned QuestieDB SHA. It installs Lua 5.1, extracts the **original** three function definitions from their source files, and **attempts to execute** the same 19 inputs used by the Python reference model. No implementation of those functions is substituted.

**Important:** This is an isolated execution harness, not a fully initialized WoW addon. Missing WoW APIs, dependencies or incompatible data representations are reported as `ERROR`/`NOT_RUN`/`NON_BOOLEAN`, never counted as parity. Each test reports actual Lua output or the error and the reference expectation. A green GitHub workflow only means an evidence artifact was generated, **not** that the technical gate passed. `PASS_SOURCE_PARITY_ONLY` requires 19 actual boolean executions, no mismatch, and no loader error. Ingame gate and route gate remain BLOCKED regardless.

Download artifact `forever-v37-original-lua-evidence` and return `forever-v37-original-lua.json` for dependency-specific follow-up. The goal of this first execution pass is to expose *exactly which* WoW/Questie dependencies need faithful mocks, without pretending missing APIs are verified.
