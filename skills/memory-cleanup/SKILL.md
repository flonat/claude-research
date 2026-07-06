---
name: memory-cleanup
description: "Use when you need to prune duplicates and merge overlapping entries in MEMORY.md files."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
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
| **Project** (default) | Single project's `MEMORY.md` + `.claude/state/personal-memory.md` | Consolidate both tiers |
| **Global** | All `MEMORY.md` + personal-memory files across projects + Task Management | Consolidate all, cross-pollinate shared patterns |

## Workflow

### Phase 1: Sleep (Consolidation)

Read the target `MEMORY.md` file(s) and `.claude/state/personal-memory.md` (if it exists) and perform:

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

#### 1.4 Tier Routing Check

Check whether entries are in the correct tier (see `learn-tags` rule for the two-tier system).

**Promotion candidates** (personal-memory → MEMORY.md):
- Entries in `.claude/state/personal-memory.md` that would help a collaborator on a different machine
- Local workarounds that turned out to be general conventions
- Tool quirks that apply to all machines (not just this one)

**Demotion candidates** (MEMORY.md → personal-memory):
- Entries in `MEMORY.md` that reference local paths, machine-specific tool versions, or environment quirks
- Workarounds that only apply to this specific setup

**Action:** Present promotion/demotion suggestions to the user. Move entries only after explicit approval.

#### 1.5 Strengthening

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

If `.claude/state/personal-memory.md` exists, also rewrite it with consolidated machine-specific entries. Apply any user-approved promotions (move to MEMORY.md) and demotions (move from MEMORY.md to personal-memory).

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
| Tier promotions (personal → generic) | X |
| Tier demotions (generic → personal) | X |
| Cross-project promotions | X (global mode) |

### Entries Before: XX
### Entries After: YY
### Net reduction: ZZ
```

#### 3.3 Confirmation

**Always show the full proposed MEMORY.md before writing.** Wait for explicit approval. The user may want to keep entries flagged as stale, adjust abstractions, or revert merges.

### Phase 4: Propagate to Shared Auto-Memory

**Why:** `scripts/sync-push-memory.sh` append-merges `MEMORY.md`. Deletions propagate via **tombstones**: each shared dir carries a git-tracked `.tombstones` file (one filename per line, `#` comments allowed) that both sync scripts honour since 2026-07-03 — tombstoned entries are removed from both sides on every sync, so other machines self-clean instead of resurrecting deleted entries. This phase mirrors the cleanup to shared AND writes the tombstones.

**When to run:** Whenever this skill deletes files or shortens `MEMORY.md` (not needed for pure additions). If only adding entries, the normal append-merge sync handles it.

**What to do:**

1. Identify the shared copy location(s) that correspond to the local scope:
   - Task Management auto-memory (`~/.claude/projects/-Users-user-*Task-Management/memory/`) → `$TM/.context/auto-memory/task-management/`
   - Global auto-memory (`~/.claude/projects/*/memory/` for non-TM projects) → `$TM/.context/auto-memory/global/`

