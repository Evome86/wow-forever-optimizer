# v3.8 — Lua Dependency Resolution (fail closed)

This release attempts the **unmodified original Questie Lua functions** using isolated, explicit dependency stubs and captures original source context to evaluate stub provenance.

**No technical PASS is possible in v3.8**: mock provenance is not yet verified against actual addon initialization. A 19/19 result only indicates agreement *under assumed test environment*. It does not prove actual game behavior or addon initialization.

Run **Forever v3.8 Lua Dependency Resolution** in GitHub Actions. Download `forever-v38-dependency-evidence` and provide both JSON files.

Important: `playerRaceFlagX2=17179869184` is an **assumption**, not a verified source-derived value. Questie completion functions are stubbed as completed-set lookups, and real semantics (including exclusiveTo) may differ. The original function bodies are not rewritten. Every execution error is counted in `runtime_error_count`; `technical_gate` and `route_gate` remain BLOCKED.
