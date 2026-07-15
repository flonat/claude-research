# Dropbox EPERM on the headless Mini — FDA on `mosh-server` (not tmux)

> A mosh-adjacent failure on the headless Mac mini (`mosh → tmux → AI coding client`): mid-session, every shell access to the configured SSD-backed Dropbox root starts returning **"Operation not permitted" (EPERM)**, while the same paths work from the user's own SSH terminal. Root cause is TCC/Full-Disk-Access gating on the wrong responsible process. First diagnosed 2026-06-05 during QUIVER-EA (the trigger incident); the mechanism is general to any Dropbox-synced project reached headlessly.

## Symptom

- `ls -ld <dir>` — works. `ls <dir>/`, `cat`, `cp`, `head`, `Write`, `Edit` — all EPERM.
- Same paths from the user's own SSH/Terminal login: **work fine** (same UID 501).
- Non-Dropbox paths (the local project checkout, `/tmp`) — fine.
- Persists even with `dangerouslyDisableSandbox` → it is **NOT** the Bash sandbox.
- Worked for hours, then broke **abruptly** mid-session.

## Root cause (two-stage)

1. **Dropbox File-Provider re-adopted the folder → provider-managed files, which require Full Disk Access (TCC).** The trigger is usually a **folder rename** (e.g. an Overleaf↔Dropbox bridge renaming a venue folder), which makes Dropbox's File-Provider extension re-adopt the contents as *provider-managed*. Plain materialised files (pre-rename) do **not** need FDA — which is why it worked for hours, then broke after the rename. **Heavy churn aggravates** re-adoption (mass dir creation inside a provider-managed tree can retrigger adoption on the parent — e.g. a sweep writing ~4,000 per-run dirs into a Dropbox-synced `results/`), but churn is the *aggravator*, not the root cause for renamed dirs.
2. **The TCC "responsible process" is `mosh-server`, not tmux.** the user reaches the headless Mini via `mosh → tmux`. `mosh-server` detaches from the SSH login and reparents to launchd; the shell, tmux, and Claude Code all chain off it. TCC attributes file-access to that responsible process — so **granting FDA to tmux alone changes nothing**. The interactive terminal worked because the login shell has its own TCC accounting (already FDA-granted via Terminal/iTerm); Claude Code inherited the `mosh-server` attribution and lacked the grant.

## Fix

Grant Full Disk Access (System Settings → Privacy & Security → Full Disk Access → `+`, ⇧⌘G to paste) to:

- `/opt/homebrew/bin/mosh-server` ← **the key one** (TCC responsible process)
- `/opt/homebrew/bin/tmux`
- Optional/tidy: `/opt/homebrew/bin/mosh`, `/usr/libexec/sshd-keygen-wrapper`

**TCC grants only take effect at process launch** — a `mosh-server` that predates the grant stays EPERM. Apply the grant, then get a **NEW** mosh-server (reconnecting the existing mosh is NOT enough):

```sh
tmux kill-server                       # from inside the broken session
# then FULLY disconnect mosh (close the Terminal/iTerm window), reconnect:
#   1. close the window holding the mosh session
#   2. reopen, `mosh mini`
#   3. `tmux new`
#   4. relaunch claude
```

## Verify it took

```sh
RESEARCH_ROOT="$(head -1 "$HOME/.config/task-mgmt/research-root")"
ls "$RESEARCH_ROOT/<theme>/<project>/results/"                 # should succeed, no EPERM
head "$RESEARCH_ROOT/<theme>/<project>/CLAUDE.md"
```

If still EPERM, the mosh-server is still the pre-grant one — `ps -o pid,ppid,command -p $(pgrep mosh-server)`; the PID must **post-date** the FDA grant timestamp.

## Wrong turns (none of these are the cause)

- Quitting the Dropbox menu-bar app — the `garcon` File-Provider extension runs independently.
- `killall garcon` — EPERM persists; FDA gating is enforced upstream of the servicer.
- `open -a Dropbox` "up to date" sync — access fluctuates then fully re-locks.
- Assuming it's a transient sync lock from churn alone — that's the **superseded** `reference_dropbox_eperm_new_dirs.md` framing; for renamed/provider-managed dirs the fix is FDA-on-mosh-server, not `rm`+recreate.

## Prevention

1. **Keep churn off Dropbox** — sweep/experiment outputs to a non-Dropbox scratch dir (e.g. `~/<project>-runs/…`), `.gitignore` any per-run dirs defensively.
2. **Rename folders sparingly** — renames promote contents to provider-managed status; if a rename is unavoidable (Overleaf↔Dropbox bridge), expect a mosh-server restart on the Mini afterward.
3. **Make the FDA grant permanent** — the Mini setup checklist should include FDA for `mosh-server`/`tmux` as a standing grant; once set, future sessions are immune.

## Cross-references

- `reference_fda_registry.md` (auto-memory) — the registry of every binary needing FDA on the Mini; this doc is the *why* behind the `mosh-server` entry.
- `reference_dropbox_eperm_new_dirs.md` (auto-memory) — the churn-only framing this doc corrects.
- `reference_launchd_cannot_read_dropbox.md` (auto-memory) — sibling File-Provider gotcha (launchd context).
- `multi-machine.md` rule — Dropbox symlink hygiene (relative, not absolute).
