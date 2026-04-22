---
name: handoff
description: "Use when you need to pass state to the next session in the current working directory. Writes a handoff.md file that the next session's SessionStart hook will read and delete."
allowed-tools: Read, Write, Bash(pwd), Bash(ls*), Bash(git status*), Bash(git log*)
argument-hint: [optional-note]
---

# Handoff Skill

> Write a one-shot handoff note to the next session, in the current working directory.

## Purpose

Bridge state across a restart or `/exit` when a full session log is overkill. The next session's SessionStart hook (`handoff-read.sh`) reads `handoff.md`, injects its contents as additional context, then **deletes** the file. One read, gone.

Use this when:
- You need to restart (e.g., MCP server re-enable, permission change, context pressure)
- You want to hand off mid-task state to the next session without polluting `log/`
- A quick note is enough — not a full `/session-close`

## When NOT to Use

- End of a substantive work session → use `/session-close` (proper logs, git commit)
- Permanent decisions or learnings → use MEMORY.md with `[LEARN]` tags
- Cross-project notes → use `.context/agent-messages.md`

## Workflow

### Step 1: Gather state

Collect:
- **Current working directory** (`pwd`) — the handoff lives here
- **What was happening** — the immediate task, not a session recap
- **What's next** — the specific next action
- **Open loops** — files mid-edit, background processes, pending confirmations
- **Blockers** — why the session is ending (e.g., "Paperpile MCP needs restart")

### Step 2: Write `handoff.md` in cwd

Use this template:

```markdown
# Handoff — <YYYY-MM-DD HH:MM>

## Where we are
<1-3 sentences on current task state>

## Next action
<The single next thing to do — be specific>

## Open loops
- <file.py mid-edit at line N>
- <background job: description>
- <HPC job $SLURM_JOB_ID on your-hpc: submitted/running/completed; OUT_DIR=~/projects/<name>/out/<jobid>/>
- <pending user confirmation: question>

## Blockers / context the next session needs
<Why the handoff exists. API keys set? MCP restarted? Permission added?>

## Files touched this session
- <path:line> — <what changed>

## Scratch
<Anything else — half-formed thoughts, commands to try, URLs>
```

Keep it tight. The next session reads this once as SessionStart context — it should be skimmable in 10 seconds.

### Step 3: Confirm

Tell the user: "Handoff written to `<cwd>/handoff.md`. Next session in this directory will read and delete it."

## Hook Behavior

The companion hook `handoff-read.sh` fires on **every** SessionStart (startup + resume + compact). If `handoff.md` exists in the session's cwd:

1. Reads contents
2. Injects as `additionalContext` with the header `# Handoff from previous session`
3. Deletes `handoff.md` (scratch)

Zero token cost when no handoff exists.

## Important

- Handoff is **ephemeral** — one-shot. If you need durable state, write to `log/` or MEMORY.md instead.
- `handoff.md` should NOT be committed. Add to `.gitignore` if the directory has one.
- If the next session's cwd differs, the handoff won't fire — always `cd` to the same directory before restarting.
