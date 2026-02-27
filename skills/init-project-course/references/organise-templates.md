# Phase 3: Organise — Templates & Handling Rules

> Directory structure templates, workshop naming, and file handling rules for `/init-project-course` Phase 3.

---

## Student Template

For modules where the user is a student:

```
module-folder/
├── lectures/ or seminars/   # Lecture slides or seminar papers/readings
├── notes/                   # Personal notes, reading summaries
├── recordings/              # Lecture recordings (if any video files exist)
├── workshops/
│   ├── 01-topic-slug/
│   ├── 02-topic-slug/
│   └── ...
├── assessments/
│   ├── group-work/          # Only if group assessment exists
│   ├── individual/          # Only if individual assessment exists
│   └── exam/                # Only if exam exists
├── docs/                    # Module specification, guidelines, syllabi
├── reviews/                 # Created on demand by review agents
├── to-sort/                 # Inbox for unsorted files
├── .claude/
│   └── settings.local.json
├── CLAUDE.md
└── MEMORY.md                # Notation registry, code pitfalls (seeded)
```

**Use `seminars/` instead of `lectures/`** when the module is discussion-based (no traditional lectures — e.g., IB9PK-style with seminar papers and readings).

## Instructor Template

For modules where the user teaches:

```
module-folder/
├── lectures/ or classes/    # Lecture slides
├── recordings/              # Lecture recordings (if any video files exist)
├── workshops/ or labs/
│   ├── 01-topic-slug/
│   ├── 02-topic-slug/
│   └── ...
├── assessments/
│   ├── group-work/          # Only if group assessment exists
│   ├── individual/          # Only if individual assessment exists
│   └── exam/                # Only if exam exists
├── marking/                 # Marking scripts, rubrics, feedback templates
├── shared-folder/           # Student-facing materials (if applicable)
├── docs/                    # Module specification, guidelines
├── reviews/                 # Created on demand by review agents
├── to-sort/                 # Inbox for unsorted files
├── .claude/
│   └── settings.local.json
├── CLAUDE.md
└── MEMORY.md                # Student misconceptions, code pitfalls (seeded)
```

## Workshop Naming

- Format: `XX-topic-slug/` (zero-padded number + kebab-case topic)
- Infer topic from folder name if descriptive (e.g., "Workshop 1 - JavaScript Bootcamp" → `01-javascript-bootcamp`)
- For ambiguous names (e.g., "Workshop 6" with no description), try to identify the topic:
  - Read any PDF or `.docx` inside the folder
  - Check file names for clues
  - If still unclear, **ask the user** for that specific workshop
- Preserve numbering gaps — do NOT renumber (Week 11 stays `11-`, not `07-`)

## Lecture PDF Handling

- Collect ALL lecture PDFs into `lectures/` (or `seminars/`) from wherever they are scattered (root, workshop folders, assessment folders)
- **Deduplicate** — if the same filename appears in multiple locations, keep one copy in `lectures/` and remove the rest
- Do NOT rename lecture PDFs — keep original filenames
- Workshop-specific PDFs (exercise sheets, briefs) stay in their workshop folder

## Recording Handling

- Only create `recordings/` if video files are detected in the scan
- Move all lecture recordings to `recordings/`
- If recordings are already in a sensibly named folder, rename to `recordings/` rather than creating a new one

## Assessment Handling

- Only create subcategories under `assessments/` that the user confirmed exist
- Never guess assessment types — if unclear, ask

## Rules

- Present the full move plan as a list before executing
- Never move files without explicit approval
- If the existing structure is already clean, say so and only suggest minor fixes
