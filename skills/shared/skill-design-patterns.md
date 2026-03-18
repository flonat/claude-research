# Skill Design Patterns

> Reference for designing new skills. Read this before writing any SKILL.md.
> Loaded on demand by `/learn` and when manually creating skills.

## Structural Patterns

Choose based on what the skill does. Most skills fit one pattern; some combine two.

### Workflow-Based

Multi-step processes where order matters and user approval is needed between phases.

```
Phase 1: Gather → Phase 2: Process → REVIEW GATE → Phase 3: Output
```

**When to use:** Report generation, project bootstrapping, multi-pass analysis, content creation with review cycles.

**Key elements:**
- Numbered phases with explicit entry/exit criteria
- Review gates between phases (hard stops where the agent presents work and waits)
- Default assumptions table to reduce friction


### Task-Based

Focused input/output with clear processing rules. No phases — just do the thing well.

```
Input spec → Processing rules → Output spec → Quality checks
```

**When to use:** Code review, proofreading, validation, data transformation, file conversion.

**Key elements:**
- Explicit input format and constraints
- Processing rules as imperative instructions
- Output format specification
- Verification criteria


### Agent-Delegation

Multiple subagents, each responsible for a distinct concern. Coordinator manages handoffs.

```
Coordinator → Subagent A (generate) → Subagent B (critique) → Coordinator (synthesize)
```

**When to use:** Tasks where quality benefits from separation of concerns — writing with editing, analysis with critique, multi-perspective evaluation.

**Key elements:**
- `agents/` directory or Task tool delegation with focused system prompts
- Each subagent does one thing well
- Coordinator synthesizes outputs


### Reference-Based

Augments the agent with domain knowledge it lacks, loaded on demand.

```
SKILL.md (routing + procedures) → references/ (domain knowledge)
```

**When to use:** Specialized domains where training data is insufficient — niche APIs, internal conventions, proprietary formats, scoring rubrics.

**Key elements:**
- SKILL.md stays concise — routing logic and procedures only
- `references/` contains detailed specs, lookup tables, scoring rubrics
- Agent reads references on demand, not all at once


---

## Design Elements

### Review Gates

Prevent runaway execution by requiring user approval at checkpoints.

```markdown
### REVIEW GATE: [Gate Name]

Present the following to the user and STOP:
- [What to show]
- [What to show]

Do NOT proceed until the user explicitly approves.
```

Place gates after planning/before execution, and after first draft/before refinement.

### Anti-Pattern Lists

Tell the agent what NOT to do. Agents default to safe, generic patterns unless explicitly constrained. Negative constraints are as important as positive instructions.

```markdown
## Never Do These

- Never use "leverage" — use "use" instead
- Never produce bullet points when a table would be clearer
- Never assume verbose output — default to concise
```

### Default Assumptions Table

Reduce friction by pre-answering common questions. Only ask the user what can't be reasonably defaulted.

```markdown
## Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Output format | Markdown | User specifies otherwise |
| Verbosity | Concise | User says "detailed" |
| Location | Project root | User provides path |
```

### Drift Prevention

Skills that reference external state (database schemas, file counts, theme lists, status options) go stale silently. Use this 3-part pattern when a skill has hardcoded values derived from mutable sources.

**Part 1: Runtime detection (Phase 0)**

Add a Phase 0 at the start of the skill that checks hardcoded values against reality before proceeding:

```markdown
## Phase 0: Drift Detection

Before starting, verify skill references:
1. Count actual {items} — compare against ~N in this skill
2. List actual {categories} — compare against the N listed here
3. Fetch {schema/config} — verify properties still match

If drift detected:
- Warn in output header: "⚠ Drift: {what} was {expected}, actually {found}"
- Use actual values for this run (self-heal)
- Log to references/drift-checks.md
```

**Part 2: Drift reference file**

Create `references/drift-checks.md` listing every drift-prone value:

```markdown
| Value | Location | Source of Truth | Trigger |
|-------|----------|-----------------|---------|
| Topic count (~67) | SKILL.md Phase 1 | ls topics/**/*.md | /scaffold-atlas-topics |
| Theme list (9) | SKILL.md, sa-prompts.md, build_report.py | ls Research Projects/ | New theme dir |
```

Include a Drift Log table where Phase 0 appends detected drift with timestamps.

**Part 3: Trigger notes in related skills**

Add cross-references in skills that commonly cause drift:

```markdown
| `/atlas-review` | **Drift trigger:** new topics change count — see drift-checks.md |
```

This ensures the person (or agent) running the triggering skill is aware that downstream skills may need updating.

**When to use:** Any skill with hardcoded counts, database IDs, schema property names, status option lists, file paths derived from external systems, or theme/category lists that grow over time.

