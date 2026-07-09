---
name: tailscale-mosh-recover
description: "Use when mosh hangs / fails to connect to a headless Mac mini after a Tailscale update or restart, OR when a remote-access tool (RustDesk, VNC, AnyDesk) fails to reach its public relay from an MDM-managed client. Layers — Tailscale daemon health (dual-install conflict, headless GUI-app limitation, Homebrew launchd takeover), downstream mosh-server cleanup (stale UDP bindings to old Tailscale IP), macOS resolver stuck state, and Tailscale direct-IP as relay-bypass fallback. Symptoms include `could not get canonical name for <host>`, `failed to connect to local Tailscale service`, `Tailscale.CLIError error 1`, `Connection closed by UNKNOWN port 65535`, `Failed to connect to rs-ny.rustdesk.com:21116: Please try later`."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(tailscale:*)
  - Bash(brew:*)
  - Bash(ps:*)
  - Bash(lsof:*)
  - Bash(kill:*)
  - Bash(tmux:*)
  - Bash(which:*)
  - Bash(ls:*)
  - Bash(ln:*)
  - Bash(rm:*)
  - Bash(sudo:*)
  - Bash(hash:*)
  - Bash(mdls:*)
  - AskUserQuestion
---

# Tailscale + Mosh Recovery (Headless Mac mini)

## Problem

After a Tailscale update or daemon restart on a headless Mac mini, mosh sessions break. Common symptoms (any combination):

- `tailscale status` returns: `failed to connect to local Tailscale service; is Tailscale running?`
- `mosh <host>` returns: `could not get canonical name for <host>: nodename nor servname provided, or not known`, then `Connection closed by UNKNOWN port 65535`, then `Did not find remote IP address (is SSH ProxyCommand disabled?)`.
- Tailscale GUI app CLI returns: `Tailscale.CLIError error 1`.
- `which tailscale` reports a path that does not actually exist on disk.
- `tailscale up` registers the machine as `<hostname>-1` (a duplicate of the original node — IP changed).

The two underlying problems are causally linked: Tailscale daemon trouble forces a re-auth → new Tailscale IP → existing mosh-server processes are bound to the old IP and become unreachable.

## Context / Triggers

| Sign | Likely cause |
|---|---|
| Mac mini's `tailscale status` says daemon not running | GUI app daemon needs a logged-in user session — won't run headless |
| `which tailscale` returns a path that `ls` says doesn't exist | Shell PATH cache + missing symlink (often the Homebrew symlink dropped during update) |
| Two Tailscale installs: GUI app at `/Applications/Tailscale.app` AND Homebrew Cellar | Dual install — one's daemon is fighting for the socket |
| `mosh` fails *only after* a working `tailscale up` re-registration | Stale `mosh-server` processes bound to the prior Tailscale IP |
| Old hostname offline + new hostname `<name>-1` in admin console | Re-auth created a new node; old one is stale |

## Solution

Work in this order: **Layer 1 (Tailscale daemon)** then **Layer 2 (mosh cleanup)**. If only mosh is broken and `tailscale status` is healthy, skip Layer 1.

### Layer 1: Tailscale daemon health (headless Mac mini)

**The headless constraint:** the standalone `Tailscale.app` GUI bundle's daemon needs an active user session. On a headless Mac mini (no monitor, no auto-login), the GUI daemon never starts. The right setup for headless is **Homebrew's `tailscale` package run as a launchd service** — it's a system service that survives reboots without any logged-in user.

#### Step 1.1: Confirm the symptom + identify installs

```bash
tailscale status              # likely: "failed to connect to local Tailscale service"
which tailscale               # may report a path that doesn't exist
ls -la /Applications/Tailscale.app  # GUI app present?
brew list tailscale 2>/dev/null     # Homebrew install present?
ls -la $(brew --prefix)/Cellar/tailscale  # Cellar contents if Homebrew has it
```

If both installs exist, that's the dual-install conflict. The CLI symlink at `/opt/homebrew/bin/tailscale` may have been removed by a recent update — leaving the daemon running (or not) and no CLI to talk to it.

