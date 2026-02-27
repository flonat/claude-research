---
name: consolidate-memory
description: "Consolidate MEMORY.md files: prune duplicates, merge overlapping entries, generate abstractions, and remove stale knowledge. Inspired by npcsh sleep/dream cycles."
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
argument-hint: "[project-path or 'all' for global consolidation]"
---

# Consolidate Memory

Periodic refinement of `MEMORY.md` files across projects. Prunes redundant entries, merges overlapping knowledge, generates higher-order abstractions from accumulated patterns, and removes stale or superseded entries.

Inspired by npcsh's knowledge graph sleep/dream cycles — memory consolidation applied to research project knowledge.

## When to Use

- Monthly maintenance (pair with `/system-audit`)
- When a `MEMORY.md` exceeds 100 entries
- After completing a major project milestone (e.g., paper submission)
- When starting a new session and `MEMORY.md` feels cluttered
- When the same correction keeps appearing across multiple projects

## When NOT to Use

- During active work sessions — consolidation is a maintenance task
- When `MEMORY.md` has fewer than 10 entries — not enough to consolidate
- Immediately after recording `[LEARN]` tags — let knowledge accumulate first

## Modes

Ask the user which mode to run:

| Mode | Scope | What it does |
|------|-------|-------------|
| **Project** (default) | Single project's `MEMORY.md` | Consolidate one file |
| **Global** | All `MEMORY.md` files across projects + Task Management | Consolidate all, cross-pollinate shared patterns |

## Workflow

### Phase 1: Sleep (Consolidation)

Read the target `MEMORY.md` file(s) and perform:

#### 1.1 Duplicate Detection

Find entries that say the same thing in different words.

**Signals:**
- Same correction direction (wrong → right) with different phrasing
- Same file/variable referenced in multiple entries
- Entries from different dates that record the same learning

**Action:** Merge into a single entry, keeping the most precise wording. Note the merge in a comment: `<!-- merged from 2 entries -->`.

#### 1.2 Contradiction Resolution

Find entries that contradict each other (e.g., "use X" in one entry, "don't use X" in another).

**Signals:**
- Opposite correction directions for the same variable/convention
- Entries where a later one supersedes an earlier one

**Action:** Keep the most recent/correct entry. Flag contradictions for user review if the resolution isn't obvious.

#### 1.3 Staleness Detection

Find entries that are no longer relevant.

**Signals:**
- References to files, variables, or conventions that no longer exist in the project
- Entries about bugs that have been fixed
- Entries about tools or APIs that have changed
- Entries marked with dates older than 6 months with no recent reinforcement

**Action:** Mark as `[STALE?]` and present to user for confirmation before removing. Never auto-delete.

#### 1.4 Strengthening

Entries that have been independently confirmed multiple times are high-confidence knowledge.

**Signals:**
- Same pattern recorded from different sessions
- Corrections reinforced by compilation errors or test failures
- Conventions confirmed by supervisor feedback

**Action:** Move to the top of their section. Add `[CONFIRMED]` marker if supported by 3+ independent occurrences.

### Phase 2: Dream (Abstraction)

Generate higher-order patterns from the accumulated entries.

#### 2.1 Cross-Entry Patterns

Look for patterns that span multiple entries:

- "Every time we work with X, we hit Y" → Record as a general rule
- "We always use convention A for project type B" → Record as a convention
- "Corrections in category C cluster around the same mistake" → Record the root cause

#### 2.2 Cross-Project Patterns (Global mode only)

When consolidating across all projects, look for knowledge that applies everywhere:

- Notation conventions used consistently across 3+ projects → Promote to global MEMORY.md
- The same code pitfall appearing in multiple projects → Record once with cross-references
- Citation corrections that apply to shared bibliography entries → Consolidate

#### 2.3 Abstraction Generation

For each pattern found, generate an abstraction:

```markdown
## Abstraction: [Name]

**Pattern:** [What keeps happening]
**Root cause:** [Why it happens]
**Prevention:** [How to avoid it in future]
**Evidence:** [Which entries support this]
```

Present abstractions to the user. Only write the ones they approve.

### Phase 3: Write

#### 3.1 Restructure

Rewrite `MEMORY.md` with:
1. **Abstractions** at the top (new section: `## Patterns`)
2. **Confirmed entries** next (high-confidence knowledge)
3. **Regular entries** in their standard sections (Notation Registry, Citations, Key Decisions, Anti-Patterns, Code Pitfalls)
4. **Stale entries removed** (only those confirmed by user)

#### 3.2 Diff Report

Before writing, show a summary:

```markdown
## Consolidation Summary

| Action | Count |
|--------|-------|
| Duplicates merged | X |
| Contradictions resolved | X |
| Stale entries flagged | X |
| Stale entries removed | X (user-confirmed) |
| Entries strengthened | X |
| Abstractions generated | X |
| Cross-project promotions | X (global mode) |

### Entries Before: XX
### Entries After: YY
### Net reduction: ZZ
```

#### 3.3 Confirmation

**Always show the full proposed MEMORY.md before writing.** Wait for explicit approval. The user may want to keep entries flagged as stale, adjust abstractions, or revert merges.

## MEMORY.md Sections (Reference)

Standard sections from the `learn-tags` rule:

| Section | Columns |
|---------|---------|
| **Patterns** | Pattern / Root cause / Prevention / Evidence (NEW — added by this skill) |
| **Notation Registry** | Variable / Convention / Anti-pattern |
| **Estimand Registry** | What we estimate / Identification / Key assumptions |
| **Citations** | One-liner corrections |
| **Key Decisions** | Decision / Rationale / Date |
| **Anti-Patterns** | What went wrong / Correction |
| **Code Pitfalls** | Bug / Impact / Fix |

## Global MEMORY.md Location

The Task Management MEMORY.md at the project root:
```
MEMORY.md
```

Also check the auto-memory directory:
```
~/.claude/projects/-Users-user-Library-CloudStorage-YOUR-CLOUD-Task-Management/memory/MEMORY.md
```

## Cross-References

- **`/system-audit`** — Run consolidation as part of periodic maintenance
- **`/learn`** — Creates the entries that this skill consolidates
- **`[LEARN]` tags** (rule) — The tagging system that feeds MEMORY.md
- **`/session-recap`** — May surface entries worth recording before consolidation
