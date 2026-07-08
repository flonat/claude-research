# Phase 4.1, 4.3, 4.4 — Paper directory conventions

> Cross-cutting checks for `paper*/` directories. The nested-pattern paper directory is the central concern of Phase 4.

## 4.1 Paper directory convention (nested pattern)

Each `paper*/` directory should be a **real directory** containing a `paper/` symlink → Overleaf. This allows venue-specific files (checklists, cover letters) alongside the Overleaf content.

| Check | What to look for | Severity |
|-------|-----------------|----------|
| `paper*/` is a real directory | `test -d paper-xxx && ! test -L paper-xxx` | Expected (nested pattern) |
| `paper*/` is a direct symlink | `test -L paper-xxx` | Degraded — "Direct symlink; should use nested pattern" |
| `paper*/paper/` symlink exists | `test -L paper-xxx/paper` | Missing if absent |
| Symlink target exists | `test -d paper-xxx/paper` | Missing — "Overleaf target missing" |
| Symlink target in Overleaf | `readlink paper-xxx/paper` contains "Overleaf" | Info if pointing elsewhere |
| Symlink path is **relative** | `readlink paper-xxx/paper` does NOT start with `/`, `~`, `/Volumes/`, or `~/Library/CloudStorage/` | Degraded — "Absolute symlink embeds this machine's Dropbox root and breaks across machines (incident 2026-04-19, see `rules/multi-machine.md`). Should be relative (e.g., `../../../../../Apps/Overleaf/<folder>`)." |

Remediation for absolute symlink: `cd paper-xxx && rm paper && ln -s '../../../../../Apps/Overleaf/<folder>' paper`.

## 4.3 Sibling paper directory check

| Check | What to look for | Severity |
|-------|-----------------|----------|
| Multiple `paper-*/` with same content | Compare `paper-*/paper/main.tex` (via `diff` on first 50 lines, ignoring whitespace). | Degraded — "Paper dirs `<a>` and `<b>` appear to hold the same manuscript; consider consolidating" |
| Multiple `paper-*/` with same Overleaf target | `readlink paper-*/paper` — if two symlinks point to the same Overleaf folder, flag | Missing — "Two paper dirs symlink to the same Overleaf target" |

Remediation: present the near-duplicate pair to the user, ask which to keep, rename the symlink of the survivor rather than deleting references (per `rules/overleaf-separation.md`).

## 4.4 Backup directory

Each `paper-{venue}/` directory should contain its own `backup/` subdirectory for Overleaf snapshots.

| Check | What to look for | Severity |
|-------|-----------------|----------|
| `paper-{venue}/backup/` exists | Each `paper*` directory must contain a `backup/` subdirectory | Missing |
| Wrong convention (root-level) | `backup/` at project root instead of inside `paper-{venue}/` | Degraded |
| Wrong convention (top-level named) | `paper-*-backup/` dirs at project root | Degraded |
| No paper directories | Skip this check entirely | — |

Remediation: `for d in paper*/; do mkdir -p "${d}backup"; done`.