**When to skip:** Skills that derive all values at runtime (no hardcoded references to external state).

**Example:** `/atlas-review` — topic count, theme list, Notion schemas, stage mappings, rules count all drift. Phase 0 detects and self-heals; `references/drift-checks.md` tracks 8 drift-prone values.

### Progressive Disclosure

Control what goes where based on how often the agent needs it:

| Location | Loaded | Use for |
|----------|--------|---------|
| `name` + `description` | Always in context | Trigger matching — when to activate |
| SKILL.md body | When skill triggers | Core procedures, workflow, constraints |
| `references/` | On demand via Read | Detailed specs, large examples, lookup tables |
| `scripts/` | On demand via Bash | Deterministic operations (validation, formatting) |

**Rule of thumb:** If the agent needs it every time → SKILL.md body. If it needs it sometimes → `references/`. If it should execute it → `scripts/`.

---

## Writing Guidelines

### For the Description (Frontmatter)

The `description` determines when the skill activates. It's always in context. **Write in third person** — the description is injected into the system prompt, and inconsistent point-of-view causes discovery problems.

**Good:**
- `"Analyze datasets using statistical methods. Handles EDA, hypothesis testing, and causal inference. Use when asked to analyze CSV/Excel data or run A/B test analysis."`
- `"Academic proofreading for LaTeX papers. Grammar, notation consistency, citation format, tone. Report-only — never edits source files."`

**Bad:**
- `"A helpful skill"` — too vague, triggers on everything
- `"I can help you process files"` — wrong point-of-view (first person)
- `"Skill for doing things with files"` — will trigger on every file operation

**Tips:**
- Lead with the primary capability
- Include concrete task types as trigger phrases
- End with "Use when..." to define activation conditions
- State what it does NOT do if there's a common confusion
- Max 1024 characters; name max 64 characters (lowercase, hyphens, numbers only)

### For the Body (System Prompt)

- **Write for an AI agent, not a human.** Procedural knowledge the agent cannot infer.
- **Imperative form.** "Parse the input" not "You should parse the input."
- **Be specific about what NOT to do.** Anti-pattern lists are highly effective.
- **Include concrete examples.** Input/output pairs and good/bad snippets beat abstract rules.
- **Keep SKILL.md under 500 lines** (Anthropic official threshold). Move detailed specs and large examples to `references/`. Aim for under 300 lines when possible.
- **Every instruction must be actionable.** If the agent cannot act on a sentence, delete it.
- **Use tables for structured data.** Defaults, field specs, command references — tables are faster to parse than prose.
- **One section, one concern.** Don't mix workflow steps with quality criteria.

### For allowed_tools

Follow principle of least privilege:

| Skill type | Tools |
|-----------|-------|
| Report-only | `Read`, `Glob`, `Grep` |
| File-creating | + `Write`, `Edit` |
| Shell-needing | + specific `Bash(command*)` patterns |
| Interactive | + `AskUserQuestion` |
| Delegating | + `Task` |

---

## Quality Checklist

Before finalising any skill, verify:

| Check | Question |
|-------|----------|
| Trigger clarity | Would Claude know when to invoke this from the description alone? |
| Pattern fit | Does the structure match one of the 4 patterns above? |
| No duplication | Does this overlap with an existing skill? |
| Anti-patterns | Does it say what NOT to do, not just what to do? |
| Examples present | Are there concrete before/after or good/bad examples? |
| Minimum tools | Only the tools actually needed are in `allowed_tools`? |
| No secrets | No API keys, tokens, or passwords? |
| References extracted | Is detailed reference material in `references/`, not inline? |
| Description specificity | Would the description distinguish this from similar skills? |
| Tested | Has the procedure been tested, not just theorised? |
| Refs one-level deep | All reference files link directly from SKILL.md (no nested refs)? |
| Third-person description | Description uses "Processes..." not "I can..." or "You can..."? |

---

## Evaluation-Driven Development

Per [Anthropic's official best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

1. **Identify gaps:** Run Claude on representative tasks without the skill. Document specific failures.
2. **Create evaluations:** Build 3+ scenarios that test these gaps.
3. **Establish baseline:** Measure Claude's performance without the skill.
4. **Write minimal instructions:** Just enough to address the gaps and pass evaluations.
5. **Iterate:** Execute evaluations, compare against baseline, refine.

### Claude A / Claude B Pattern

- **Claude A** (the expert): helps design and refine the skill
- **Claude B** (the user): tests the skill in real tasks with fresh context
- Observe Claude B's behavior, bring insights back to Claude A
- Repeat: observe → refine → test

This is similar to the existing `/skill-creator` workflow but emphasises real-task testing over synthetic evaluation.
