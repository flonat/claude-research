# Transitioning to flonat-research

The framework was previously distributed as `claude-research` and installed
repository-owned links under `~/.claude/`. The new `flonat-research` layout is
client-neutral, supports Claude Code and Codex explicitly, and installs
content-addressed copies with a receipt. The GitHub repository was renamed on
2026-07-12; the former URL remains a redirect for existing checkouts.

## Safe transition process

1. **Inspect the current installation.** Note any real files you maintain under
   `~/.claude/skills`, `~/.claude/agents`, `~/.claude/rules`, or
   `~/.claude/hooks`. The installer never removes an unowned link or overwrites
   an unmanaged file.
2. **Update the checkout.** Run `git pull --ff-only`. Do not remove the old
   links manually first; ownership can be verified only while their targets
   still exist.
3. **Preview the required migration.** Run
   `./scripts/setup.sh --client both --check`. A legacy-link diagnostic is
   expected on old installations.
4. **Migrate proven repository-owned links.** Run
   `./scripts/setup.sh --client both --migrate-legacy`. On Windows use
   `.\scripts\setup.ps1 -Client both -MigrateLegacy`. Only links or junctions
   resolving to this checkout are removed. Unowned paths stop the migration.
5. **Verify the managed installation.** Run
   `./scripts/setup.sh --client both --check`. It must report `PASS` before the
   old checkout or any backup is removed.
6. **Check skill discovery.** Shared names live in `~/.agents/skills/` for
   Codex and in `~/.claude/shared-skills/` behind small Claude command adapters.
   They do not also appear in `~/.claude/skills/`, preventing duplicate entries
   in Codex Desktop. Claude-only skills remain under `~/.claude/skills/`.

Select `--client claude` or `--client codex` instead of `both` when only one
client is installed. Re-run the installer with `--update` after each pull.

## Files-first continuity

Both clients use `MEMORY.md`, `.context/`, and `.context/ai-handoff.md` as the
portable context contract. Claude hooks can surface those files automatically,
but they are conveniences rather than a dependency. Codex reads the same files
directly through `AGENTS.md`.

## Rollback

If validation fails, stop before deleting anything. Divergent files previously
managed by the installer are preserved under
`~/.config/flonat-research/backups/<timestamp>/`. Restore the relevant file,
retain the checkout, and run `--check` again. The installer does not modify an
existing `~/.claude/settings.json`; merge settings manually if required.

The repository rename from `claude-research` to `flonat-research` does not
change installed paths or receipts. GitHub redirects preserve old clone URLs;
new clones should use `https://github.com/flonat/flonat-research.git`.

## Transition completion

The client-neutral installer is now the only supported installation path.
Private-workspace commands such as `claude-pull`, `sync-to-codex.sh`, and
`sync-to-claude-home.sh` were migration mechanisms and are not part of this
distribution. Existing public checkouts need only pull the renamed repository
and run the managed-copy installer with `--update`; no client-to-client copy is
required. Keep portable continuity in `MEMORY.md`, `.context/`, and
`.context/ai-handoff.md`, not in either client's home directory.
