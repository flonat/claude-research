# Rule: Sub-Agent Write Guard

## Principle

**Sub-agents must not run `git commit`, `git push`, `latexmk`, or any other write/build command without explicit authorisation in the prompt.** The orchestrator (main context) handles all git activity, all builds, and all file edits outside the assigned scope. This applies even when a sub-agent could plausibly infer that a commit/build is the natural next step.

## Why this rule exists


## What "explicit authorisation" looks like

The sub-agent prompt must contain something like:

> "You are authorised to: edit files matching `paper-{venue}/paper/*.tex`. You are NOT authorised to run git commands, latexmk, or any build."

OR, when builds/commits are needed:

> "After editing, run `latexmk -pdf main.tex` exactly once and report the exit code. Do NOT commit."

The default is read-only + scoped writes. Explicit affirmation expands the surface.

## Standard forbid-list (paste into prompts that need it)

```
## Scope of action — DO NOT do these things

This sub-agent has a narrow scope. It does NOT inherit the orchestrator's
authorisation for any other action. Do NOT do any of the following, even if
they would seem like a natural next step:

- Do NOT run `git add`, `git commit`, `git push`, or any other git
  write command. The orchestrator handles all git activity.
- Do NOT run any build command (`latexmk`, `pdflatex`, `Rscript`,
  `uv run python <script>` for non-utility scripts, etc.) unless the
  task explicitly requires it. The orchestrator handles builds.
- Do NOT edit `.context/` files. The orchestrator handles session context.
- Do NOT edit `MEMORY.md`, `CLAUDE.md`, `README.md`, or any project-level
  documentation file. The orchestrator handles project state.
- Do NOT edit any file outside the assigned scope.
- Do NOT create new files outside the assigned scope.

If you find yourself wanting to do any of these, stop and include what
you were about to do in your final summary. The orchestrator decides.
```

## When This Applies

- Every Agent / Task tool dispatch where the sub-agent has `Edit`, `Write`, or `Bash` available
- Project-level orchestration agents

## When to Skip

- Read-only sub-agents (`subagent_type: Explore`, search-only) — explicit forbid-list optional
- Single-file lookup or grep tasks — Bash with `grep`/`find` only is fine without the full list
- Pre-tested sub-agent templates that have the forbid-list baked in


## Failure modes prevented

- **S2** unauthorised sub-agent commit — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **S3** unauthorised sub-agent build — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
- **S5** sub-agent touches project docs — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)

## Cross-References

| Rule | Relationship |
|---|---|
| `subagent-prompt-discipline.md` | Defines self-contained prompt requirements; this rule is the action-scope companion |
| `agents-vs-skills.md` | When to use a sub-agent vs a skill |

## Anti-Patterns

- **Don't** assume "drafted a paper → compile + commit" is the natural sub-agent flow. It isn't. The orchestrator decides.
- **Don't** rely on the sub-agent reading global rules — they don't auto-load in sub-agent context. Inline the forbid-list.
- **Don't** dispatch a sub-agent with `Bash` and Edit access without an explicit forbid-list. Default permissions enable harmful side-effects.
