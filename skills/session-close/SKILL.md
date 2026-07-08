---
name: session-close
description: "Use when you need to run the end-of-session checklist (uncommitted changes, focus update, project sync). Auto-detects research projects and adds atlas consistency checks."
allowed-tools: Bash(git*), Bash(curl*), Bash(grep*), Bash(taskflow-cli*), Read, Write, Edit, Glob, Grep, Skill, AskUserQuestion, Task
argument-hint: "[project-name ...] or no arguments for CWD"
---

# Closing — End-of-Session Checklist

> On-demand session wrap-up. Run `/session-close` when you're done working to make sure nothing is lost. Auto-detects whether the project is a research project (atlas topic, `paper*` directories, vault submissions) and applies additional atlas consistency checks if so.

## Auto-Detection

At the start of execution, detect the project type:

```bash
# Check for atlas topic file
ATLAS_TOPIC=$(grep -rl "project_path:.*$(basename "$PWD")" ~/vault/atlas/ 2>/dev/null | head -1)
# Check for paper directories
PAPER_DIRS=$(ls -d paper*/ 2>/dev/null | wc -l | tr -d ' ')
```

| Signal | Detected as |
|--------|-------------|
| Atlas topic file exists **OR** `paper*/` directories found **OR** vault submission entries exist | **Research project** — run full protocol with atlas checks |
| None of the above | **General project** — run base protocol only |

Print the detection result at the start:
```
Session closing for: <project-name> (<full-path>)
Mode: research / general
```

## When to Use

- End of any work session
- Before switching projects
- When the user says "wrap up", "closing time", "let's close out", "end of session"

## What It Does NOT Do

- Never runs automatically — this is user-triggered only
- Never pushes to remote unless explicitly confirmed (git is the only question asked, or `--autonomous` is set)

---

## Autonomy

Per the global `--autonomous` / `-y` convention in `~/.claude/rules/phased-work.md` § "Autonomy flag convention". Invoke as `/session-close --autonomous` (or `-y`). When set:

