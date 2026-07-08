---
name: pre-commit-audit
description: "Use when you need a fast pre-commit safety scan: file size, anonymity (author / affiliation strings in tex/bib), and hardcoded secrets. Triggers: 'audit before commit', 'check before push', 'pre-commit scan', 'safety check'."
allowed-tools: Read, Bash(git*), Bash(grep*), Bash(find*), Bash(stat*), Bash(numfmt*), Bash(wc*), AskUserQuestion
argument-hint: "[--staged | --unstaged | --all]"
---

# Pre-Commit Audit — File Size, Anonymity, Secrets

> Three-pass safety scan before commit. Blocks pain-points: oversized commits (1.3GB parquet incident), CCS-style anonymity breaches, leaked credentials. Each pass is a hard gate; user OKs proceed.

## Hard Rules

### Existential — block proceed

1. **Size pass blocks anything >10MB unless gitignored OR user explicitly approves.** Threshold matches `block-large-files.sh` hook for consistency.
2. **Anonymity pass runs only on paper-relevant paths**: `paper-*/`, `*.tex`, `*.bib`, `*.md` inside paper directories. Scope is data-driven — we don't false-flag README authorship.
3. **Secrets pass uses an entropy heuristic + known-prefix list.** No regex-only matching that misses high-entropy keys. Block on confirmed secret; warn on suspicious-but-uncertain.
4. **All three passes run on the same file set** (default: staged for commit). Don't mix staged-only size check with all-files anonymity check.

### Format — catch in review

5. Output a single consolidated table (file × pass × verdict) — not three separate reports.
6. Severity tiers: BLOCK (must fix), WARN (proceed with confirm), OK.
7. Always show the file path and line number when flagging — make it copy-paste-fixable.

## When to Use

- Before any `git commit` on a paper / project repo
- Pre-submission checklist (research projects)
- Before pushing to anonymous-artifact repo (the highest-risk anonymity surface)
- After a sub-agent has written files (verify before committing their work)
- Wired as a `/session-close` Phase 4 sub-step (alternate path to running the hook)

## When NOT to Use

- Before commits on infrastructure-only changes (skills, hooks, rules) — anonymity scan would false-flag README author lines
- Auto-generated commits (CI, dependabot) — they don't need the scan
- When the change is purely metadata (`.gitignore`, `LICENSE`, etc.)

## Modes

| Invocation | Scope |
|---|---|
| `/pre-commit-audit` | Staged files (default) |
| `/pre-commit-audit --staged` | Same as default |
| `/pre-commit-audit --unstaged` | Modified-but-not-staged files |
| `/pre-commit-audit --all` | Working tree + staged |

## Architecture

```
Phase 1 (size)        → find files >10MB; check .gitignore status
Phase 2 (anonymity)   → grep paper paths for author/affiliation/email
Phase 3 (secrets)     → entropy + prefix heuristics on all staged files
Phase 4 (consolidate) → single table; user OK to proceed
```

## Phase 1: Size

```bash
THRESHOLD_BYTES=$((10 * 1024 * 1024))

git diff --cached --name-only --diff-filter=ACM | while read f; do
    if [ -f "$f" ]; then
        size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
        if [ "$size" -gt "$THRESHOLD_BYTES" ]; then
            ignored=$(git check-ignore "$f" 2>/dev/null && echo "ignored" || echo "tracked")
            echo "$f|$size|$ignored"
        fi
    fi
done
```

Verdict: BLOCK if any tracked file >10MB. WARN if gitignored but staged anyway.

## Phase 2: Anonymity

**Single source of truth:** [`skills/_shared/double-blind-anonymity-checklist.md`](../_shared/double-blind-anonymity-checklist.md) holds the authoritative pattern list (paper-side P1-P8, artifact-side A1-A6) plus the CCS 2026 #1328 incident report that motivates the checks. Both `/pre-commit-audit` (this skill) and `/anonymous-artifact` reference it; do not duplicate the patterns inline.

