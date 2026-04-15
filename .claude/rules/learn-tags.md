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

Machine-specific examples:
- `[LEARN:code] On this Mac, latexmk needs /Library/TeX path explicitly`
- `[LEARN:code] uv 0.5.x on ARM has slow lock resolution — use --frozen`
- `[LEARN:code] Zotero DB at ~/.local/share/user-papers/ not default path`

If `.claude/state/personal-memory.md` does not exist, create it on first machine-specific entry (see `init-project-research` templates for the seed format). Create the directory too: `mkdir -p .claude/state`.

## Examples

```
[LEARN:notation] In this paper, treatment is $D_i$ not $T_i$
[LEARN:citation] Sant'Anna & Zhao (2020) key is santanna2020doubly not santanna2020
[LEARN:code] R: use <- for assignment, not = (the user's preference)
[LEARN:method] TWFE is biased with staggered treatment — use CS or Sun-Abraham
[LEARN:domain] UK universities use "marks" not "grades" for assessment scores
```

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

When recording a `[LEARN]` tag, also add the correction to the appropriate table:
- `[LEARN:notation]` → Notation Registry
- `[LEARN:code]` → Code Pitfalls
- `[LEARN:method]` or `[LEARN:domain]` → Anti-Patterns or Key Decisions
- `[LEARN:citation]` → Citations section (one-liners)

## Important

- Keep entries concise — one line per learning
- Include the correction direction (wrong → right)
- These accumulate over time and inform future sessions