| Behaviour | Default | `--autonomous` |
|---|---|---|
| Phase 4 safety checks (size, anonymity, DOI) | run | **still run** — flag failures, do NOT auto-bypass (safety gates aren't a Phase 5 question) |
| Phase 5 commit `AskUserQuestion` | asks user | **skipped** — defaults to `Commit & push` if remote exists, else `Commit only` (with a one-line warning) |
| Git remote verification (`git remote -v`) | yes | yes (per `git-safety` rule — still verify before push) |
| Worktree removal (Phase 6) | asks user | **still asks** — destructive, deserves explicit consent even in autonomous mode |
| Atlas topic body gate (§19) | asks user if body < status-floor | **skipped** when body ≥ 50% of floor (surfaces as warning); **still asks** when below 50% (gap too large to ignore) |
| Memory updates, focus update, session log | run | run (no question to skip) |
| Final summary block | always | always |

**Safety gate failures under `--autonomous`**: if Phase 4 finds a >10MB staged file, an unblinded paper, or unverified DOIs, the run STOPS and surfaces the failure. The flag does NOT mean "ignore safety" — it means "don't ask the routine commit question". User must address Phase 4 failures before re-running.

**No-remote fallback**: if `git remote -v` shows no remote (e.g., a Dropbox-synced research project with no GitHub), `--autonomous` falls back to `Commit only` and prints `Warning: no remote configured — committed but not pushed`. Per `git-safety.md` G4 (wrong remote target).

Recommended invocations:

```
/session-close --autonomous     # auto-commit & push, all safety gates still active
/session-close -y               # short form
```

Use this for end-of-day wrap-ups where the commit is routine. Skip the flag for sessions touching paper-* directories (where the anonymity gate is more likely to fire and you want the gate-failure conversation rather than silent stop).

---

## Arguments

Accepts zero or more project names:
- **No arguments:** operates on CWD
- **One or more names:** resolves each to its project path (searches under Projects root, Teaching, Task Management, etc.), runs the protocol for each sequentially

Resolution order:
1. Exact match in CWD
2. Search `~/.config/task-mgmt/research-root` for a matching directory name (recursive, up to depth 3)
3. Search Task Management root for a matching directory name
4. If ambiguous, ask with `AskUserQuestion`

---

## Focus File Retention Policy

`.context/current-focus.md` is a **rolling 7-day window** of chronological session blocks. Every run of `/session-close` enforces this:

1. **Prepend** a new `## What I Just Did (<date> <time> — <headline>)` block at the top of the chronological section (just below the masthead).
2. **Update** the masthead `> Last updated:` line to match the new block's date/time/headline. The masthead is exactly three `>` lines — do not accumulate `> Earlier ...` lines.
3. **Prune** any block whose date (parsed from its `## What I` header) is older than today minus 7 days. Move pruned blocks — in the order they appear — into `.context/archive/focus-log-YYYY-MM.md` (create the file if it doesn't exist; group by the month the block belongs to). Preserve all content verbatim.
4. **Never** re-add an `Active Plan` or `Latest Session Log` section — the latest block already names its plan/log inline.

Today's date comes from the shell (`date +%Y-%m-%d`). If parsing a block header's date fails, keep the block (err on the side of retention) and flag it in the agent's summary.

## Quick Reference: What Gets Updated Where

| Action | What it writes | What it captures |
|--------|---------------|-----------------|
| **Update focus** | `.context/current-focus.md` | New session block (prepended), masthead updated, 7-day retention enforced (see policy above) |
| **Refresh project docs** | Project's own `CLAUDE.md`, `README.md`, `docs/*.md` | Stale file trees, outdated counts, next steps |
| **Sync project state** | `.context/projects/_index.md` + vault research pipeline | Project stage, target journal, co-authors, status |
| **Topic next steps** (research mode, always) | Atlas topic file `## Next steps` section | Exactly 3 checkbox to-dos (incl. readings) — the next actions for the topic; refreshed each close (see Phase 3d) |
| **Update planning state** | `.planning/state.md` | Phase progress, component status, decisions made this session |
| **Archive session log** | `log/YYYY-MM-DD-HHMM.md` (new file) | Detailed timestamped record of the full session |
| **Memory** (automatic) | Auto memory (`~/.claude/projects/<hash>/memory/MEMORY.md`) + project-root `MEMORY.md` | Infrastructure learnings -> auto memory; domain knowledge (notation, decisions, citations) -> project memory |
| **Save to context** (only if needed) | Any file in `.context/` (profile, people, workflows) | New collaborators, preferences, workflow changes -- facts to persist beyond this session |

---

## Protocol

Four phases: **pre-flight**, **scan**, **execute**, **commit**.

**Everything is automatic except the git decision in Phase 4.** No interview, no multi-select. The only question asked is whether to commit/push.

### Phase 1: Pre-flight

Three setup steps:

1. **Sync auto-memory** to the shared location so it gets committed with the repo:
   ```bash
   bash "$(head -1 ~/.config/task-mgmt/path)/scripts/sync-push-memory.sh"
   ```
2. **Auto-detect mode** (research vs. general -- see "Auto-Detection" section above).
3. **Validate working directory.** Resolve CWD to its project name. Print: `Session closing for: <project-name> (<full-path>)`. If CWD is a parent directory (e.g., Projects root instead of a specific project), warn: *"CWD appears to be a parent directory, not a project. Session log and focus update will proceed, but project docs refresh is skipped."* Do NOT write project-specific files to parent directories.

Output paths must resolve to Task Management or the current project directory:
- `.context/current-focus.md` -> Task Management
- `log/YYYY-MM-DD-HHMM.md` -> Task Management
- `CLAUDE.md`, `README.md`, `MEMORY.md`, `.planning/state.md` -> CWD or project root

### Phase 2: Scan

Run all checks in parallel:

1. **Session summary** -- prepare a 3-5 bullet recap of what was done this session.
2. **Project type** -- check for `CLAUDE.md` and/or `README.md` in CWD. This single check gates project-docs refresh, project-state sync, and vault sync.
3. **Git state** -- `git rev-parse --is-inside-work-tree`, then `git status` + `git diff --stat`.
4. **Planning state** -- check for `.planning/state.md` in CWD or project root (via `git rev-parse --show-toplevel`).
5. **Memory candidates** -- scan session for learnings, gotchas, decisions worth persisting.
6. **Memory health** -- count entries in both MEMORY.md files (auto + project). Flag if either exceeds **~80 entries** (≈ 2 screens of scrolling -- past that, navigation and dedup-grep get unwieldy).
7. **Session incidents** -- stuck moments, wrong-approach events, rollbacks, or non-obvious multi-step discoveries.
8. **Convention candidates** -- two sources:
   - **Practice-propagation queue.** Read `log/practice-propagation-queue.md` (auto-populated by `hooks/propagate-feedback-memory.py` whenever a `feedback_*.md` auto-memory is written). Each unchecked `- [ ]` line is a candidate for propagation into a TM guide.
   - **Session declarations.** Scan the current session for declarations of new conventions / practices -- phrases like "from now on", "papers default to", "always use X, not Y", "convention is", "never X". Match against the canonical guides (`docs/reference/conventions.md`, `docs/reference/coding-standards-*.md`, `docs/guides/*.md`, `CLAUDE.md`).

**Research-only checks** (skip in general mode): see [`references/research-checks.md`](references/research-checks.md) for atlas topic, outputs drift, vault consistency, paper-dir validation, bibliography, backup freshness, git-project health, atlas topic body richness (gated update; see §19), and knowledge-compile freshness (info-only; never auto-invokes `/compile-knowledge`).

**Drift report** (research mode only): if any research check failed, present a single drift summary before Phase 3. Example:

```
Research consistency check:
  Atlas topic:     OK found (ai-safety-governance/privacy-compliance-gaming.md)
  Pipeline drift:  Warning: 2 paper dirs but atlas has 3 outputs -- needs update
  Vault:
    Topic:         OK 1 entry, status matches
    Submissions:   OK 2 submissions linked
  Overleaf:
    paper-ccs/:    OK symlink valid, .latexmkrc present
    paper-rg/:     Warning: .latexmkrc MISSING
  Bibliography:    Warning: no .bib files (project status: Drafting)
  Git project:     Warning: no remote configured -- backup risk
  Knowledge:       last compiled 2026-04-12 (34d ago, getting stale)
```

### Phase 3: Execute

Three sub-steps -- run sequentially because (b) depends on (a)'s file writes and (c) reports on both.

#### 3a. Parallel agents

Launch **all applicable agents in parallel** (subagent_type: "general-purpose"). Wait for all to complete before 3b.

| Agent | When it runs | What it writes |
|-------|-------------|---------------|
| Focus agent | Always | `.context/current-focus.md` -- prepend new session block, update masthead, prune >7d (see retention policy above) |
| Session log agent | Always | `log/YYYY-MM-DD-HHMM.md` -- timestamped archive (includes Collaboration quality line, see below) |
| Project docs agent | If `CLAUDE.md` or `README.md` in CWD | Project `CLAUDE.md`, `README.md` -- stale trees, counts, next steps |
| Project state agent | If `CLAUDE.md` in CWD | `.context/projects/_index.md` -- stage, journal, status |
| Planning state agent | If `.planning/state.md` exists | `.planning/state.md` -- phase progress, decisions |
| Atlas update agent | Research mode + drift detected | Atlas topic `outputs:`, `status:`, open questions |
| Vault submission agent | Research mode + drift detected | Vault submission entries (file edits to `~/vault`). When the drift being synced IS a submission event (submitted / reviews-in / decision / camera-ready), also append the dated `history:` row per `rules/submission-file-archive.md` § history — part of the same writeback, not an afterthought |
| Atlas body extractor | Research mode + topic body below status-floor (see §19) | Proposed 150–400-word addition to the topic body, returned as plain markdown — applied in Phase 3c after user confirmation |

**Memory updates** also happen here in the main context (fast appends -- no agent needed):
- Auto memory (`~/.claude/projects/<hash>/memory/MEMORY.md`): infrastructure learnings, tool gotchas
- Project memory (project-root `MEMORY.md`): domain corrections, key decisions (per `learn-tags` rule)

#### 3b. Vault sync (main context only)

**Why a top-level step:** MCP tools are permission-scoped to the main conversation -- they do not work inside sub-agents. Vault writes that need MCP must run here, after agents complete.

If research mode and drift was detected (or vault submission entries changed in 3a), call `vault sync (edit vault files directly)` from the main context. Skip silently otherwise.

#### 3c. Memory review, knowledge filing, follow-ups

Show memory updates from 3a:

```
Memory updates:
  Auto memory:    + "zsh `status` is read-only -- use `result` instead"
  Project memory: + [LEARN:notation] Treatment is D_i not T_i
                  + Key Decision: Use CS estimator (staggered treatment)
```

If nothing was saved: `Memory: nothing to save this session.` the user can say "undo" to adjust.

**Research memory prompts** (research mode only): scan session for uncaptured learnings in these categories. Only prompt where the session had relevant activity.

| Category | Example |
|----------|---------|
| Notation | `[LEARN:notation] Readability is r_i not R_i` |
| Estimand | Estimand Registry entry |
| Citation | `[LEARN:citation] Muguiro key is muguiro2026teens` |
| Method | Key Decisions table entry |
| Domain | `[LEARN:domain] AADC applies to UK only, not EU-wide` |

**Collaboration quality** (always-on, one line in the session log). The Session log agent in 3a writes a single honest sentence covering direction-setting, intellectual contribution, and iteration discipline. No scores, no separate file. If the session was purely mechanical (compilation, file moves, infra), the agent writes: `Collaboration quality: mechanical session, n/a.`

**Atlas topic body gate** (research mode + body below status-floor; see §19). After the parallel agents return, if the Atlas body extractor produced a proposal, present it before memory review:

1. Print the proposed addition in a fenced block.
2. `AskUserQuestion`: **Accept** (recommended) / **Edit** / **Skip with reason**.
3. **Accept** → append to the atlas topic file body, prefixed with `## Session update — <date>` (or merged into an existing session-update section).
4. **Edit** → paste revised text → write that instead.
5. **Skip with reason** → log `Atlas body update skipped: <reason>` in the session log. Common reasons: maintenance session / investigative session / deferring to dedicated update.

Under `--autonomous`, this gate fires only when body is below 50% of floor; otherwise the line surfaces in the final summary as a warning. See §19 for the full skip-condition list.

#### 3d. Topic next-steps to-dos (research mode — ALWAYS, not drift-gated)

Every research-mode close records the next actions for the topic **on its atlas topic file**, so they are waiting when the topic is next picked up. This runs on every research close (independent of the drift/body gates above).

1. **Derive exactly 3 concrete next-step to-dos** for the topic — the same next-actions synthesised for `.context/current-focus.md`, re-expressed at topic level. Draw them, in priority order, from: unresolved review open-issues (`reviews/INDEX.md`), imminent deadlines (< 30 days), blindspot virtues / opportunities, and **specific readings to do** (papers to read next — name them by author-year or citekey). Each must be actionable — "Read Foo & Bar 2025 on X", "Add the \(u_R\) sensitivity to prior(G)", "Draft the §5 welfare corollary" — never vague ("improve the paper"). Preserve `[UNVERIFIED]` on any un-checked reading per `mark-unverified`.
2. **Write them to the atlas topic file** (`~/vault/atlas/<theme>/<slug>.md`) as a **maintained** `## Next steps` section of checkbox items:

   ```
   ## Next steps
   <!-- maintained by /session-close; refreshed each research close -->
   _As of YYYY-MM-DD:_
   - [ ] <to-do 1>
   - [ ] <to-do 2>
   - [ ] <to-do 3>
   ```

   If a `## Next steps` section already exists, **replace its body** with the new 3 (do not accumulate stale lists across closes). Otherwise append the section at the end of the topic body. This is body content, not frontmatter — no controlled-vocabulary concern. The vault is **not git**: the edit is complete once written (no commit). Runs in the main context (plain vault file, no MCP needed), or fold into the Atlas update agent's remit when that agent is already dispatched.
3. **Under `--autonomous`** this still runs with defaults, no prompt. If the session genuinely produced no sensible next step (pure infra / maintenance close), write a single `- [ ] <one obvious next action>` and note the thinness in the summary rather than fabricating three.

**Knowledge filing** (research mode only). Depends on `/compile-knowledge` having created a `knowledge/` directory in the project. If absent, skip silently -- do not create one. Otherwise, for each finding, file it into the relevant article via the `/store-insight` pattern (read `knowledge/_index.md`, append to Key Findings with session date, create new article if no match), then update `_index.md` last-updated dates.

Report:
```
Knowledge filed: 2 findings -> concept-a.md, 1 finding -> concept-b.md (new article)
```

**Follow-up suggestions** (never blocking):

- **Memory bloat:** if either MEMORY.md > 80 entries -> `"MEMORY.md has N entries -- consider /memory-cleanup."`
- **Memory staleness:** project MEMORY.md has entries dated >90 days old -> `"oldest entry from <date> -- consider /memory-cleanup."`
- **Incident detected:** stuck moments / rollbacks / wrong-approach events -> `"Consider /postmortem."`
- **Skill-worthy discovery:** non-obvious multi-step workflow (not a one-liner) -> `"Consider /skill-extract."`
- **Code review nudge:** `.py`/`.R`/`.jl`/`.do` files modified this session (`git diff --name-only` + `git ls-files --others --exclude-standard`) AND no `correspondence/internal-reviews/CODE-REVIEW-REPORT.md` produced -> `"You modified N code files -- consider /code-review."`
- **Convention propagation nudge:** if Phase 2 step 8 found queue items OR session-declared conventions -> list them with their suggested guide targets and prompt: `"N convention candidate(s) found -- propagate to TM guides now (Y/n)?"`. If yes, present each candidate one at a time with the suggested target doc, ask whether to (a) edit the guide now, (b) defer to monthly /docs-consistency cron, or (c) drop. On edit/defer, mark the queue item by changing `- [ ]` to `- [x]`. On drop, remove the line. Queue file is auto-truncated by the monthly cron after listing.

### Phase 4: Pre-commit verification

Run three checks against the staging area BEFORE asking about commit. Block close if any fails — user must address before committing.

| Check | What | Pass | Fail |
|---|---|---|---|
| **Size** | Any staged file >10MB | proceed | print path + size; suggest `.gitignore` or `git reset HEAD <file>` |
| **Anonymity** (research mode + `paper-*/` paths staged) | Scan staged `.tex`/`.bib` for author / affiliation strings (the user's names + institution names) | proceed | print matches; suggest blinding before commit |
| **DOI verification** (research mode + new `.bib` entries staged) | For each newly-added `@article`/`@inproceedings` in staged `.bib`, run `scholarly scholarly-verify-dois` (batch ≤50 per call) | proceed | print unverified keys; suggest manual verification or `[UNVERIFIED]` flag |

If a check fails:
1. Print the failures
2. Ask: "Address these before commit, or proceed with `--force` (risky)?"
3. Only proceed to Phase 5 (Commit) on user confirmation

The DOI check can be slow (~30-60s per batch). Skip it silently if `scholarly` is unavailable or the staged change has no new bib entries.

### Phase 5: Commit (only manual step)

This is the **only** point where `/session-close` asks a question — UNLESS `--autonomous` / `-y` is set, in which case the question is skipped and the default is taken (see § Autonomy).

1. Run `git status` (never `-uall`) and `git diff --stat`.
2. If uncommitted changes exist:
   - **Default mode**: ask with `AskUserQuestion`:
     - **Commit & push (recommended)** -- stage, commit, push
     - **Commit only** -- stage, commit, no push
     - **Skip** -- leave uncommitted
   - **`--autonomous` mode**: skip the question. Default to `Commit & push` if `git remote -v` shows a remote; otherwise `Commit only` with `Warning: no remote configured — committed but not pushed`. Surface the chosen action in the final summary.
3. Before pushing, verify a remote with `git remote -v`. If no remote, fall back to commit-only with a warning (applies in both modes).

If not a git repo, skip silently.

### Phase 6: Worktree hygiene (if applicable)

If `pwd` is inside a git worktree (not the main checkout), check whether the current branch can be safely cleaned up. Run this AFTER Phase 5 so any final commit is in place.

1. **Detect worktree.** `git worktree list --porcelain` lists multiple entries AND the current path is not the main worktree (`git rev-parse --git-common-dir` ≠ `git rev-parse --git-dir`).
2. **Skip silently** if not in a worktree.
3. **Safety checks** (all must pass to offer removal):
   - **No uncommitted changes:** `git status --porcelain` is empty.
   - **Branch fully merged into local `main`:** `git merge-base --is-ancestor HEAD main` returns 0. Check `main` (local), not `origin/main` — merge happens locally even when push is deferred.
4. **If all pass**, offer with `AskUserQuestion`:
   - **Remove worktree + branch (recommended)** — runs from the main checkout, since git refuses to remove the worktree you're currently in:
     ```bash
     MAIN_REPO=$(git rev-parse --git-common-dir | xargs dirname)
     WT_PATH=$(pwd)
     BRANCH=$(git branch --show-current)
     # Move out of the worktree first
     cd "$MAIN_REPO"
     git worktree remove "$WT_PATH"
     git branch -d "$BRANCH"
     ```
     If `main` hasn't been pushed yet (`git -C "$MAIN_REPO" log origin/main..main` non-empty), warn: *"main is N commits ahead of origin/main — push when ready."*
   - **Keep** — leave both in place.
5. **If checks fail**, print one-line state and skip the offer (never auto-remove):
   - `Worktree: <name> on branch <X>, N commits not in main — leaving as-is.`
   - `Worktree: <name> has uncommitted changes — leaving as-is.`

The check intentionally lives at session close because that's when "this work is done" is most likely true. The two safety gates (clean tree + merged into main) are non-negotiable — auto-removing an unmerged worktree silently destroys commits.

---

## Output

After Phase 6, print a summary block. Lines for both modes:

```
Session closed [(research)]:
  Focus / Project docs / Planning state / Memory / Session log / Git / Worktree
```

The **Worktree** line only appears when in a worktree. Values: `removed (branch <X> deleted)` / `kept (N commits not in main)` / `kept (uncommitted changes)` / `kept (declined)`.

**Research mode adds:** Atlas consistency, Vault submissions, Knowledge filing, Bibliography presence, Git project state (nested repos, unpushed commits, no-remote warnings).

Each line shows status (`updated` / `skipped` / `OK aligned` / `Warning: <detail>` / `committed (abc1234)` / `committed & pushed`).

---

See [`references/design-notes.md`](references/design-notes.md) for design rationale and key decisions.

## Cross-References

See [`references/related-skills.md`](references/related-skills.md) for the full table of related skills and their relationships to this one.
