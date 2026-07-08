---
name: brief-compliance-check
description: "Use when you need to check a LaTeX submission against a PDF assessment brief."
allowed-tools:
  - Read
  - Glob
  - Bash(python3*)
  - Bash(ls*)
---

# Brief Compliance Check

> Given a PDF brief and a LaTeX submission, report exactly what is met, missing, or over-limit.
> **Report-only — never modifies files.**

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `brief-compliance-check`
- **Write reports to:** `reviews/<paper-slug>/brief-compliance-check/<YYYY-MM-DD-HHMM>.md` inside the project, where `<paper-slug>` is the paper directory name (e.g., `paper-jtp`, `paper-philtech`). Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `/review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- "Do we meet the requirements of the brief?"
- "Check my submission before I submit"
- Any coursework or report with per-task deliverables and word limits
- Argument: `[brief.pdf] [submission/]` or auto-detect from context

## Defaults

| Setting | Default |
|---------|---------|
| Brief path | Prompt if not found automatically |
| Submission dir | CWD or `submission/` subdirectory |
| LaTeX file | `main.tex` in submission dir |
| Word counting | Strips `lstlisting`, `tikzpicture`, `tabular`/`tabularx`, LaTeX commands |

## Protocol

### Step 1: Read the Brief

Read the full brief PDF. Extract for each task/section:
- **Deliverables** — what files or content must be present
- **Word limits** — any "maximum N words" constraints
- **Required files** — non-LaTeX files (YAML specs, workflow files, code, etc.)
- **Total marks** — note the rubric criteria for context

Present a one-paragraph summary: how many tasks, total marks, submission format.

### Step 2: Check Word Counts

For any task with a word limit, count words in the corresponding LaTeX section using this script:

```python
import re

with open('main.tex', 'r') as f:
    tex = f.read()

# Map section headings to task labels and limits
# (fill from brief before running)
sections = {
    'Task X': (r'\section{Heading}', r'\section{Next Heading}', limit),
}

for task, (start, end, limit) in sections.items():
    s = tex.find(start)
    e = tex.find(end) if end else len(tex)
    chunk = tex[s:e]
    # Strip non-prose environments
    chunk = re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', '', chunk, flags=re.DOTALL)
    chunk = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', chunk, flags=re.DOTALL)
    chunk = re.sub(r'\\begin\{tabular[x]?\}.*?\\end\{tabular[x]?\}', '', chunk, flags=re.DOTALL)
    # Strip LaTeX commands but keep their text arguments
    chunk = re.sub(r'\\[a-zA-Z]+\*?\{([^}]*)\}', r' \1 ', chunk)
    chunk = re.sub(r'\\[a-zA-Z]+\*?', ' ', chunk)
    chunk = re.sub(r'[{}\$~^%]', ' ', chunk)
    count = len(chunk.split())
    status = 'OK' if count <= limit else f'OVER by {count - limit}'
    print(f'{task}: ~{count} words (limit {limit}) [{status}]')
```

Adapt section headings and limits from the brief before running.

### Step 3: Check File Deliverables

For each required non-LaTeX file, verify existence:

```bash
ls submission/          # check submitted PDF and LaTeX
ls openapi/             # check YAML specs if required
ls .github/workflows/   # check CI workflow if required
ls services/*/          # check service implementations if required
```

Report each as ✅ present / ❌ missing.

### Step 4: Report

Produce a compliance table per task. Then summarise overall status.

## Output Format

```
## Brief Compliance Report — [Module/Assessment Name]

### Overview
[1-para summary: N tasks, N marks, submission format]

### Per-Task Compliance

| Task | Requirement | Status |
|------|-------------|--------|
| A    | Architecture diagram | ✅ |
| A    | Written explanation ≤600 words | ✅ ~540 words |
| B    | Security requirements ≤800 words | ✅ ~416 words |
| C    | Five OpenAPI YAML files | ✅ |
| C    | Linting output in PDF | ✅ |
| D    | Test logs | ✅ |
| D    | Written analysis ≤600 words | ❌ ~764 words (OVER by 164) |
| E    | GitHub Actions workflow file | ✅ |
| F    | Reflection ≤700 words | ✅ ~645 words |

### File Deliverables

| File/Directory | Required | Status |
|----------------|----------|--------|
| main.pdf | Yes | ✅ |
| openapi/*.yaml (5 files) | Yes | ✅ |
| .github/workflows/ci.yml | Yes | ✅ |
| services/*/Dockerfile (5) | Yes | ✅ |

### Summary

- ✅ N requirements met
- ❌ N gaps or violations
- ⚠️ N warnings (approaching limit, optional items)

[Action items for any ❌ or ⚠️]
```

## Never Do These

- Never modify the submission to fix issues — report only
- Never count words from `lstlisting`, `tikzpicture`, or table body content — these are not prose
- Never guess word limits — read them from the brief before counting
- Never report "approximately compliant" — every requirement is either met or not
- Never skip file existence checks — a missing deliverable is a hard gap

## Log to REVIEW-STATE.md (final step)

Write the brief-compliance report to `reviews/<paper-slug>/brief-compliance-check/<YYYY-MM-DD-HHMM>.md` (where `<paper-slug>` is extracted from the paper directory, e.g. `paper-jtp`; create `mkdir -p reviews/<paper-slug>/brief-compliance-check/` first). Then append a row to the project's `REVIEW-STATE.md`:

```bash
bash ~/.claude/skills/_shared/review-state-log.sh \
  --check brief-compliance-check \
  --paper "<paper-{venue} dir>" \
  --verdict "<PASS|PARTIAL|FAIL>" \
  --score "<met-count>/<total-criteria>" \
  --open-issues "<gap-count>/<total-criteria>" \
  --report "reviews/<paper-slug>/brief-compliance-check/<YYYY-MM-DD-HHMM>.md" \
  --notes "<one-line: e.g. 'over word limit by 250; missing appendix C'>" \
  [--trigger "pre-submission-report|review-cluster"]
```

- Verdict: PASS if every criterion met; PARTIAL if some met; FAIL if any hard gap (missing deliverable, over hard word limit).
- Score: criteria met / total criteria (e.g. `8/10`).
- Open issues: total gaps at run time / total criteria.
- Trigger: pass orchestrator name only if invoked as a sub-agent. Otherwise omit.

Schema: `~/Task-Management/docs/reference/review-state-schema.md`.
