# WoW Forever Optimizer v2.8 — language selector + localization diagnostics

Copy the ZIP contents into the **root** of `Evome86/wow-forever-optimizer`. Commit and push. In **Actions**, run **Forever Localization Diagnostics v2.8**, download artifact `forever-localization-v28`, and provide `forever-localization-v28.json` plus `forever-quest-names-v28.csv`.

## Website integration

The ZIP **does not overwrite your existing frontend** because its layout was not provided. Import `web/language-selector.js` in the existing site and mount into your character configuration:

```js
import { mountLanguageSelector, getLanguage, questName, translate } from './web/language-selector.js';
mountLanguageSelector(document.querySelector('#character-settings'));
// Render questName({id:92595,names:{enUS:'The Windshapers',deDE:null}},getLanguage())
// Listen for 'forever:language-changed' and rerender labels/quest names only.
```

Language is a presentation preference independent of faction/race/class/route. Default is deDE; English fallback is automatic. Never translate quest IDs or modify route calculation based on language.

## Data safety

The v2.7 parser reported 0 names from a 590 KB file. v2.8 recognizes numeric and English-name keyed Lua table entries, but the actual source syntax is **not confirmed**. If parsing fails, the workflow fails deliberately and uploads a diagnostic source sample. This is *not* evidence that translations are absent. Name-key matches can be ambiguous when English quest names are duplicated; prefer ID-keyed source if available. No eligibility/AND-OR semantics are promoted to verified.
