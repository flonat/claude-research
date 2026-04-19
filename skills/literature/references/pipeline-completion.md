# Literature — Phase 6d: Pipeline Completion (Pipeline Mode Only)

> Skip entirely in standalone mode. Runs after Phase 6b passes (bib-validate clean) and Phase 6c completes.

## 1. Vault Sync

Update the vault topic entry with new paper count or related metadata. Use `taskflow-cli update-task --task-slug <slug> --description "..."` if a related task exists (find with `taskflow-cli search-tasks --query "<topic>" --json`).

## 2. Knowledge Wiki Filing

If `knowledge/` exists in the project directory:

- For each new paper added, extract a one-line key finding
- File each finding into the relevant knowledge article
- If no matching article exists, create one for the concept
- Skip silently if no `knowledge/` directory exists

## 3. Auto-Commit (Hard Gate)

Only commit if bib-validate passed clean. Do NOT commit if issues remain.

```bash
cd "$PROJECT"
git add <bib-file> <lit-review-file>
git commit -m "literature: add N papers for <topic-slug>"
```

Do NOT push — verify remote first per git-safety rule.

## 4. Final Summary (Pipeline Mode)

```
Literature pipeline complete for <topic>

Papers added: N (M already held, K new)
Bib file: <path> — N total entries
Lit review: <path> — updated/created
Knowledge: filed N findings to knowledge/ (or: skipped — no knowledge dir)
Vault: <topic entry updated>
Bib-validate: PASS
Commit: <hash>

Next: review new entries, push when ready
```
