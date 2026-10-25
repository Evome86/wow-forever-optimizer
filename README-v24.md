# WoW Forever Optimizer v2.4 – Conservative Eligibility Audit

Apply ZIP **over the existing GitHub repository**, retaining v2.3 exporter scripts and tests. Commit/push and run **Forever Eligibility Audit v2.4** from GitHub Actions. Download artifact `forever-eligibility-v24` and send `forever-eligibility-v24-summary.json` and `forever-eligibility-v24.json` (zip if necessary).

This workflow regenerates the native v2.3 dataset and audits all quests for a **Horde Skyborne Druid, levels 1–30**. It records explicit race/class/level exclusions, unresolved zero-mask semantics, unverified quest prerequisites, and source references. CSV is suitable for manual inspection.

**Safety:** `CANDIDATE_REQUIRES_VALIDATION` means only that no explicit race/class/level mask excluded the quest. It is **NOT** a verified playable quest. `requiredRaces=0` is UNKNOWN, not automatically 'all races' or 'disabled'. `preQuestSingle` is a list of possible dependency references; the exporter does **not** assume AND or OR semantics. `nextQuestInChain` is a hint, not a prerequisite. Faction and class bit constants are hypotheses from source analysis; in-game validation still required. No XP/hour or routing estimates.

The full quest JSON is regenerated in workflow but is **not uploaded again** to avoid unnecessary artifact size; use existing v2.3 artifact if needed.
