# Pedro Sant'Anna — Claude Code Workflow Takeaways

> Source: `resources/pedro-santanna/claude-code-my-workflow`
> Context: Production workflow used for 6 PhD lecture decks (800+ slides), Econ 730 at Emory
> Saved: February 2026

## What It Is

A modular, opinionated system for using Claude Code to develop academic lecture materials (Beamer + Quarto). Everything is parameterised so other academics can fork it.

## Architecture

```
CLAUDE.md                  — Project memory (~150 lines, links to detailed rules)
.claude/agents/ (10)       — Specialized reviewers (proofreader, slide-auditor, pedagogy, R, TikZ, etc.)
.claude/skills/ (13)       — Slash commands (/compile-latex, /translate-to-quarto, /qa-quarto, etc.)
.claude/rules/ (12)        — Auto-loaded enforcement protocols
quality_reports/            — Plans and session logs (survive context compression)
```

## Key Design Patterns Worth Adopting

### 1. Specialist Agents > Generalist Prompts
- 10 narrow agents instead of one "review everything" prompt
- Each agent has a well-defined domain and output format
- Agents report findings but **never apply changes directly** — human approves first
- Run independent agents in parallel for speed

### 2. Plan-First Workflow (Mandatory for Non-Trivial Tasks)
- Enter plan mode → draft approach → save plan to disk → get approval → execute
- Plans saved as `quality_reports/plans/YYYY-MM-DD_description.md` so they survive context compression
- **Critical rule:** Never use `/clear` — rely on auto-compression instead

### 3. Orchestrator (Contractor Mode)
After plan approval, autonomous loop:
**Implement → Verify → Review → Fix → Score → Loop** (max 5 rounds)
- Fix priority: Critical > Major > Minor
- Agent selection based on file types modified
- Present summary when done

### 4. Quality Gates with Numeric Scoring
- **80** = commit threshold (blocks if below)
- **90** = PR threshold (warning)
- **95** = excellence target
- Objective rubric with specific deductions (e.g., compilation failure = -100, broken citation = -15)
- Prevents infinite iteration — you know when it's "done enough"

### 5. Adversarial Critic-Fixer Loop
- Critic agent reads output and produces harsh findings
- Fixer agent implements exactly what critic found
- Loop up to 5 rounds until critic says "APPROVED"
- Catches subtle issues that single-pass review misses

### 6. Single Source of Truth
- One file is authoritative (e.g., Beamer `.tex`)
- Everything else (Quarto, SVGs, figures) is derived
- When you modify the source, regenerate all derived versions automatically

### 7. [LEARN] Tags for Continuous Learning
Format: `[LEARN:tag] Incorrect → Correct`
- Persists in MEMORY.md across sessions
- Prevents repeating mistakes across large projects
- Captures corrections immediately, not at end of session

### 8. Three-Part Session Logging
1. **Post-plan** — Goal, plan summary, rationale (written right after plan approval)
2. **Incremental** — Written immediately when significant events happen (not batched)
3. **End-of-session** — Summary, open questions, unresolved issues

### 9. Stop Hook for Verification
- `settings.json` includes a hook that runs on conversation end
- Checks: did Claude verify compilation/rendering before stopping?
- Prevents shipping broken outputs

### 10. Knowledge Base Template
- Notation registry (prevents inconsistency across lectures)
- Course narrative arc (ensures pedagogical coherence)
- Anti-patterns list (what NOT to do)
- Updated continuously as field conventions are learned

## Philosophy

- Claude as **collaborative partner**, not fully autonomous agent
- Human drives vision and approves; Claude implements, reviews, iterates
- Verification is **non-negotiable** — enforced by hooks
- Decision rationale preserved in session logs (git shows *what*, logs show *why*)
- Orchestrator frees cognitive load for creative work

## What's Adaptable to My Workflow

- **Specialist agents** pattern → could create focused reviewers for my research (methods, writing, code)
- **Quality gates** → numeric scoring for paper drafts before submission
- **[LEARN] tags** → already using MEMORY.md, could formalise correction tracking
- **Critic-fixer loop** → useful for devil's advocate on papers (similar to my `/devils-advocate` skill)
- **Plan-first + save to disk** → plans surviving context compression is smart
- **Stop hooks** → enforce verification before ending sessions
