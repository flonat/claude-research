# External Audit Protocol

> Shared workflow for all `external-*-audit` skills. Each skill references this file and provides scope-specific configuration (CWD, checklist, report path).

## What This Is

Uses an external LLM CLI (Codex or Gemini) to get a **fresh, independent perspective** from a competing model on Claude Code infrastructure. This extends the agents-vs-skills principle: not just fresh Claude context, but an entirely different model reviewing the work.

**Key difference from `/system-audit`:** System audit uses Claude sub-agents for mechanical checks (counts, symlinks, broken links). External audits are **qualitative** — architecture coherence, design quality, redundancy, missing capabilities, improvement suggestions.

**Model selection:** Pass `--model codex` or `--model gemini` (default: gemini). Running both triangulates — different training and reasoning patterns produce more reliable findings than either alone.

## Model Commands

| Model | CLI | Execute command | Install |
|-------|-----|----------------|---------|
| Codex | `codex` | `codex exec --full-auto "{prompt}"` | `npm install -g @openai/codex` + `codex login` |
| Gemini | `gemini` | `gemini -p "{prompt}" --yolo` | `npm install -g @google/gemini-cli` |

## Pre-Flight

Before anything else:

1. **Verify the CLI is installed:**
   ```bash
   which {model} && {model} --version
   ```
   If not found, stop and tell the user with install instructions (see table above).

2. **Confirm the target directory exists** (CWD from the skill config).

3. **Check git status** in the target directory to establish a clean baseline:
   ```bash
   cd <CWD> && git status --short
   ```
   Note any pre-existing uncommitted changes so we can distinguish them from model modifications later.

## Phase 1: Generate Manifest

Claude generates a concise ecosystem manifest describing what the model will be auditing. This gives it the map before it explores the territory.

Write to `/tmp/external-audit-manifest-{scope}.md`:

```markdown
# Ecosystem Manifest: {scope}

## Root Directory
{absolute path}

## Key Paths
{list of important directories and files, relative to root}

## Counts
{relevant metrics: number of skills, hooks, files, etc.}

## Architecture Summary
{2-3 sentence description of how the system is organized}

## Tech Stack
{languages, frameworks, key dependencies}
```

**Keep it under 200 lines.** The model needs context, not a full directory listing.

## Phase 2: Build Prompt

Combine the manifest with the skill-specific audit checklist into a single prompt file.

Write to `/tmp/external-audit-prompt-{scope}.md`:

```markdown
# External Audit: {scope}

## CRITICAL INSTRUCTIONS

You are conducting a **READ-ONLY architecture audit**. You must:
- **NEVER create, modify, or delete any files** — not even "cleanup" or "improvement" edits
- **NEVER run git commands that change state** (no commit, add, push, checkout, rm)
- **NEVER install packages or modify dependencies**
- **NEVER append to, rename, or reorganize existing files**
- Only read files and output your findings as markdown to stdout
- If you feel compelled to fix something, describe the fix in your output instead — do NOT apply it

## Ecosystem Manifest

{contents of manifest file}

## Audit Checklist

{contents of skill-specific references/audit-checklist.md}

## Output Format

Structure your response as a markdown report with these sections:

### Executive Summary
2-3 sentence overall assessment.

### Scored Sections
For each checklist category, provide:
- **Score:** A/B/C/D/F
- **Strengths:** What's done well
- **Issues:** Problems found (severity: Critical/Major/Minor)
- **Recommendations:** Specific, actionable improvements

### Architecture Diagram
If helpful, describe the system architecture in text form.

### Top 5 Recommendations
Prioritized list of the most impactful improvements, with effort estimates (Quick/Medium/Large).

### Fresh Eyes
Things that seem odd, redundant, or unnecessarily complex to someone seeing this for the first time. This is the most valuable section — it's what insiders miss.
```

## Phase 3: Execute

Run from the target CWD with a 10-minute timeout:

**Codex:**
```bash
cd <CWD> && timeout 600 codex exec --full-auto "$(cat /tmp/external-audit-prompt-{scope}.md)" 2>&1
```

**Gemini:**
```bash
cd <CWD> && timeout 600 gemini -p "$(cat /tmp/external-audit-prompt-{scope}.md)" --yolo 2>&1
```

**Capture the full output** — both stdout and stderr.

**If the model fails or times out:**
- Log the error
- Report to the user: "{Model} execution failed: {error}. The prompt is saved at `/tmp/external-audit-prompt-{scope}.md` if you want to retry manually."
- Do not retry automatically

## Phase 4: Safety Check

> **Critical warning:** Both Codex and Gemini are agentic coding tools designed to make changes. Despite read-only instructions, they may create, modify, or delete files. Gemini has a documented tendency to do this. **Always assume the model touched something** and verify thoroughly. This check is not optional.

**Immediately after the model returns**, verify nothing was modified:

```bash
cd <CWD> && git diff --stat
cd <CWD> && git status --short
```

Run **both** commands — `git diff` catches modifications to tracked files, `git status` catches new untracked files or deletions. Compare against the baseline from pre-flight.

If there are **new changes not present before**:

1. **Alert the user immediately:** "{Model} modified files despite read-only instructions. Changed: {list}"
2. **Revert immediately:** `git checkout -- .` (for modifications/deletions). For new untracked files, list them and delete manually.
3. **Do not proceed** with report generation until the working tree matches the pre-flight baseline
4. **Note the violation** in the report header (replace "No files modified" with a description of what was changed and reverted)

## Phase 5: Write Report

Write the model output to the skill-specified report path (typically `audits/{model}-audit-{scope}-YYYY-MM-DD.md`).

Add a header:

```markdown
# {Model} Audit: {Scope Title} — YYYY-MM-DD

> Generated by {Model CLI description}.
> Read-only audit | No files modified.

---

{Model output}
```

## Phase 6: Present

Show the user:

1. **Executive summary** from the report
2. **Any Critical/Major issues** found
3. **Top 5 recommendations** with effort estimates
4. **Fresh Eyes section** — the outsider perspective
5. Link to the full report

Ask if he wants to address any findings now.

## Error Handling

| Situation | Action |
|-----------|--------|
| CLI not installed | Stop, show install instructions |
| Target directory doesn't exist | Stop, ask the user for correct path |
| Model times out (>10 min) | Save partial output if any, report failure |
| Model modifies files | Alert, offer revert, do not continue |
| Model returns empty output | Report failure, save prompt for manual retry |
| Git not initialized in target | Skip git safety checks, warn the user |
| Authentication error | Stop, tell the user to authenticate |

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `/system-audit` | Mechanical checks (counts, symlinks) — complementary, not overlapping |
| `/audit-project-research` | Per-project structural audit — external audits are cross-cutting |
| `/lessons-learned` | Critical findings can feed into post-mortems |
| `/ideas` | Recommendations can be captured as improvement ideas |
