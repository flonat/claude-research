# Research-Only Checks

Detailed specs for Phase 1, Checks 11-17 (research mode only — skip if general mode).

## 11. Atlas Topic File

Resolve the project's atlas topic:
```bash
TM="$(cat ~/.config/task-mgmt/path)"
grep -rl "project_path:.*$(basename "$PWD")" ~/vault/atlas/ 2>/dev/null
```
If found, read it. Extract `outputs:`, `status:`, `co_authors:`, `connected_topics:`.

**Existence & naming checks:**

| Check | What to verify | Flag if |
|-------|---------------|---------|
| File exists | `grep -rl` returns a result | X "No Atlas topic file found" |
| Slug matches | Atlas filename matches CLAUDE.md `**Slug:**` | Warning: Slug mismatch |
| Title matches | Atlas `title:` matches project directory basename (Title Case) | Warning: Title drift |
| `project_path` resolves | Atlas `project_path:` points to a directory that exists on disk | Warning: Stale project_path |
| `last_worked` stamp | When this session committed work to the topic's project, stamp `last_worked` = project git mtime (`git log -1 --format=%cI -- <project>`, date portion). session-close is the **SOLE writer of `last_worked`** and NEVER writes `last_reviewed` (curation — only `/update-topic-file`). | (stamped) |
| Topic file stale | `last_worked` newer than `last_reviewed` by >14 days | Warning -- topic file drifted from the work; run `/update-topic-file` |

## 12. Outputs Drift Check

Compare local state vs atlas:

| Check | Local source | Atlas source | Flag if |
|-------|-------------|-------------|---------|
| Paper dir count | `ls -d paper*/ 2>/dev/null \| wc -l` | `outputs:` array length | Mismatch |
| Paper dir names | Sorted list of `paper*` basenames | `outputs[].venue` slugified | Mismatch |
| Venues | CLAUDE.md `**Target venues:**` | `outputs[].venue` | Mismatch |
| Output labels | Atlas `outputs[].label` | Check each has a meaningful label (not empty) | Warning if empty |
| Output status | Atlas `outputs[].status` | Should reflect actual progress | Info if stale |
| Submission-join completeness | Atlas `outputs[]` at a submission-active status (`Submitted`/`Under Review`/`R&R`/`Accepted`/`In Press`/`Camera-ready`) | Each must carry `paper_id` + `paper_title` (= registry `canonical_title`) + (if the venue is a Conference/Workshop) `cycle: <Venue> <edition-year>` | Warning if `cycle`/`paper_id`/`paper_title` missing or if `paper_title` drifts from `canonical_title` — set/align it now (journals/preprints exempt from cycle; see `rules/atlas-status-vocabulary.md` § submission-join completeness) |
| Status | CLAUDE.md `**Status:**` | Atlas `status:` | Mismatch (Info only) |
| Slug | CLAUDE.md `**Slug:**` | Atlas filename | Mismatch |

**Portfolio validator (project-independent):** run `uv run --with pyyaml python "$(cat ~/.config/task-mgmt/path)/scripts/validate-portfolio-registry.py"` — it reports `cycle-gap:` (conf/workshop submission-active output missing `cycle`), `minting-gap:` (submission-active output/submission missing `paper_id`), `title-gap:` (submission-active output missing `paper_title`), and `title-drift:` (output `paper_title` ≠ registry `canonical_title`) as WARNs across the whole vault. Report-only; surface any new gaps for the current project.

## 13. Atlas Consistency Check

Verify vault topic and submission entries:

a. **Topic entry** — search atlas for the atlas slug:
   - Use `taskflow-cli search-tasks --query "<project name>" --json` for the project name
   - Verify exactly 1 topic entry exists (not 0, not duplicates)
   - Check topic `Status` matches atlas `status:`
   - Check `Papers` relation count matches atlas `outputs:` count

b. **Submission entries** — for each atlas output, verify its linked submission:
   - Check each atlas output has a corresponding submission entry in vault
   - Flag orphaned submissions (submission with no matching output)
   - Flag missing submissions (output with no submission entry yet)
   - Verify submission venue matches atlas output venue

