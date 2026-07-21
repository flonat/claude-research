---
name: reorg
description: "Use when you need content-aware file reorganisation or deduplication driven by a LOCAL model (Ollama on the Mac Mini) that actually reads each file's contents, not just its name — proposes a folder structure or finds exact/near duplicates, always dry-runs first, and executes only on approval with a full undo. Triggers: 'reorganise this folder', 'tidy up Downloads with the local model', 'reorg', 'find duplicate files', 'dedup this folder', 'sort these files by reading them'."
skill-dependencies: []
---

# reorg — local-model file reorganiser

Conversational front-end for the `local-reorg` CLI (`scripts/local-reorg/`). The CLI runs a
**local Ollama model on the Mac Mini** that reads each file's content and proposes where it
should go, or finds duplicates. Nothing is ever moved without your approval, and every run
is reversible.

## When to use

- "Reorganise / tidy / sort this folder" where you want the model to **read** files, not
  just pattern-match filenames.
- "Find duplicates" / "dedup this folder" (exact + near-duplicate via embeddings).
- General clutter (Downloads, Desktop, a messy project subfolder).

For research-project *structural* changes use an installed project-renaming or
project-initialization workflow; if none is available, use a normal reviewed `git mv`
plan with explicit backlink and configuration checks. For meeting `to-sort/` inboxes,
use the project's inbox-processing workflow. This skill is general-purpose file tidying.

## How to invoke the CLI

First `hostname`:

- **On the Mac Mini** (`[server]`): the `reorg` shim is on PATH — call `reorg …` directly.
- **Anywhere else** (MacBook, etc.): run the installed Mini wrapper over SSH:
  `ssh mini '~/.local/bin/reorg <args>'`

The model + files both live on the Mini, so resolve the target using the Mini's
Task Management path registries before invoking the wrapper. Do not embed
either machine's physical Dropbox root. If you cannot resolve the path
unambiguously, ask.

## Workflow

1. **Confirm the target folder** and pick a mode with the user if unclear:
   - reorg by scheme: `auto` (default) · `by-type` · `by-topic` · `by-date`
   - dedup: `--dedup` (report) → `--dedup --quarantine` (move redundant copies aside)
2. **Dry-run** — never skip this:
   - reorg: `reorg <folder> [--scheme X] [--recursive]`
   - dedup: `reorg <folder> --dedup`
   The CLI writes `<folder>/.reorg/plan.md` (reorg) or `.reorg/duplicates.md` (dedup).
3. **Read the plan file and summarise it for the user** — group counts, notable moves, and
   any `⚠low-conf` items. Do not dump the whole file; give a scannable summary and the path.
4. **Get approval.** The user may edit `.reorg/plan.json` first (trim/retarget moves).
5. **Execute** only after a clear yes:
   - reorg: `reorg <folder> --apply` (add `--yes` if ≥20 moves — tell the user it's the
     break-the-glass threshold)
   - dedup: `reorg <folder> --dedup --quarantine`
6. **Offer undo**: `reorg <folder> --undo` reverses the most recent applied/quarantined run
   (LIFO). Mention it after any execution.

## Options worth surfacing

- `--model gemma4:e2b` — ~1.5× faster than the default `gemma4:e4b`, slightly less accurate.
  Suggest it for large folders.
- `--max-files N` — default 200; raise for big sweeps (warn about time: ~5–6 s/file on e4b).
- `--dedup-threshold 0.95` — stricter near-match (default 0.92; paraphrases ~0.96).

## Safety (the CLI enforces; restate to the user)

- **Refuses** Overleaf (`Apps/Overleaf/`), the vault (`vault/`), AI client homes, and
  anything under `data/raw/` or `.git/`. Don't try to work around this.
- **Never deletes.** Reorg moves into subfolders; dedup *quarantines* into `.reorg/duplicates/`.
- **git mv** for tracked files; **undo manifest** on every applied run.
- The dry-run → approve → apply loop is mandatory. Do not run `--apply`/`--quarantine`
  before showing the plan and getting a yes.

## Requirements

Ollama must be running on the Mini with `gemma4:e4b` (or the chosen model) + `nomic-embed-text`
for dedup, plus `pdftotext`. All present as of setup. If Ollama is unreachable the CLI exits
with a clear message — relay it rather than guessing.
