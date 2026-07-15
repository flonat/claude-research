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
   expected on old installations and names the exact `--migrate-legacy`
   command. Check mode never removes a link or writes managed files.
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
client is installed. After the one-time migration, pull with `git pull
--ff-only` and run the installer normally; `--update` remains only as a
backward-compatible alias.

## Files-first continuity

Both clients use `MEMORY.md`, `.context/`, and `.context/ai-handoff.md` as the
portable context contract. Claude hooks can surface those files automatically,
but they are conveniences rather than a dependency. Codex reads the same files
directly through `AGENTS.md`.

## Migrate the content, not just the links

The managed-copy migration above fixes deployment ownership. Review the old
Claude-only content separately:

1. Move durable shared guidance from a large hand-authored `CLAUDE.md` into
   neutral `AI.md`, `MEMORY.md`, and `.context/` files. Keep `CLAUDE.md` and
   `AGENTS.md` as thin client adapters.
2. Convert reusable slash commands into neutral skill directories with an
   explicit client/capability row. Do not copy command files directly into
   Codex discovery roots.
3. Keep one neutral agent body and generate Claude Markdown and Codex TOML
   adapters. Bundle every referenced support file with the installed agent.
4. Separate rules from hooks: rules express durable policy; hooks are optional
   client conveniences and must not be the only place shared context exists.
5. Separate MCP registrations from credentials. Codex workflows need a tested
   CLI or manual fallback; neither client should receive secrets from Git.
6. Retire old sync writers only after their callers and launch jobs point to
   the managed installer.

Use [`availability.md`](availability.md) to record a deliberate client-only or
external dependency. A missing row is not permission to assume compatibility.

## Choose one distribution

`flonat-research` and `flonat-research-friends` install overlapping managed
paths. Switching between them is a migration: keep the old checkout, run the
new installer in `--check` mode, inspect ownership, install, then verify. Do not
run both update loops against the same home directory.

## Transition project-local orchestration

If an existing project has hand-authored `.claude/agents/` or
`.claude/commands/`, do not copy those files into Codex. Run the reviewed
`init-project-orchestration` migration: it preserves unmanaged collisions,
creates neutral sources under `.ai/orchestration/`, and renders Claude and
Codex adapters deterministically. Inspect the migration plan and commit the
neutral sources plus generated project adapters together.

Use [`availability.md`](availability.md) to distinguish a genuinely
client-specific workflow from an asset that is simply not installed.

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
distribution. Existing symlink-based checkouts must complete the one-time
`--migrate-legacy` step above. Later updates need only pull the repository and
run the managed-copy installer; no client-to-client copy is required. Keep
portable continuity in `MEMORY.md`, `.context/`, and
`.context/ai-handoff.md`, not in either client's home directory.