2. Mirror local → shared for each location:
   - **MEMORY.md and MEMORY-ARCHIVE.md:** force-copy from local to shared (overwrites, bypasses append-merge)
   - **Deletions:** delete from shared **only the entries this cleanup explicitly removed** (the user-confirmed removal set from Phase 3). Track those filenames as you go, and **append each to `$shared_dir/.tombstones`** with a dated `#` comment — this is what makes the deletion stick on other machines.
   - **Reconcile UP:** any entry present in shared but NOT in local, NOT in the removal set, **and NOT listed in `.tombstones`** (a tombstoned name is a confirmed prior deletion, not a missing entry — re-delete it, don't pull it), is a legit entry this machine never pulled (shared aggregates across machines/sessions). **Pull it into local + flag it for indexing — never delete it.**
   - **Mirror entry files:** copy any local entry file that's newer/missing into shared.

> ⚠️ **Do NOT infer deletion from a local/shared set difference.** The naive
> `[ ! -f local/$name ] && rm shared/$name` is a data-loss bug: shared is a
> *union* across machines, so a shared-only file is usually a real entry local
> is missing, not something to delete. Real incident 2026-05-31: that loop
> silently deleted a legit `reference_hermes_vps.md` (created in another
> session) before it was caught in git. Delete only what Phase 3 explicitly removed.

3. Commit the shared-copy changes to the Task Management repo with a message explaining it's a cleanup propagation (so the log is clear about why entries vanished).

**Example (Task Management scope):**

```bash
local_dir=~/.claude/projects/-Users-user-Task-Management/memory
shared_dir="$TM/.context/auto-memory/task-management"

# REMOVED = the entry files THIS cleanup deleted (user-confirmed in Phase 3).
# ONLY these may be deleted from shared. Edit per run.
REMOVED=(feedback_notion_rest_api.md feedback_dropbox_path_change.md)   # example

# Force-copy the indices (overwrite, bypasses append-merge)
cp "$local_dir/MEMORY.md" "$shared_dir/MEMORY.md"
[ -f "$local_dir/MEMORY-ARCHIVE.md" ] && cp "$local_dir/MEMORY-ARCHIVE.md" "$shared_dir/MEMORY-ARCHIVE.md"

# 1. Delete from shared ONLY the explicitly-removed entries + tombstone them
#    (the tombstone makes the deletion propagate: both sync scripts remove
#    tombstoned files from local AND shared on every push/pull)
for name in "${REMOVED[@]}"; do
  rm -f "$shared_dir/$name"
  echo "$name  # removed $(date +%Y-%m-%d) by /memory-cleanup" >> "$shared_dir/.tombstones"
done

# 2. Reconcile UP: a shared-only entry (not in REMOVED, not tombstoned) is a
#    legit entry this machine is missing — pull it into local + flag it,
#    never delete. A TOMBSTONED shared-only entry is a zombie: re-delete it.
for f in "$shared_dir"/*.md; do
  name=$(basename "$f")
  case "$name" in MEMORY.md|MEMORY-ARCHIVE.md) continue;; esac
  if [ -f "$shared_dir/.tombstones" ] && grep -q "^$name" "$shared_dir/.tombstones"; then
    rm -f "$f"; echo "re-deleted tombstoned zombie: $name"; continue
  fi
  if [ ! -f "$local_dir/$name" ]; then
    cp "$f" "$local_dir/$name"
    echo "PULLED shared-only entry into local — verify + add to MEMORY.md index: $name"
  fi
done

# 3. Mirror local → shared (copy locally-newer/missing entry files)
for f in "$local_dir"/*.md; do
  name=$(basename "$f")
  case "$name" in MEMORY.md|MEMORY-ARCHIVE.md) continue;; esac
  if [ ! -f "$shared_dir/$name" ] || [ "$f" -nt "$shared_dir/$name" ]; then
    cp "$f" "$shared_dir/$name"
  fi
done

# After pulling any shared-only entries, add their index lines to local
# MEMORY.md, then re-copy local MEMORY.md → shared so both indices match.

# Commit
cd "$TM" && git add .context/auto-memory/task-management/ && git commit -m "memory: propagate cleanup to shared auto-memory"
```

**Skip Phase 4 if:** the consolidation only added entries (no deletions, no line removals from MEMORY.md). Append-merge handles additions correctly on its own.

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
$TM/MEMORY.md
```

Also check the auto-memory directory (path varies by machine — glob for it):
```
~/.claude/projects/-Users-user-*Task-Management/memory/MEMORY.md
```

## Cross-References

- **`/system-audit`** — Run consolidation as part of periodic maintenance
- **`/skill-extract`** — Creates the entries that this skill consolidates
- **`[LEARN]` tags** (rule) — The tagging system that feeds MEMORY.md
- **`/session-close`** — May surface entries worth recording before consolidation