#### Step 1.2: Remove the GUI app's broken CLI shim (if present)

The GUI app installs a shim at `/usr/local/bin/tailscale` that errors with `Tailscale.CLIError error 1` when the GUI app isn't running. Remove it to avoid PATH ambiguity:

```bash
sudo rm -f /usr/local/bin/tailscale
```

#### Step 1.3: Re-link the Homebrew CLI

The Homebrew binary still exists in `$(brew --prefix)/Cellar/tailscale/<version>/bin/tailscale`; it's just unlinked.

```bash
brew link tailscale
hash -r                       # clear shell PATH cache
which tailscale               # should now report /opt/homebrew/bin/tailscale
```

If `brew link` complains about a conflict, the conflicting path was likely the GUI shim from Step 1.2 — re-run Step 1.2 and try again. If you've decided to remove the GUI app entirely, `brew link --overwrite tailscale` is acceptable.

##### Variant: orphan-after-autoremove

If `which tailscale` returns nothing right after a `brew uninstall` of something else reported `Autoremoving ... tailscale`: the daemon is still running on the unlinked binary — `brew link --overwrite tailscale` restores the CLI without touching it. Full diagnosis + 2026-05-22 incident: [`references/extended-diagnostics.md`](references/extended-diagnostics.md) §Variant.

#### Step 1.4: Confirm the Homebrew daemon is running as a system service

```bash
sudo brew services list | grep tailscale
```

Expected: `tailscale   started   root   /Library/LaunchDaemons/homebrew.mxcl.tailscale.plist`.

If `started` and `root` are correct, the daemon is already healthy — skip to Step 1.5. If not started:

```bash
sudo brew services start tailscale
```

The `sudo` matters — without it, `tailscaled` runs as your user and lacks the privileges for subnet routing / exit node mode.

#### Step 1.5: Re-authenticate

```bash
tailscale up
```

Follow the auth URL on another device. If the prior config used flags (exit node, subnet routes, etc.), include them — for example:

```bash
sudo tailscale up --advertise-exit-node --advertise-routes=192.168.1.0/24 --accept-routes
```

Re-auth creates a fresh node identity, which is why **the machine's Tailscale IP can change**. Note the new IP — Layer 2 depends on it.

```bash
tailscale status              # confirm: tailnet visible, node "active"
```

#### Step 1.6: Clean up the GUI app (recommended for headless)

For a headless Mac mini, the GUI app is dead weight and risks dropping a broken CLI shim back on future updates:

```bash
sudo rm -rf /Applications/Tailscale.app
sudo rm -f /usr/local/bin/tailscale
# Optional: user-level support files (vary by App Store vs standalone build):
rm -rf ~/Library/Containers/io.tailscale.ipn.macos
rm -rf ~/Library/Group\ Containers/*.io.tailscale.ipn.macsys
rm -rf ~/Library/Application\ Support/Tailscale
rm -rf ~/Library/Preferences/io.tailscale.ipn.macos.plist
rm -rf ~/Library/Caches/io.tailscale.ipn.macos
# Verify nothing GUI-related in LaunchAgents (Homebrew daemon plist must remain):
ls -la /Library/LaunchDaemons/ | grep -i tailscale  # keep homebrew.mxcl.tailscale.plist
ls -la /Library/LaunchAgents/ ~/Library/LaunchAgents/ 2>/dev/null | grep -i tailscale
```

#### Step 1.7: Admin-console cleanup (browser, not CLI)

Visit `https://login.tailscale.com/admin/machines`:

- Delete the old offline node (the one with the original hostname before re-auth).
- Rename the new node back to the clean hostname if you ended up with `<name>-1`.
- Re-approve advertised routes / exit-node status — these need explicit approval per node.

### Layer 2: Mosh-server cleanup (downstream of any Tailscale IP change)

