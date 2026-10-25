# Forever Optimizer v2.9 — German Quest Name Parser Fix

The v2.8 diagnostic revealed that `l10n/Forever/lookupQuests/deDE.lua` uses
`l10n.questLookup["deDE"] = loadstring([[return { [ID] = {"title", {"objective"}}, ... }]])`.
The old parser expected `[ID] = "title"`, incorrectly reporting zero matches.

This release matches the first quoted string in each numeric-keyed record as the
German title, joins exclusively on quest ID, and preserves the English fallback.
No quest is promoted to playable; prerequisites and race semantics remain unverified.

## Run

Overlay the ZIP at repository root (do not upload `__pycache__`), commit, then run
GitHub Actions → **Forever Localization Parser Fix v2.9** → Run workflow.
Download `forever-localization-v29` and provide:

- `forever-localization-v29.json`
- `forever-quest-names-v29.csv`

The `web/language-selector.js` module from v2.8 is unchanged; it is not automatically
integrated into an unknown frontend. Language must remain display-only.
