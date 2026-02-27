---
name: learn
description: "Extract reusable knowledge from the current session into a persistent skill.\nUse when you discover something non-obvious, create a workaround, or develop\na multi-step workflow that future sessions would benefit from."
allowed_tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(uv run python*)
  - AskUserQuestion
---

# Learn: Session Knowledge Extraction

Extract reusable workflows, workarounds, and multi-step procedures discovered during a session into persistent skills. Complementary to the `learn-tags` rule — while `[LEARN]` tags record one-liner corrections in MEMORY.md, `/learn` creates full skill definitions in `skills/`.

## When to Use

- You discovered a non-obvious multi-step procedure
- You built a workaround for a recurring problem
- You developed a workflow that future sessions would benefit from
- the user says "save this as a skill", "learn this", or "remember how to do this"

## Phase 1: Evaluate

Before creating anything, answer these 4 self-assessment questions:

1. **Non-obvious?** Would a future session figure this out without help, or would it waste time rediscovering it?
2. **Future benefit?** Will this come up again across sessions or projects?
3. **Repeatable?** Is this a procedure that can be followed step-by-step, or was it a one-off?
4. **Multi-step?** Does it involve 2+ non-trivial steps that benefit from being documented together?

**Decision rule:** If at least 3 of 4 answers are "yes", proceed to Phase 2. Otherwise, suggest recording as a `[LEARN]` tag in MEMORY.md instead (simpler, lower overhead).

If borderline, ask the user:
> "This seems useful but may not warrant a full skill. Should I create a skill or just add a [LEARN] tag to MEMORY.md?"

## Phase 2: Creation Guard + Read Patterns

Run the **creation-guard** analysis (see [`skills/creation-guard/SKILL.md`](../creation-guard/SKILL.md)):

1. Identify the proposal (name, type, purpose, key functions, keywords)
2. Search existing skills and agents for overlap (skill-index scan + keyword grep)
3. Analyse overlap and generate a recommendation:

| Recommendation | Criteria | Action |
|----------------|----------|--------|
| **PROCEED** | <20% overlap, genuinely new | Continue to Phase 3 |
| **EXTEND** | 50%+ overlap with one existing | Modify existing skill instead — stop here |
| **COMPOSE** | Multiple artifacts cover 80%+ | Create wrapper or document workflow — stop here |
| **ITERATE** | 20-50% overlap, needs refinement | Ask the user to clarify differentiation, then re-evaluate |
| **BLOCK** | Would create duplication | Do not create — stop here |

4. Present the creation-guard analysis to the user and get explicit approval before proceeding
5. **Read [`skills/shared/skill-design-patterns.md`](../shared/skill-design-patterns.md)** — choose the structural pattern that fits:
   - **Workflow-based** — multi-step with phases and review gates
   - **Task-based** — focused input/output with processing rules
   - **Agent-delegation** — multiple subagents, each handling one concern
   - **Reference-based** — augmenting with domain knowledge via `references/`

## Phase 3: Design the Skill

Before writing, make three decisions:

**1. Choose the structural pattern** (from Phase 2). State it explicitly:
> "This is a [workflow/task/agent-delegation/reference]-based skill."

**2. Identify resources needed:**
- Does the skill need `scripts/` for deterministic operations?
- Does it need `references/` for detailed specs, rubrics, or large examples?
- Does it need to delegate to subagents?

**3. Draft the architecture** — for non-trivial skills, sketch the flow:
```
Input → [Step A] → REVIEW GATE → [Step B] → Output
```

## Phase 4: Build the Skill

Write `skills/{name}/SKILL.md`:

### Frontmatter

```yaml
---
name: {kebab-case-name}
description: "{What it does. Concrete task types. Use when...}"
allowed_tools:
  - {minimum set of tools needed}
---
```

### Body Structure

The body varies by pattern, but always includes these elements:

```markdown
# {Skill Name}: {Short Description}

## When to Use
[Activation conditions — natural language triggers and /command]

## {Main Workflow / Processing Rules / Delegation Protocol}
[The core of the skill — structured per the chosen pattern]

## {Anti-Patterns / Never Do These}
[What NOT to do — agents default to generic without constraints]

## Output Format
[What the output looks like]

## Verification
[How to confirm it worked]
```

**Optional sections** (add when relevant):
- `## Defaults` — assumptions table to reduce friction
- `## Examples` — concrete before/after or good/bad snippets
- `## Notes` — edge cases, limitations

### Writing Rules

- **Imperative form.** "Parse the input" not "You should parse the input."
- **Be specific about what NOT to do.** Anti-pattern lists are highly effective.
- **Include concrete examples.** Show expected input/output pairs.
- **Keep SKILL.md under 300 lines.** Move detail to `references/`.
- **Every instruction must be actionable.** No throat-clearing.
- **Use tables for structured data.** Faster to parse than prose.

### Naming Conventions

- **Directory and name:** `kebab-case`, descriptive, 2-4 words
- **Avoid generic names:** `fix-bug` is bad; `fix-overleaf-sync-conflict` is good
- **Match the trigger:** If the natural trigger is "compile my slides", the name should relate to slide compilation

### Allowed Tools

Follow principle of least privilege:

| Skill type | Tools |
|-----------|-------|
| Report-only | `Read`, `Glob`, `Grep` |
| File-creating | + `Write`, `Edit` |
| Shell-needing | + specific `Bash(command*)` patterns |
| Interactive | + `AskUserQuestion` |
| Delegating | + `Task` |

## Phase 5: Validate

Run the validation script on the new skill:

```bash
uv run python skills/learn/scripts/validate_skill.py skills/{name}
```

Fix all errors. Address warnings to improve quality. Use `--strict` to promote warnings to errors.

The validator checks: frontmatter validity, name format and directory match, description quality, body length, broken links, referenced directories, and placeholder text.

## Phase 6: Confirm

1. Check that `~/.claude/skills/{name}/SKILL.md` exists (via the symlink)
2. Tell the user: "Created `/{name}` — [one-line summary]. It's available immediately in all projects."
3. If the skill is substantial, suggest updating `docs/skills.md` with the new entry

## What This Skill Does NOT Do

- **Does not replace `[LEARN]` tags** — one-liner corrections still go in MEMORY.md via the `learn-tags` rule
- **Does not create agents** — agents need separate context and persistent memory
- **Does not modify existing skills** — if an existing skill needs updating, do that directly
