# Round 2 Q7 — HPC Scaffold

> Referenced from: `init-project-research/SKILL.md` Phase 1 Round 2 Q7 and Phase 3 (conditional structure).

Only ask this question for **Experimental, Computational, or Mixed** projects. Theoretical projects skip it.

## Question

"Will this need your HPC cluster (GPU, long sweeps, large state spaces)? — Yes / No / Later."

## Behaviour by answer

| Answer | What to do |
|--------|-----------|
| **Yes** | Scaffold the full `hpc/` directory now (file list below). |
| **Later** | Add `hpc/` to `.gitignore` as a placeholder. Scaffold on demand when the user runs `/init-project-research --hpc <project>` or asks for HPC setup directly. |
| **No** | Do nothing. |

## Files scaffolded when Yes

| File | Purpose |
|------|---------|
| `hpc/submit.sbatch` | Single-job SLURM script. Entry point matches the project's `src/` package. |
| `hpc/sweep.sbatch` | Array-job SLURM script for parameter sweeps. |
| `hpc/env-setup.sh` | Idempotent module-load + `uv sync` invocation. |
| `hpc/sync-up.sh` | Wraps `scripts/hpc/sync-project.sh` to push project state to Avon. |
| `hpc/sync-down.sh` | Wraps `scripts/hpc/sync-project.sh` to pull results back. |
| `hpc/README.md` | Per-project HPC notes (partition choice, expected runtime, resource needs). |

For LLM projects, also add:

| File | Purpose |
|------|---------|
| `hpc/prestage-models.sh` | Downloads and caches model weights to scratch before job dispatch (avoids login-node bandwidth limits). |

## Sbatch invariants (apply to both submit.sbatch and sweep.sbatch)

- `--account=wbs` (the user's Avon account).
- Log `git-sha.txt` and `git-status.txt` to `OUT_DIR` **before** `srun` runs the workload, so results are traceable to a specific commit.
- Use `--mail-user=user@example.com` only on `--mail-type=FAIL` (avoid mail spam on completion).

## Templates and reference implementations

- Templates: `Task Management/templates/slurm/{compute,devel,hmem,gpu,array}.sbatch` — all use `--account=wbs`.
- Reference projects with working HPC setups: `Projects/[your-project]/hpc/`.
- Full HPC guide: Task Management `docs/guides/hpc.md` (access via 2FA, SSH multiplex, partition choice, per-project workflow).
