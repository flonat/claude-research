# Rule: Record Learnings with [LEARN] Tags

## Format

```
[LEARN:category] Incorrect → Correct — applies when: {context}
```

The `— applies when:` suffix is **required** for `code`, `method`, and `domain` categories (where context determines applicability). It is **optional** for `notation` and `citation` (which are typically universal).

Examples with context:
```
[LEARN:code] Growing a list in a loop → Pre-allocate or use list comprehension — applies when: Python loops over >1000 items
[LEARN:method] TWFE → CS or Sun-Abraham — applies when: staggered treatment adoption with heterogeneous effects
[LEARN:domain] "grades" → "marks" — applies when: UK university context
```

## Categories

| Category | What to record |
|----------|---------------|
| `notation` | Math/LaTeX notation conventions (e.g., `$x_i$` vs `$x_{i}$`) |
| `citation` | Bibliography and citation issues (wrong keys, format) |
| `code` | Programming patterns, bugs, language-specific gotchas |
| `method` | Econometric/statistical method corrections |
| `domain` | Domain knowledge corrections (institutional details, definitions) |

## When to Record

- **Immediately** when a correction is discovered — do not batch
- When the user corrects something during a session
- When a compilation error reveals a recurring mistake
- When a reviewer/supervisor flags an issue

## Dedup Check (before writing)

Before appending a new entry to MEMORY.md, **grep the file for the key terms** in your learning (variable name, function name, concept). If an existing entry covers the same topic:

- **Same correction:** Skip — it's already recorded.
- **Updated correction:** Replace the old entry with the new one (don't append a duplicate).
- **Contradictory:** Replace the old entry, add `[SUPERSEDED YYYY-MM-DD]` note explaining what changed.

This prevents MEMORY.md from growing with redundant or contradictory entries.

## Where to Write

Append to `MEMORY.md` in the project root, under the matching category section.

If `MEMORY.md` does not exist, create it using the Knowledge Base template below. To choose the right variant: check the project's `CLAUDE.md` for keywords like "course", "workshop", or "teaching" → use the **teaching** template. Otherwise → use the **research** template (default).

## Tier Routing

Learnings are routed to one of two files based on portability:

| Tier | File | Committed? | Examples |
|------|------|-----------|----------|
| Generic | `MEMORY.md` (project root) | Yes | Notation conventions, method corrections, citation fixes, design decisions |
| Machine-specific | `.claude/state/personal-memory.md` | No (gitignored) | Local path workarounds, tool version quirks, machine-specific build flags |

**Decision rule:** "Would this help a collaborator on a different machine?" Yes → Generic. No → Machine-specific. **Default: Generic** (~95% of entries).

Machine-specific examples: local paths (latexmk on `/Library/TeX`), tool version quirks (`uv 0.5.x` slow on ARM), non-default DB paths (Zotero at `~/.local/share/user-papers/`).

If `.claude/state/personal-memory.md` does not exist, create it on first machine-specific entry: `mkdir -p .claude/state` and seed from `init-project-research` templates.

## Knowledge Base in MEMORY.md

Beyond one-liner `[LEARN]` tags, MEMORY.md should build structured knowledge tables. These are faster to scan than narrative and immediately actionable in new sessions.

### Research Project Template

When `MEMORY.md` is created for a research project, seed it with these sections:

| Section | Columns | When to populate |
|---------|---------|-----------------|
| **Notation Registry** | Variable / Convention / Anti-pattern | When notation is first established or corrected |
| **Estimand Registry** | What we estimate / Identification / Key assumptions | When research design is discussed |
| **Key Decisions** | Decision / Rationale / Date | When a methodological choice is made |
| **Citations** | One-liner corrections | On `[LEARN:citation]` |
| **Anti-Patterns** | What went wrong / Correction | On `[LEARN:method]` or `[LEARN:domain]` |
| **Code Pitfalls** | Bug / Impact / Fix | On `[LEARN:code]` |

### Teaching Project Template

For teaching or workshop projects, use these sections instead:

| Section | Columns |
|---------|---------|
| **Lecture Progression** | Topic / Core question / Key method |
| **Student Misconceptions** | Misconception / Correction / How to address |
| **Empirical Applications** | Paper / Dataset / Purpose |

### How [LEARN] Tags Feed In

Each tag also lands in its corresponding table: notation → Notation Registry; code → Code Pitfalls; method/domain → Anti-Patterns or Key Decisions; citation → Citations.

## Important

One line per learning, wrong → right direction explicit. Entries accumulate and inform future sessions.
