# Checkpoint-Based Resumability — Shared Protocol

> Enables multi-phase skills to survive session crashes and context compactions by saving progress after each completed phase. On restart, the pipeline auto-skips completed phases.

## Principle


## When This Applies

- Any skill with 3+ sequential phases where each phase produces durable output
- Skills that spawn sub-agents (agent failures shouldn't lose prior phases)
- Skills that modify external state (vault, git) and need to know what's already been done
- Skills invoked with topic slugs or project paths (resumability is expected)

## When to Skip

- Standalone / single-phase skills (e.g., `/proofread`, `/rate`)
- Skills that complete in under 60 seconds
- Skills where re-running is cheap and idempotent
- When the user says "start fresh" or "from scratch"

## Checkpoint Format

Each checkpoint is a JSON file at `.checkpoints/<skill>/<run-id>.json`:

```json
{
  "skill": "literature",
  "mode": "pipeline",
  "run_id": "lit-2026-04-11-1430",
  "started_at": "2026-04-11T14:30:00Z",
  "phases": [
    {
      "name": "Phase 1: Project Resolution",
      "status": "complete",
      "started_at": "2026-04-11T14:30:00Z",
      "completed_at": "2026-04-11T14:30:45Z",
      "outputs": {
        "project_path": "/path/to/project",
        "topic_slug": "carbon-collusion"
      }
    },
    {
      "name": "Phase 2: Search",
      "status": "complete",
      "started_at": "2026-04-11T14:30:45Z",
      "completed_at": "2026-04-11T14:33:12Z",
      "outputs": {
        "papers_found": 23,
        "search_results_file": "/tmp/lit-search-results.json"
      }
    },
    {
      "name": "Phase 3: Verification",
      "status": "failed",
      "started_at": "2026-04-11T14:33:12Z",
      "completed_at": "2026-04-11T14:35:00Z",
      "error": "Context limit reached during DOI batch verification",
      "outputs": {
        "verified_count": 14,
        "remaining_count": 9
      }
    }
  ],
  "resume_from": "Phase 3: Verification",
  "context": {
    "query": "carbon auction collusion detection",
    "n_requested": 25
  }
}
```

## Directory Structure

```
<project-root>/
└── .checkpoints/
    ├── literature/
    │   └── lit-2026-04-11-1430.json
    ├── computational-experiments/
    │   └── exp-2026-04-10-0900.json
        └── pw-2026-04-09-1600.json
```

For skills invoked outside a project directory, use `~/.claude/checkpoints/` instead.

## Operations

### Save (after each phase completes)

```bash
mkdir -p .checkpoints/<skill>/
```

Write or update the checkpoint file. The `run_id` is `<skill-prefix>-<ISO-date>-<HHMM>` from when the run started.

**What to save in `outputs`:**
- File paths to durable artifacts (search results, enriched data, draft sections)
- Counts and metrics (papers found, sections written)
- Configuration used (so resume can continue with same settings)
- **NOT** large data blobs — only pointers to where data was written

### Resume (at skill start)

1. Check for existing checkpoints: `ls .checkpoints/<skill>/*.json`
2. If a checkpoint exists with `resume_from` set (incomplete run):
   - Present to user: "Found incomplete `/<skill>` run from {date}. Resume from {phase}? (y/n/fresh)"
   - If yes: skip completed phases, start from `resume_from`
   - If no/fresh: archive the old checkpoint, start new run
3. If no checkpoint exists: normal fresh start

### Clean (after successful completion)

When all phases complete successfully:
1. Update checkpoint: set all phases to `complete`, clear `resume_from`
2. Move to `.checkpoints/<skill>/archive/` (keep last 5 for debugging)
3. Delete archived checkpoints older than 7 days

### Partial Resume

Some phases produce partial output (e.g., verified 14/23 papers before crash). The checkpoint stores partial progress in `outputs`. On resume:
- Read the partial outputs
- Continue from where the phase left off (e.g., verify remaining 9 papers)
- Don't re-do work that's already saved

## Skill Integration Guide

### For skill authors: adding checkpoints to a multi-phase skill

1. **At skill start**: check for resumable checkpoint
2. **After each phase**: save checkpoint with phase outputs
3. **On error**: save checkpoint with `status: "failed"` and `error` message
4. **On completion**: clean up checkpoint

### Minimal integration (3 lines per phase):

```
# Before phase
[check if this phase is already complete in checkpoint → skip if so]

# After phase succeeds  
[save checkpoint: phase complete, record outputs]

# On phase failure
[save checkpoint: phase failed, record partial outputs and error]
```

## Skills to Retrofit (priority order)

| Skill | Phases | Crash risk | Priority |
|-------|--------|-----------|----------|
| `/literature` (pipeline) | 6 phases | High (sub-agents, MCP calls) | P0 |
| `/computational-experiments` | 5 phases | Medium (long runs) | P1 |
| `/pre-submission-report` | 4 agents | High (multi-agent orchestration) | P1 |
| `/replication-package` | 4 phases | Low (mostly file ops) | P3 |

## Relationship with Other Persistence

| Mechanism | Purpose | Survives |
|-----------|---------|----------|
| **Checkpoints** | Resume a crashed pipeline run | Session crash, context compaction |
| **Session logs** (`log/`) | Human-readable record of what happened | Forever (git) |
| **`.planning/state.md`** | Track progress across multiple sessions | Until project completes |
| **Material passport** | Track artifact provenance and staleness | Until artifact is superseded |

Checkpoints are ephemeral (cleaned after success). They exist only to bridge the gap between "skill started" and "skill completed."
