# WoW Forever Optimizer – v0.2 Data Foundation

This is an **audit-only milestone**, not a quest importer or route optimizer.

## Setup
1. In your public GitHub repository, upload the **contents** of this package, preserving the paths `.github/workflows/questiedb-audit.yml` and `scripts/audit.py`. Keep your existing `index.html`.
2. In **Settings → Actions → General → Workflow permissions**, select **Read and write permissions** and save. If organization/repository policy prevents this, ask before proceeding.
3. Open **Actions → QuestieDB Forever source audit → Run workflow → Run workflow**.
4. Wait for a green result. Open `data/source-audit.json` on the Code tab.
5. Verify `status` equals `inventory_only`, `candidate_file_count` is positive, and `source_commit` is a full Git commit SHA.

The audit records filenames, file sizes and SHA-256 hashes for paths containing `Forever` or `Camelot`. It does **not** prove that the data is complete, extract actual quest records, or calculate a route. A green workflow means the source-inventory stage succeeded only.

## Cost and safety
This workflow is manual only, has a 10-minute timeout and uses a standard GitHub-hosted runner. It requires a public repository and GitHub Free's applicable terms/limits. It does not use a paid API or any self-hosted server. No billing or paid runners are required for this design. Source code is checked out temporarily; the audit JSON is the only published data artifact. Do not enable paid runners.

## Licensing
Before publishing extracted QuestieDB content, inspect its LICENSE.md, PROVENANCE.md, and applicable third-party data restrictions. This stage publishes only source paths and hashes.