Use `taskflow-cli` for reads. If fixes are needed, edit the vault markdown files directly (`~/vault`) per `vault-api-fallback` rule.

## 14. Paper Directory Validation (Nested Pattern)

Each `paper*` directory should be a real directory containing a `paper/` symlink to Overleaf:

| Check | What to verify | Flag if |
|-------|---------------|---------|
| Is real directory | `test -d paper-xxx && ! test -L paper-xxx` | Warning if direct symlink -- "Should use nested pattern" |
| Has `paper/` symlink inside | `test -L paper-xxx/paper` | X "Missing Overleaf symlink inside paper dir" |
| Symlink target exists | `test -d paper-xxx/paper` (follows symlink) | X "Overleaf target missing -- sync may be broken" |
| Target in Overleaf | `readlink paper-xxx/paper` contains "Overleaf" | Warning if pointing elsewhere |
| Has `.latexmkrc` | `test -f paper-xxx/paper/.latexmkrc` | Warning "Missing build config in Overleaf dir" |
| Has main .tex | `ls paper-xxx/paper/*.tex 2>/dev/null` | Info if empty (early stage) |
| No forbidden files in symlink | No `.py`, `.R`, `.csv` etc. in `paper-xxx/paper/` | X Overleaf separation violation |
| Venue-specific files | `ls paper-xxx/ --ignore=paper` | Info -- list any checklists, cover letters, etc. |

## 15. Bibliography Status

Check if any `.bib` files exist in `paper*` dirs or `docs/`:
```bash
find paper*/ docs/ -name "*.bib" -not -empty 2>/dev/null
```
Flag if the project is beyond "Idea" stage but has no bibliography.

## 16. Backup Freshness

If `backup/` exists, check `.last-backup` timestamps:
```bash
for f in backup/*/.last-backup; do echo "$f: $(cat "$f")"; done
```
Flag if any backup is older than 7 days.

## 17. Git Project Health

Run targeted git checks relevant to research projects:

| Check | Command | Flag if |
|-------|---------|---------|
| Remote configured | `git remote -v` | No remote -- warn about backup risk |
| Uncommitted paper changes | `git status -- paper*/ backup/` | Modified `.tex`/`.bib` not yet committed |
| Branch divergence | `git log @{u}..HEAD --oneline 2>/dev/null` | Local commits not pushed (if remote exists) |
| Large untracked files | `find . -not -path './.git/*' -not -path '*/out/*' -size +5M -type f 2>/dev/null` | Files >5MB that should be gitignored |
| Nested `.git` dirs | `find . -name .git -type d -mindepth 2 -not -path './.git/*' 2>/dev/null` | Nested repos (breaks parent tracking) |

## 19. Atlas Topic Body Richness (gated update)

**The gap.** Topic file bodies often stay sparse even as a project advances to Drafting / Advanced / Submitted. Work moves into `paper-*/` and the atlas topic body — which is what `atlas.example.com` actually displays, and what future-the user reads to remember why this project exists — gets neglected. This check enforces minimum body richness scaled by status.

**Compute.** Read the atlas topic file. Body = everything after the closing `---` of the YAML frontmatter. Word count excludes markdown syntax minimally (split on whitespace is fine — order-of-magnitude accuracy is enough).

**Status-scaled thresholds** (body word count floors):

| `status:` | Floor |
|---|---:|
| Idea | 150 |
| Exploring | 150 |
| Drafting | 400 |
| Advanced | 600 |
| Submitted | 600 |
| Accepted | 700 |
| Parked | — (no floor; do not gate Parked topics) |

Calibration: thresholds sit well below current medians (e.g. Drafting median 346 → floor 400 catches the bottom half) and well above worst cases (Drafting min was 41 words). Tighten over time.

**Surface in Phase 2 drift report.** One line:

```
Atlas body:  Warning: 87 words for `Submitted` status (floor 600) -- update gate will fire
```

or, when above floor:

```
Atlas body:  OK 612 words for `Advanced` status (floor 600)
```

**Phase 3 update gate.** If below floor AND the session was substantive (not a pure infra / no-op session — heuristic: at least one file edit OR git diff non-empty), trigger the gated update step:

