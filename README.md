# WoW Forever Optimizer v1.7 – Runtime Semantics Source Probe

Focused, source-line-based audit for **Horde Skyborne**. Searches race-related files for actual race symbol declarations (avoiding unrelated NPC `NONE`), finds config/loader references and relevant merge code, and records exact quest blocks for 94414, 92595, 92871 and 93836.

**Evidence-only**: this release deliberately does not claim to have executed Lua, resolved race masks, proved patch precedence, or validated route eligibility. The 94414 conflict remains an open question until runtime semantics are verified.

## Installation
Extract this ZIP into the root of the existing `Evome86/wow-forever-optimizer` repository, preserving directory structure; commit. In GitHub Actions run **Forever Runtime Semantics v1.7**, download artifact `forever-runtime-semantics-v17`, and upload `forever-runtime-semantics-v17.json` here.

Pinned upstream QuestieDB commit: `5c094f6e9a264f0dc54e2fde9731a37a97ed197c`. Python standard library only. No paid API.
