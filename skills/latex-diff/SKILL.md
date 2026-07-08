---
name: latex-diff
description: "Use when you need to see what changed between two versions of a LaTeX document — two files, two project directories, or two git revisions. Produces a human-readable change summary plus a machine-readable, severity-graded list of semantic changes."
allowed-tools: Bash(latexdiff-agent:*), Bash(git show:*), Bash(git diff:*), Bash(git worktree:*), Bash(git log:*), Bash(mktemp*), Bash(mkdir*), Bash(ls*), Bash(rm*), Read, Glob, Grep
argument-hint: [old] [new]  (files, dirs, or git revisions)
---

# LaTeX Diff

> Compare two versions of a LaTeX document and report what actually changed —
> text, equations, citations, labels/refs, section titles, macros, environments,
> file add/remove, and moves — each graded by severity. Wraps the `latexdiff-agent`
> CLI (`packages/latex-diff`). Member of the `latex-*` source/build family.

## When to Use

- "What changed between these two versions of the paper?"
- Building an R&R "summary of changes" or a preprint vN→vN+1 changelog
- Focusing a re-review on the changes that matter (semantic-impact only)
- Sanity-checking a co-author's edits before merging

## When NOT to Use

- **Compiling** a document → `/latex`
- **Prose quality / proofreading** → `/proofread`
- A raw line diff is enough → `git diff` (this skill is LaTeX-aware: it knows a
  changed `\cite` key from a reflowed paragraph)

## What it produces

Two views from the same canonical diff:

1. **Human summary** — grouped by file and section, every line carrying a change
   `id`, a severity badge, and a `file:line` location.
2. **Machine-readable JSON** — severity-graded `ChangeRecord`s. `semantic_impact:
   true` flags the changes a reviewer should actually read.

Severity ladder: `trivial < low < medium < high < critical`. Change types:
`formatting_only, text, equation, citation, label_ref, environment,
section_title, macro_definition, file_add, file_remove, move, other`.

Full flag reference: [`packages/latex-diff/README.md`](../../packages/latex-diff/README.md).

## Critical rules

1. **Read-only.** This skill never edits the paper. It reports; the human (or a
   downstream skill) decides what to do.
2. **`paper/` is LaTeX-only** — when extracting git revisions to temp dirs, write
   temp copies under `/tmp`, never inside an Overleaf-synced `paper/`.
3. Clean up any `git worktree` / temp dirs you create.

## Protocol

### 1. Resolve the two inputs

| Input form | How to run |
|------------|-----------|
| **Two files** | `latexdiff-agent OLD.tex NEW.tex …` |
| **Two project dirs** (multi-file, `\input`/`\include`-aware) | `latexdiff-agent OLD_DIR/ NEW_DIR/ …` |
| **Two git revisions of one file** | extract each, then diff (below) |
| **Two git revisions of a whole project** | `git worktree` each, then diff dirs (below) |

Single file across revisions:

```bash
git show <REV_OLD>:<path/to/main.tex> > /tmp/ld-old.tex
git show <REV_NEW>:<path/to/main.tex> > /tmp/ld-new.tex   # omit for working tree
latexdiff-agent /tmp/ld-old.tex /tmp/ld-new.tex --summary -
```

Whole project across revisions (multi-file):

```bash
git worktree add /tmp/ld-old <REV_OLD>
git worktree add /tmp/ld-new <REV_NEW>
latexdiff-agent /tmp/ld-old/<paper-dir> /tmp/ld-new/<paper-dir> --summary - --compact --semantic-only
git worktree remove /tmp/ld-old && git worktree remove /tmp/ld-new
```

> Resolve revisions with `git log --oneline -- <path>` when the user names a
> round ("since submission", "v1") rather than a SHA. If ambiguous, ask.

### 2. Run the diff

Get both views in one pass — the human summary to read aloud, and the
semantic-only JSON to reason over:

```bash
latexdiff-agent <OLD> <NEW> --summary -                 # human view
latexdiff-agent <OLD> <NEW> --compact --semantic-only   # the changes that matter
```

Useful filters (compose freely): `--min-severity high`, `--type citation`,
`--section Methods`, `--file sections/intro.tex`. Add `--json diff.json` /
`--summary summary.md` to save artefacts when the user asks.

### 3. Report

1. Lead with the summary line: total changes, semantic-impact count, impact score.
2. List the **semantic-impact** changes grouped by section, each with its
   `file:line`, type, and severity. These are the ones worth attention.
3. Note (don't dump) the trivial/formatting/move changes as a count.
4. If the user wanted a changelog or response-letter "summary of changes", phrase
   the semantic changes as prose bullets — but **do not edit the manuscript**
   (`rules/manuscript-edit-budget.md`); hand the bullets back for them to place.

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/latex` | Compiles documents; this skill compares versions of them |
| `/strategic-revision` | Consumes this to auto-draft the R&R "summary of changes" |
| `/preprint` | Consumes this for a vN→vN+1 changelog on version bump |
| `paper-critic` / `referee2-reviewer` | Can take `--semantic-only` JSON to focus a re-review on what changed |
| `packages/latex-diff/README.md` | Full CLI flags, schema, and design notes |