After any Tailscale re-auth or daemon restart that changes the machine's IP, existing `mosh-server` processes are bound to the **old** IP and become unreachable. `tmux` sessions remain alive and untouched — only the mosh-server wrapper needs replacing.

#### Step 2.1: List mosh-servers and their UDP bindings

```bash
ps aux | grep mosh-server | grep -v grep
lsof -nP -iUDP 2>/dev/null | grep mosh
```

The `lsof` output shows each mosh-server's PID and bound IP/port (e.g. `mosh-serv 94933 ... UDP 100.x.y.z:60005`). Compare the bound IPs against the **current** Tailscale IP from `tailscale status` (e.g. `100.x.y.z`). Any mosh-server bound to a different IP is stale.

#### Step 2.2: Verify which tmux sessions correspond to which mosh-servers

```bash
tmux ls
ps -ef | grep mosh-server | grep -v grep   # `mosh-server new ... -- tmux new -s <SESSION>` shows the session each was attached to
```

This lets you confirm a stale mosh-server is the wrapper for a specific tmux session — that session's work is preserved on disk by tmux regardless of mosh-server fate.

#### Step 2.3: Kill stale mosh-servers (preserve the healthy one)

```bash
kill <PID-list-of-stale-servers>
```

Do **not** include any mosh-server whose UDP binding matches the current Tailscale IP. tmux sessions survive.

#### Step 2.4: Verify

```bash
ps aux | grep mosh-server | grep -v grep   # only the healthy ones remain
lsof -nP -iUDP | grep mosh                 # bindings should all show the current IP
tmux ls                                    # sessions unchanged
```

#### Step 2.5: Reconnect from the remote machine

From the client (e.g. MacBook):

```bash
mosh <host> -- tmux a -t <session-name>
```

This spawns a fresh mosh-server bound to the current Tailscale IP and reattaches to the existing tmux session. If `mosh <host>` fails with the canonical-name error, fall back to the resolved hostname directly:

```bash
mosh <my-mini-or-actual-tailscale-name> -- tmux a -t <session-name>
```

## Verification

After Layer 1 + Layer 2:

```bash
# On the Mac mini:
which tailscale                            # /opt/homebrew/bin/tailscale
tailscale status                           # shows tailnet; this node "active"
sudo brew services list | grep tailscale   # tailscale started root
ps aux | grep mosh-server | grep -v grep   # only mosh-servers bound to current IP

# From the client:
mosh <host> -- tmux a -t <session-name>    # connects; tmux session intact
```

## Layer 3 — Downstream references to the (changed) Tailscale IP

**Hostname-first principle:** use MagicDNS hostnames (`my-mini`, `my-vps`) everywhere; never hardcode `100.x.y.z` IPs. After a re-auth changes the IP, grep every peer machine for the OLD IP (health-check scripts, `~/.ssh/config` `HostName` lines, `known_hosts`, monitoring targets) and hostname-ify each hit.

Full Layer 3 protocol — detection greps, per-location fix table, VPS health-check verification — plus three related failure modes (macOS resolver stuck `Not Reachable` after Tailscale restart → `dscacheutil -flushcache` + `killall -HUP mDNSResponder`; RustDesk/VNC relay blocked by MDM → connect via Tailscale direct-IP; `mosh-server: command not found` → Homebrew PATH in `~/.zshenv`), the worked 2026-05-18 example, and edge-case notes: [`references/extended-diagnostics.md`](references/extended-diagnostics.md).

## Anti-Patterns

