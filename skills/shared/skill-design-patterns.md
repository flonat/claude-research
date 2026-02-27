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

The `description` determines when the skill activates. It's always in context.

**Good:**
- `"Analyze datasets using statistical methods. Handles EDA, hypothesis testing, and causal inference. Use when asked to analyze CSV/Excel data or run A/B test analysis."`
- `"Academic proofreading for LaTeX papers. Grammar, notation consistency, citation format, tone. Report-only — never edits source files."`

**Bad:**
- `"A helpful skill"` — too vague, triggers on everything
- `"This skill helps users"` — tells the router nothing
- `"Skill for doing things with files"` — will trigger on every file operation

**Tips:**
- Lead with the primary capability
- Include concrete task types as trigger phrases
- End with "Use when..." to define activation conditions
- State what it does NOT do if there's a common confusion

### For the Body (System Prompt)

- **Write for an AI agent, not a human.** Procedural knowledge the agent cannot infer.
- **Imperative form.** "Parse the input" not "You should parse the input."
- **Be specific about what NOT to do.** Anti-pattern lists are highly effective.
- **Include concrete examples.** Input/output pairs and good/bad snippets beat abstract rules.
- **Keep SKILL.md under 300 lines.** Move detailed specs and large examples to `references/`.
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
