# WOW Forever Optimizer v2.5 — Combined Semantics Evidence + Quest Graph

One workflow combines the native v2.3 export, v2.4 eligibility audit, complete reference graph, tiered Horde Skyborne Druid candidates (levels 1–30), and pinned QuestieDB source-search evidence.

## Install
Overlay this ZIP at the **root** of `Evome86/wow-forever-optimizer` (do not delete existing files), commit and push. In GitHub Actions run **Forever Combined Semantics and Quest Graph v2.5**. Download `forever-combined-v25` and upload `forever-graph-v25-summary.json`, `forever-semantics-evidence-v25.json`, and `forever-graph-v25.json` (zip if large).

## Interpretation
- `EXPLICIT_RACE_MATCH_UNVERIFIED`: mask includes Skyborne; does not prove in-game availability.
- `ZERO_RACE_MASK_UNVERIFIED`: race mask 0; semantics not assumed.
- `EXPLICITLY_EXCLUDED`: fails an explicit race/class/level field for the target.
- Edges are **raw references**, never assumed AND/OR dependencies or playable route steps.
- Source evidence lists matching code locations; it **does not** automatically certify semantics.
- `route_eligibility_gate` intentionally remains blocked pending code review and/or in-game verification.

## Local tests
`python3 -m unittest discover -s tests -v`

## Provenance
QuestieDB pinned SHA `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`. No external source required to run the local graph script if a valid v2.3 JSON export is provided.