Scope for `/pre-commit-audit`: only files staged for commit at paths matching `paper-*/`, `**/*.tex`, `**/*.bib`, `**/*.cls`, `**/*.sty`. The full checklist also covers structured-metadata files (`pyproject.toml`, `package.json`, `Cargo.toml`, `CITATION.cff`, etc.) — those are checked by `/anonymous-artifact` since they only matter when pushing the artifact, not on every commit.

Apply checks P1-P8 from the shared checklist:
- P1 — title page authors blinded
- P2 — no `\thanks{}` / `\acknowledgements` / `\funded` / `\grant` revealing identity
- P3 — first-person self-reference uses third person (no "our prior work")
- P4 — self-citation bib entries blinded if author overlap
- P5 — body text doesn't name authors of self-cited works
- P6 — no identifying URLs (personal sites, lab pages, repos with handles)
- P7 — PDF metadata sanitized (`pdfinfo paper.pdf`)
- P8 — figures contain no identifying watermarks/captions

For each match: print path:line and the matched text (truncated). Verdict: BLOCK on any match in a path containing `paper-*/`. WARN on matches outside paper directories.

Exception: a frontmatter-style `Made by the user` in friends-repo / public-repo READMEs is allowed (intentional attribution).

## Phase 3: Secrets

Patterns by category:

| Category | Detection |
|---|---|
| API keys with prefix | `sk-`, `sk-proj-`, `sk-ant-`, `hf_`, `gh[a-zA-Z]_`, `xoxb-`, `AIza` |
| AWS | `AKIA[0-9A-Z]{16}`, `aws_secret_access_key` |
| Generic high-entropy strings | length ≥32, base64-ish character set, no whitespace |
| `.env`-style assignments | `^[A-Z_]+=[a-zA-Z0-9+/=_-]{20,}` outside `.env.example`/`.env.template` |

Skip `.env.template`, `.env.example`, `*.example`, comment lines starting with `#`.

Verdict: BLOCK on any match in a non-template file.

## Phase 4: Consolidate + ask

Single table:

```
File                                   Size   Anon   Secrets  Verdict
─────────────────────────────────────────────────────────────────────
paper-ccs/paper/main.tex               5KB    OK     OK       OK
paper-ccs/paper/references.bib         12KB   FAIL   OK       BLOCK   (line 23: the user)
data/raw/results.parquet               1.3GB  N/A    N/A      BLOCK   (size; not gitignored)
scripts/sync-creds.sh                  2KB    OK     FAIL     BLOCK   (line 15: hf_<...>)
```

If any BLOCK rows: ask `AskUserQuestion`:
- **Fix the issues and rerun** — recommended
- **Override and proceed** — risky, requires explicit confirmation
- **Cancel commit** — abort

If only WARN rows: ask whether to proceed.
If all OK: print "Pre-commit clean ✓" and exit silently.

## Cross-References

| Skill / Hook / Rule | Relationship |
|---|---|
| `block-large-files.sh` hook | Runtime enforcement of Phase 1 (this skill is the manual / verbose counterpart) |
| `/anonymous-artifact` | The anonymity-on-publish workflow; this skill is the pre-commit equivalent |
| `/session-close` Phase 4 | Can invoke this skill as part of pre-commit verification |
| `mark-unverified.md` rule | Verbal counterpart for content claims; this skill handles file content |

## Anti-Patterns

- **Don't** scan binary files for anonymity strings — false positives on PDFs, images.
- **Don't** rely solely on regex for secret detection — entropy heuristics catch keys with novel prefixes.
- **Don't** auto-fix issues — surface them for the user to handle. Auto-replacement of names risks breaking acknowledgements.
- **Don't** skip the .gitignore check — large gitignored files staged anyway are a signal of `git add -A` mistakes.
- **Don't** require this skill on infra-only commits. Add a path filter or let the user opt out for those.
