# Progressive Disclosure for Skills

> Pattern for structuring large skills so that Claude reads only the sections it needs, rather than loading everything into context upfront.

## The Problem

When a skill is invoked, its full `SKILL.md` is loaded into context. For large skills (200+ lines), most of the content may be irrelevant to the specific task. This wastes tokens and can push sessions toward compression earlier than necessary.

## The Pattern

Split a skill into a **lean core** (the main `SKILL.md`) and **on-demand sections** (files in `references/`). The core contains workflow logic, decision points, and a section index. Reference files contain detailed instructions that Claude reads only when the workflow reaches that branch.

### Structure

```
skills/my-skill/
  SKILL.md              # Lean core: workflow + section index (< 100 lines ideal)
  references/
    phase-1-details.md  # Detailed instructions for phase 1
    phase-2-details.md  # Detailed instructions for phase 2
    edge-cases.md       # Handling for uncommon scenarios
    report-template.md  # Output format template
```

### Section Index in SKILL.md

Include a section index that tells Claude what exists and when to read it:

```markdown
## Reference Sections

Read these **only when needed** — do not pre-load all of them.

| Section | When to read | File |
|---------|-------------|------|
| Phase 1 details | When starting Phase 1 | [`references/phase-1-details.md`](references/phase-1-details.md) |
| Phase 2 details | When starting Phase 2 | [`references/phase-2-details.md`](references/phase-2-details.md) |
| Edge cases | When encountering an unusual input | [`references/edge-cases.md`](references/edge-cases.md) |
| Report template | When writing the output report | [`references/report-template.md`](references/report-template.md) |
```

### What Goes in the Core vs. References

**Keep in SKILL.md (always loaded):**
- YAML frontmatter (name, description, allowed-tools)
- When to use / when not to use
- High-level workflow (numbered phases)
- Decision logic (if X then do Y)
- Section index table
- Cross-references to other skills

**Move to references/ (loaded on demand):**
- Detailed instructions for individual phases (> 15 lines)
- Report/output templates
- Lookup tables, checklists, scoring rubrics
- Domain-specific knowledge (e.g., journal formatting rules)
- Edge case handling
- Examples and sample outputs

### Threshold Rule

Apply progressive disclosure when a skill meets **any** of:
- Total `SKILL.md` exceeds 200 lines
- Any single section exceeds 40 lines of reference material (not workflow logic)
- The skill has 3+ distinct phases where only 1-2 run in a typical invocation
- The skill serves multiple domains with domain-specific branches

### Skills Already Using This Pattern

These skills already follow progressive disclosure:
- `/validate-bib` — preprint check logic in `references/preprint-check.md`, report template in `references/report-template.md`
- `/code-review` — quality rubric in `references/quality-rubric.md`
- `/devils-advocate` — competing hypotheses framework in `references/competing-hypotheses.md`

### When NOT to Apply

- Skills under 100 lines — overhead isn't worth it
- Skills where every section is always needed (e.g., `/session-log`)
- Skills where the workflow is linear and every step always runs

## For Existing Skills

When refactoring an existing skill to use progressive disclosure:
1. Identify sections that are > 40 lines of reference material
2. Extract to `references/` with a descriptive filename
3. Replace in `SKILL.md` with a one-line summary + link
4. Add a section index table if one doesn't exist
5. Test by invoking the skill — verify Claude reads the right sections at the right time