1. **Dispatch** `Atlas body extractor` agent in Phase 3a (parallel with others). Inputs: atlas topic file path, current body, session summary (the 3–5 bullet recap from Phase 2 step 1), `git diff --stat` of the session, list of files touched. Forbid-list (per `subagent-write-guard.md`): no git, no build, no edits outside the atlas topic file. Output: a proposed addition of 150–400 words written in the existing topic's voice, capturing what THIS session contributed — design choices, open questions answered, reviewer-risk anticipated, connections to other topics observed, etc. Returned as plain markdown (no diff markers).

2. **Phase 3c presentation.** After the parallel agents return, before memory review:
   - Print the proposed addition in a code block
   - `AskUserQuestion` with options:
     - **Accept (recommended)** — append the proposed text to the body (preceded by a `## Session update — YYYY-MM-DD` header if no current session-update section exists; otherwise merge under it)
     - **Edit** — let the user paste a revised version, then write it
     - **Skip with reason** — log the skip reason in the session log (`Atlas body update skipped: <reason>`). Allowed reasons include "maintenance session, no substantive work", "deferring to dedicated update later", "session was investigative — nothing to capture yet". The skip is recorded but doesn't block close.

3. **Where to write.** The atlas topic file at `~/vault/atlas/<theme>/<slug>.md`. Append at the END of the body (after existing sections). Do NOT touch frontmatter. Do NOT delete or rewrite existing body content.

**Skip conditions** (do not fire the gate):
- Status is `Parked` (no floor)
- No atlas topic file resolves for the CWD (general project)
- `--autonomous` flag is set AND body is above 50% of floor — autonomous mode treats it as a soft warning surfaced in the final summary, not a gate. (Below 50% of floor, even autonomous mode prompts — the gap is too large to silently let pass.)
- Body word count is already above floor — print the OK line, no gate

**Why this is its own step, not just memory:** Memory persists for Claude-side context but is not the user-readable as the canonical "what is this project about" document. The atlas topic body IS that document — `atlas.example.com/topic/<slug>` renders it directly. Updates have to land there.

## 18. Knowledge Compile Freshness (info-only)

**Surface, do not auto-invoke.** This check tells the user when the project
knowledge wiki was last compiled. It NEVER runs `/compile-knowledge`
itself — the user decides if and when to refresh.

Source of truth: the atlas topic frontmatter field
`knowledge_last_compiled: YYYY-MM-DD` (written by `/compile-knowledge`
on each run; backfilled by `scripts/backfill-knowledge-compile-dates.py`
for projects scaffolded before the field existed).

Logic:

| State | Surface |
|-------|---------|
| `knowledge/` directory missing or empty | _nothing_ (no line printed) |
| `knowledge/` non-empty, atlas `knowledge_last_compiled` set | `Knowledge: last compiled YYYY-MM-DD (Nd ago)` |
| `knowledge/` non-empty, atlas field missing | `Knowledge: N articles, no compile date recorded -- run /compile-knowledge to set baseline` |
| Project has no atlas topic | _nothing_ (no surface; not a research project for this check) |

Age phrasing:
- ≤7 days: `(Nd ago, fresh)`
- 8-30 days: `(Nd ago)`
- 31-90 days: `(Nd ago, getting stale)`
- &gt;90 days: `(Nd ago, stale -- consider /compile-knowledge)`

This is **info-only**, like the bibliography and backup checks. Print it
in the Phase 1 drift report if the project has any knowledge content;
otherwise skip silently.

## Paper-history regeneration (research mode)

If this session changed any `history:` row, registry `public:` block, or archive pointer for the project's papers, regenerate the folder mirror:

```bash
uv run "$(head -1 ~/.config/task-mgmt/path)/scripts/generate-paper-history.py" --project "$PWD"
```

Also regenerate the global precedent index when archive pointers changed: same script with `--collateral` (writes `~/vault/reports/submission-documents-index.md`).

`PAPER-HISTORY.md` is generated-only (rules/submission-file-archive.md § Topic-folder layout) — never hand-edit; a stale copy is a one-command fix, not a drift incident.