- **Don't reach for `tailscale up --reset` first.** It resets state on the coordination server, including all advertised routes / exit-node approvals. Use it only when nothing else recovers the daemon.
- **Don't `kill -9` mosh-servers.** A regular `SIGTERM` (`kill PID`) lets them release UDP bindings cleanly. `-9` skips cleanup; the OS will still release the socket but session state files in `/tmp` linger.
- **Don't restart the whole Mac mini to fix this.** Layer 1 + Layer 2 cumulatively take ~3 minutes; a restart adds nothing except risk of losing tmux sessions if anything in them wasn't saved to disk.
- **Don't assume `which tailscale` reflects disk reality.** Always cross-check with `ls -la $(which tailscale)`. The PATH cache mismatch is the specific gotcha this skill flags.
- **Don't remove `/Library/LaunchDaemons/homebrew.mxcl.tailscale.plist`** during GUI-app cleanup. That's the Homebrew daemon's plist — removing it is what you're trying to avoid.
- **Don't apply Layer 1 from a remote SSH session over Tailscale.** The `tailscale down` / `tailscale up` cycle drops your SSH connection. Either work locally on the Mini's console (Screen Sharing over LAN works), or open a backup SSH session via the LAN IP (`ssh user@<mini-LAN-IP>`) before starting.

## Cross-references

### Canonical setup docs (read these first if Layer 1 is unfamiliar)

| Doc | Why |
|---|---|
| [`docs/setup/mac-mini-setup.md`](../../docs/setup/mac-mini-setup.md) | Mac mini setup of record: Homebrew `brew install tailscale` is the canonical install (§ Tailscale Remote Access); also covers headless power/sleep settings (`sudo pmset -a sleep 0 ...`) that make the box stay up without a logged-in user |
| [`docs/setup/terminal-setup/terminal-setup.tex`](../../docs/setup/terminal-setup/terminal-setup.tex) | Full terminal-stack manual including § Mosh for Resilient Connections (UDP ports 60000–61000, SSH-keepalive config to prevent Tailscale NAT idleness), § Non-interactive Shell PATH (the `mosh-server` zshenv gotcha — see Related Failure Mode above), and SSH ProxyCommand pitfalls |
| [`docs/reference/terminal.md`](../../docs/reference/terminal.md) | Quick reference for the terminal stack (iTerm2, zsh, starship, tmux); config locations and which files sync across machines |
| [`docs/guides/tmux-config.md`](../../docs/guides/tmux-config.md) | tmux per-host config; mouse mode is what makes scrollback work through mosh (mosh has no scrollback of its own — tmux underneath holds it) |
| [`docs/setup/vps-setup.md`](../../docs/setup/vps-setup.md), [`docs/setup/claw-setup.md`](../../docs/setup/claw-setup.md) | Sibling host setups; same Homebrew-Tailscale-mosh pattern adapted to Linux VPS |
| [`docs/guides/cross-machine-parity.md`](../../docs/guides/cross-machine-parity.md) | Multi-machine baseline; explains why all four hosts (Mini, UOS, VPS, claw) source `packages/dotfiles/shared.zsh` |
| [`docs/guides/troubleshooting.md`](../../docs/guides/troubleshooting.md) | Generic infrastructure troubleshooting — Tailscale/mosh failures get a pointer here from this skill |

### Related skills

| Skill / Rule | Relationship |
|---|---|
| `multi-machine.md` rule | Defines `mini` / `my-mini` SSH aliases used in examples; mandates relative symlinks across Dropbox; mandates `hostname` check before machine-specific actions |
| `/scheduled-job` | Same launchd patterns (this skill's `sudo brew services start` is a manual variant of what scheduled-job automates for cron tasks) |
| `/session-health` | Different scope — checks current Claude session state, not network/process state |
| `/machine-inventory` | Adjacent — inventories what's installed; this skill recovers from a known failure |

### Origin

Extracted 2026-05-18 from a real diagnostic session — full narrative in [`references/extended-diagnostics.md`](references/extended-diagnostics.md) §Origin.
### Origin

This skill was extracted on 2026-05-18 from a real diagnostic session: the Mac mini's Tailscale GUI app auto-updated, daemon disconnected, headless box couldn't run the GUI daemon, switched to Homebrew/launchd, re-auth gave a new Tailscale IP, existing mosh-servers stranded on the old IP. Original conversation: `~/Library/Mobile Documents/com~apple~CloudDocs/Cloud Downloads/mosh-tailscale.md` (iCloud — TCC-gated; copy to `/tmp/` to read from Claude Code).
