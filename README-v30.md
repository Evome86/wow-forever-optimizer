# WoW Forever Optimizer v3.0 — bilingual data + semantics triage

Overlay ZIP **at repository root**. Do not upload `__pycache__`. Commit and run **Forever v3.0 Bilingual and Semantics Triage** under GitHub Actions. Download artifact `forever-v30` and upload `forever-v30-diagnostics.json` (and, if possible, `forever-v30-bilingual-quests.json`).

## What is included
- `scripts/build_v30.py`: builds ID-keyed `enUS` / `deDE` quest dataset with fallback metadata; measures translation coverage for quest IDs >=90000 and required level <=30; gathers focused source snippets **excluding correction assignments**.
- `web/quest-language.js`: a frontend integration adapter for the v2.8 language selector. Use `mountLanguageSelector(container)` and `bindQuestNameElements(root, await loadQuestNames(url))`; render names in elements with `data-quest-id="92595"`. Switching language updates names without route recalculation.
- `web/language-demo.html`: **standalone preview**, not an automatic replacement for your unknown existing GitHub Pages frontend. To host the preview, copy the generated JSON to `data/forever-v30-bilingual-quests.json` and publish the web directory. Adjust the fetch URL to your Pages base path when needed.
- Automated regression tests and a GitHub Actions workflow.

## Strict caveats
- The source has 3556/5232 German names in v2.9; the new report measures subsets without fabricating translations.
- No external game-client translations are claimed or imported.
- Source snippets do not establish executable prerequisite AND/OR logic, zero race mask behavior, faction availability, or in-game playability. **Route remains blocked**.
- The current repository frontend has not been supplied; therefore **actual existing website integration cannot be guaranteed**. The adapter is ready for integration when the current site source is available.
