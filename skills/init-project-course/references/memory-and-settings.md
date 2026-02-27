# Phase 5-7: MEMORY.md Templates, Settings & Notion Sync

> Templates for seeding MEMORY.md, settings.local.json, and Notion pipeline sync for `/init-project-course`.

---

## MEMORY.md — Student Module Template

```markdown
# MEMORY — [Module Code] [Module Name]

## Notation Registry

| Variable | Convention | Anti-pattern |
|----------|-----------|--------------|

## Key Decisions

| Decision | Rationale | Date |
|----------|-----------|------|

## Code Pitfalls

| Bug | Impact | Fix |
|-----|--------|-----|
```

## MEMORY.md — Instructor Module Template

```markdown
# MEMORY — [Module Code] [Module Name]

## Student Misconceptions

| Misconception | Correction | How to address |
|---------------|-----------|----------------|

## Marking Notes

| Pattern | Frequency | Comment |
|---------|-----------|---------|

## Code Pitfalls

| Bug | Impact | Fix |
|-----|--------|-----|
```

---

## Settings — settings.local.json

If `.claude/settings.local.json` exists, leave it. If not, create one:

```json
{
  "permissions": {
    "allow": [
      "Bash(latexmk *)",
      "Bash(ls:*)",
      "Bash(mkdir:*)",
      "Bash(tree:*)",
      "Bash(npm *)",
      "Bash(node *)",
      "Edit",
      "Glob",
      "Grep",
      "Read",
      "Write"
    ],
    "deny": []
  }
}
```

---

## Notion Pipeline Sync

Offer to create a row in the appropriate Notion pipeline. If the user accepts:

### Student module → Modules Pipeline (Student)

- **Database data source ID:** `YOUR-MODULES-STUDENT-DATABASE-ID-HERE`
- Set: Module Name, Module Code, University, Programme, Term, Year, Status, Assessment Type, Credits, Instructor, Folder Path, Has CLAUDE.md = `__YES__`

### Instructor module → Modules Pipeline (Instructor)

- **Database data source ID:** `YOUR-MODULES-INSTRUCTOR-DATABASE-ID-HERE`
- Set: Module Name, Module Code, University, Term, Year, Role, Status, Module Leader, Folder Path, Has CLAUDE.md = `__YES__`

Use information gathered from the interview. Leave unknown fields empty rather than guessing.
