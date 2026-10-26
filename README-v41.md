# Forever Optimizer v4.1 – IsDoable static audit + GUI preview

## Scope and truthfulness

- v4.0 evidence: 19/19 isolated original Lua functions passed, **not** full availability.
- v4.1 extracts the complete original `QuestieDB.IsDoable` source and catalogs potential conditions and method calls. This is **static evidence**, not runtime verification.
- GUI (`web/optimizer.html`) is a local file-based preview with character settings, evidence import, and quest browsing. Quest eligibility and routes remain **BLOCKED**.
- Pinned addon `30ac9acb7107fdfdd0cfff4d1e03d9bf60b0e374`, DB `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`; not proven identical to live Forever client.

## Usage

1. Merge ZIP contents into the GitHub repository and commit.
2. Run **Forever v4.1 IsDoable Audit and GUI** under GitHub Actions.
3. Download artifact `forever-v41-isdoable-source-evidence` and upload `forever-v41-isdoable-audit.json` here.
4. Open `web/optimizer.html` locally in a modern browser. Import the v4.0 report and then v4.1 audit using the JSON button. No backend or network required.

## Next technical phase

Map the entire `IsDoable` dependency graph; execute the unmodified original function with controlled fixture scenarios, then cross-check real client behavior. No unknown conditions may be silently accepted.
