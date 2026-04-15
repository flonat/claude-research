# LEARN Tag Routing — Annotation Injection Protocol

> Routes `[LEARN]` corrections from MEMORY.md to the specific skills that need them, so corrections are visible at point of use — not just sitting in a global file.

## Principle

**Corrections should appear where they're needed.** A `[LEARN:method]` tag about TWFE bias should appear when `/literature` or `/r-econometrics` is invoked — not buried in MEMORY.md hoping Claude recalls it. Annotation injection makes the existing correction system actually reach the right skills.

## How It Works

```
MEMORY.md → route-learn-tags.py → skills/.annotations/<skill>.json → skill invocation
                                                                         ↓
                                                              ## Known Corrections
                                                              (injected into prompt)
```

## Annotation Directory

```
skills/
├── .annotations/           # Auto-generated, gitignored
│   ├── literature.json
│   ├── r-econometrics.json
│   ├── computational-experiments.json
├── literature/
│   └── SKILL.md
├── ...
```

### Annotation File Format

```json
[
  {
    "tag": "[LEARN:method] TWFE is biased with staggered treatment — use CS or Sun-Abraham — applies when: staggered treatment adoption with heterogeneous effects",
    "category": "method",
    "routed_at": "2026-04-11",
    "source": "MEMORY.md",
    "keywords": ["TWFE", "staggered", "DiD", "CS", "Sun-Abraham"]
  },
  {
    "tag": "[LEARN:code] R: use <- for assignment, not = (the user's preference)",
    "category": "code",
    "routed_at": "2026-04-11",
    "source": "MEMORY.md",
    "keywords": ["R", "assignment", "<-"]
  }
]
```

## Routing Rules

### Category → Skill Mapping

| Category | Routes to |
|----------|-----------|
| `notation` | Skills referencing the same paper/project (match by project name in tag context) |
| `code` | Skills matching the language: R → `r-econometrics`, `data-analysis`; Python → `computational-experiments`, `figure` |
| `method` | `literature`, `r-econometrics`, `causal-design`, `computational-experiments` |
| `domain` | All skills in the same research domain (match by keyword) |

### Keyword Matching

Beyond category routing, match tag keywords against skill descriptions and `allowed-tools`:
- Tag mentions "DiD" or "event study" → route to skills with those terms
- Tag mentions "LaTeX" or "Beamer" → route to `latex`, `beamer-deck`
- Tag mentions a specific skill by name → route directly to it

### Multi-Routing

A single tag can route to multiple skills. Cap at 5 skills per tag to prevent noise.

## Injection at Invocation

When a skill is invoked, check for annotations:

1. Look for `skills/.annotations/<skill-name>.json`
2. If it exists and has entries, append to the skill context:

```markdown
## Known Corrections (auto-injected from MEMORY.md)

- TWFE is biased with staggered treatment — use CS or Sun-Abraham (applies when: staggered treatment adoption with heterogeneous effects)
- R: use <- for assignment, not = (the user's preference)
```

3. Cap at 10 most recent corrections per skill (FIFO — oldest drop off)
4. This injection is passive — skill authors don't need to do anything

## Routing Script

`scripts/route-learn-tags.py`:

```
Usage: uv run python scripts/route-learn-tags.py [--dry-run] [--from MEMORY.md]

Reads [LEARN:*] tags from MEMORY.md, routes each to relevant skills,
writes annotation JSON files to skills/.annotations/.

--dry-run: show routing decisions without writing files
--from:    path to MEMORY.md (default: project root)
```

### When to Run

- After adding a new `[LEARN]` tag to MEMORY.md
- As part of `/feedback-review` cycle
- Optionally: as a post-commit hook (if MEMORY.md changed)

## Integration with Feedback Pipeline

The `/rate` skill's structured labels (A2) feed into annotations too:

1. `/rate needs-work incomplete "missed X"` → recorded in `ratings.jsonl`
2. `/feedback-review` reads ratings → generates improvement proposals
3. Approved corrections become `[LEARN]` tags in MEMORY.md
4. `route-learn-tags.py` distributes them to relevant skills
5. Next invocation of the skill sees the correction

## Staleness

Annotations older than 90 days are auto-pruned by the routing script (re-run refreshes based on current MEMORY.md). If a `[LEARN]` tag is removed from MEMORY.md, its annotations are cleaned up on next routing run.

## When to Skip

- Skills that are rarely invoked (no point annotating dormant skills)
- Tags that are project-specific and the skill is general (use project MEMORY.md instead)
- During initial development of a new skill (annotations add noise to a skill still being designed)
