# Task Management Integration — Phase 8 Details

> Referenced from: `init-project-research/SKILL.md` Phase 8.

All paths relative to Task Management root (`cat ~/.config/task-mgmt/path`).

## 8a. Update `.context/projects/_index.md`

Add a new row to the "Papers in Progress" table. Stage is typically `Idea` or `Literature Review` at scaffold time.

Required columns: short name, title, theme, venue, stage, target deadline (or `—`), co-authors (initials), notes.

Use targeted `Edit` to insert the row in alphabetical order within the existing table — do NOT rewrite the file.

## 8b. Create `.context/projects/papers/<short-name>.md`

The "short name" is the kebab-case slug. Template: [`scaffold-details.md#papers-context-file-template`](scaffold-details.md#papers-context-file-template).

Populate from interview answers:

- `title:` — working title from Round 1 Q2
- `slug:` — Round 1 Q1
- `theme:` — Round 1 Q4
- `venue:` — Round 1 Q5
- `deadline:` — Round 1 Q6 (if any)
- `co_authors:` — Round 1 Q3
- `stage:` — `idea` (default after scaffold)
- `paper_type:` — Round 3 paper type
- `rqs:` — Round 3 research questions

## 8c. Update `.context/current-focus.md`

Add the new project either to the **Top 3 Active Projects** section (if the user indicated this is a primary focus) or to **Open Loops** (if it's a secondary or future thread).

Use targeted `Edit` to add the entry. Do NOT rewrite the file — `current-focus.md` has masthead retention rules and other entries that must be preserved.

Format for Top 3 entry:

```markdown
- **<Title>** (`<slug>`) — <one-line stage description>. Next: <next concrete action>.
```

Format for Open Loops entry:

```markdown
- `<slug>` — <2-5 word context tag>
```

## Verification

Before reporting Phase 8 complete, confirm:

1. `_index.md` has a new row for `<slug>`.
2. `papers/<short-name>.md` exists and parses (frontmatter + body).
3. `current-focus.md` has been edited (not rewritten) and the masthead `> Last updated:` line is unchanged from before this skill ran.

If any of these fails, surface it in the Phase 10 confirmation report so the user can manually fix.
