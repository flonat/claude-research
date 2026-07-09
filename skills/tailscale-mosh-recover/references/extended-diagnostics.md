# Tailscale + Mosh Recovery — Extended Diagnostics

> Reference companion to [`../SKILL.md`](../SKILL.md). The skill carries the core Layer 1 (Tailscale daemon) + Layer 2 (mosh cleanup) procedure; this file carries the variant fixes, downstream Layer 3, related failure modes, the worked example, and edge-case notes.

## Variant: orphan-after-autoremove (Layer 1, Step 1.3)

**Symptom:** `which tailscale` returns nothing; `brew uninstall <something-else>` (commonly a cask) just ran and triggered an autoremove that reported `Autoremoving 1 unneeded formula: tailscale`. The CLI symlink is gone but `/opt/homebrew/Cellar/tailscale/<older-version>/` may still exist on disk from a previous install — and `tailscaled` is still running because Unix processes keep file handles to the unlinked binary.

This happens when a cask (e.g., `chromium` before its 2026-05-22 deprecation) declares tailscale as a build dependency. When the cask gets uninstalled, brew autoremoves the dependency, but the running daemon doesn't notice and peer connections stay up.

**Diagnosis:**
```bash
which tailscale                                    # empty
ls /opt/homebrew/Cellar/tailscale/                 # shows older version still cached
ps aux | grep tailscaled | grep -v grep            # daemon still running
```

**Fix:**
```bash
brew link --overwrite tailscale                    # relink the cached older version
which tailscale                                    # confirm symlink restored
tailscale status                                   # confirm peers reachable
```

The `--overwrite` is needed because `brew link` would otherwise complain about phantom conflicts from the autoremoved keg's leftover state. No daemon restart is required — the running `tailscaled` keeps its config and connections; only the user-facing CLI shim needed to be re-created.

Historical incident: 2026-05-22 on Mac Mini. `brew uninstall --cask chromium` (chromium cask was deprecated, failed Gatekeeper signature check) triggered autoremove of tailscale 1.98.3 as an "unneeded formula". 1.96.4 was still on disk from an earlier install; `brew link --overwrite tailscale` restored CLI access without touching the daemon. Optional follow-up: `brew upgrade tailscale` to get back to 1.98.3 (not urgent — 1.96.4 works fine).

**Prevention:** add tailscale to `Brewfile` (or whatever your brew-package-tracking convention is) as an explicit dependency so future autoremoves leave it alone. Today's session has no Brewfile so the manual relink is the standing fix.


## Example

Real session (2026-05-18):

1. Mac mini `my-mini`: Tailscale GUI app auto-updated → daemon disconnected, CLI symlink dropped from `/opt/homebrew/bin/tailscale`.
2. Headless box, no menu-bar available → switch to Homebrew/launchd path. `sudo rm /usr/local/bin/tailscale` (GUI shim), `brew link tailscale`, `sudo brew services start tailscale` (already started under root). `tailscale up` → re-auth → node re-registered as `my-mini-1` with new IP `100.x.y.z` (was `100.x.y.z`).
3. 30 minutes later: `mosh mini -- tmux a -t myproject` from MacBook → `could not get canonical name for mini`.
4. Diagnostic: `ps aux | grep mosh-server` shows 4 processes; `lsof -iUDP | grep mosh` shows 3 of them bound to the OLD IP `100.x.y.z`. The one on the new `100.x.y.z` is the only healthy survivor.
5. `kill 94933 43357 8510` → stale ones gone. tmux sessions (`myproject`, `proj-b`, `TM`, `course-a`) all still showing in `tmux ls`.
6. From MacBook: `mosh mini -- tmux a -t myproject` → fresh mosh-server bound to `100.x.y.z`, reattaches to the existing tmux session, work resumed where it left off.

Total recovery time once root cause identified: ~3 minutes.

## Notes / Edge cases

- **Headless vs desktop Mac.** This skill assumes headless (no logged-in user). On a desktop Mac with the GUI app and a user session, the GUI app's daemon works fine and you don't need the Homebrew route at all. Don't apply Layer 1's GUI-app removal on desktop Macs.
- **mosh-server idle timeout.** Default is 7 days of no input. Stale mosh-servers from old Tailscale IPs are otherwise harmless and self-clean within a week — but they hold tmux sessions in `attached` state, which can confuse subsequent client reconnections.
- **tmux is independent of mosh.** Killing `mosh-server` never kills tmux. The two have no parent-child relationship; mosh-server's `-- tmux a -t <session>` argument is what tmux client to spawn when the mosh client first connects, not a process tree.
- **Subnet routes / exit node need re-approval.** After re-auth (Step 1.5), the new node has no approvals. Visit the admin console and re-enable everything the prior node had advertised. The CLI flags from the prior `tailscale up` are reused, but the admin-side approval state is per-node.
- **MagicDNS hostname dedup.** Tailscale appends `-1`, `-2`, etc. on hostname collisions. If you don't clean up the old node from the admin console, the new node keeps the `-N` suffix and any DNS / ACL / exit-node references to the original name will resolve to the dead node.
- **When `which tailscale` lies.** Shell PATH cache (zsh, bash) can keep returning a path long after the file is gone. `hash -r` clears the cache. The discrepancy (`which X` succeeds, `ls X` fails) is diagnostic on its own.
- **One-Tailscale-only.** Don't run both the GUI app's daemon AND `sudo brew services start tailscale` simultaneously — they fight over the local socket and ports. Pick one per machine.

## Layer 3 — Downstream references to the (changed) Tailscale IP

**Principle (hostname-first).** Use Tailscale MagicDNS hostnames (`my-mini`, `my-vps`, etc.) everywhere — **never** hardcode `100.x.y.z` IPs in scripts, SSH configs, cron jobs, monitoring rules, etc. Re-auth can change the IP at any time; hostnames are stable. The IP is implementation detail.

After Layer 1's re-auth (Step 1.5), grep for hardcoded references to the **old** Tailscale IP across all machines that talk to this one. Common offenders that have bitten this stack (2026-05-18 incident):

| Location | What to look for | Fix |
|---|---|---|
| VPS `/opt/example/health-check/check-mini.sh` (and any sibling cron scripts on peer machines) | `MINI_IP="100.x.y.z"` or any `100.\d+\.\d+\.\d+` literal | Drop the variable; use `$MINI_NAME` (hostname) for both `ping` and `ssh` — MagicDNS resolves it |
| VPS `/root/.ssh/config` (or `~/.ssh/config` on any peer) | `Host my-mini` with `HostName 100.x.y.z` | Delete the `HostName` line — `Host my-mini` alone is enough; MagicDNS resolves the bare alias |
| `~/.ssh/known_hosts` on every peer that's connected before | Old-IP entries keyed by the prior `100.x.y.z` | `ssh-keygen -R <old-ip> -f ~/.ssh/known_hosts`. Add `-o StrictHostKeyChecking=accept-new` to non-interactive (cron) SSH commands so the first connect to the new IP is accepted automatically without a TTY prompt |
| Monitoring config (Prometheus targets, Caddy reverse proxy upstreams, etc.) | Hardcoded `100.x.y.z` in target lists / upstream blocks | Replace with hostname; verify the monitoring host has Tailscale + MagicDNS |
| Documentation (`docs/setup/*.md`, runbooks) | Same hardcoded IP in prose / examples | Update to hostname-only examples |

### Detection grep

Run from **each peer machine** (not the just-re-auth'd Mac mini):

```bash
# Replace 100.x.y.z with whatever the OLD Mini Tailscale IP was
grep -rln '100\.118\.194\.31' /opt/example /etc /root ~ 2>/dev/null

# On Task-Management:
grep -rln '100\.118\.194\.31' ~/Task-Management/scripts ~/Task-Management/docs 2>/dev/null
```

If grep returns hits, each one is either:
- A stale reference that needs hostname-ification (this Layer fixes it)
- A historical example/log entry that's fine to leave (prose documenting incidents)

### Verification

After Layer 3 changes on the VPS-side health-check:

```bash
ssh root@<vps-ip> "bash /opt/example/health-check/check-mini.sh && tail -1 /opt/example/health-check/mini-health.log"
# Expect: "<YYYY-MM-DD HH:MM:SS> OK"
```

If `DEGRADED (ping OK, SSH fail)` after this fix, check `known_hosts` on the peer — old-IP entries cause SSH host-key mismatch even when MagicDNS resolves correctly. Clean with `ssh-keygen -R <old-ip>`.

### Why MagicDNS isn't always trusted by default

Some peers have `Use Tailscale DNS: enabled` but show empty MagicDNS configuration (`tailscale dns status`). Common reasons:
- Tailnet doesn't have MagicDNS enabled in the admin console
- A custom DNS resolver is overriding Tailscale's DNS handler
- macOS `mDNSResponder` is caching old answers

Quick check on each peer: `tailscale ip <hostname>` should return an IP. If yes, MagicDNS is functional even if `nslookup <hostname>` fails — SSH's `Host` alias resolution will use Tailscale's resolver directly when `HostName` is absent.

### Related: macOS resolver stuck in "Not Reachable" after Tailscale restart

Symptom: `tailscale dns status` says MagicDNS is enabled, `dig @100.100.100.100 <host>.<tailnet>.ts.net` resolves correctly, but `ssh <host>` returns `nodename nor servname provided`. `scutil --dns` shows the Tailscale search domain with `reach: 0x00000000 (Not Reachable)`.

Cause: macOS's `mDNSResponder` cached the pre-restart resolver state. The Tailscale resolver is reachable (ping 100.100.100.100 works, dig direct works), but the system resolver bypasses it because the reachability flag is stuck false.

Fix (requires sudo):

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

This flushes the DNS cache and reloads the resolver. `tailscale set --accept-dns=false && tailscale set --accept-dns=true` does NOT fix it on its own (verified 2026-05-18 — the scutil reach flag stays stuck through the accept-dns flip).

As a durable workaround if you can't reliably flush, write Tailscale FQDNs into `~/.ssh/config` rather than bare names:

```ssh-config
Host uos
    HostName my-laptop.<tailnet>.ts.net   # full tailnet FQDN — resolves even when bare-hostname routing is stuck
```

The tailnet suffix is shown by `tailscale dns status` under "MagicDNS: enabled tailnet-wide (suffix = ...)".

## Related: Remote-access fallback via Tailscale direct-IP (RustDesk, VNC, etc.)

**Symptom.** Remote-desktop tool fails to connect via its canonical relay/rendezvous server, typically with a connection-refused or "please try later" error. Example: RustDesk client on an MDM-managed MacBook returns `Failed to connect to rs-ny.rustdesk.com:21116: Please try later`, while the same RustDesk server on the Mac mini is healthy (process running, registered with the relay at 20-30ms ping).

**Cause.** Corporate / institutional firewalls and MDM profiles often block outbound traffic to non-standard ports (RustDesk uses 21116/21118, AnyDesk uses 6568, TeamViewer uses 5938). The server side is fine; the *client* network just can't reach the public rendezvous server.

**Fix — bypass the relay via Tailscale direct-IP.** Most remote-access tools accept an IP or hostname in their connect field as a "direct mode" instead of their canonical 9-digit / GUID ID.

| Tool | Field | What to enter |
|---|---|---|
| RustDesk | Main "Control Remote Desktop" ID field | `<mini-tailscale-ip>` (or `<ip>:21118` if port prompt appears) |
| VNC (built-in macOS Screen Sharing) | `vnc://<host>:5900` | `vnc://<mini-tailscale-ip>` |
| AnyDesk | Address field | `<mini-tailscale-ip>` |
| TigerVNC / RealVNC | Server address | `<mini-tailscale-ip>:5900` |

Get the Tailscale IP with `tailscale ip my-mini` on the connecting machine, or `tailscale status` and read the `100.x.y.z` for the target host. **Prefer hostname over IP** wherever the client accepts it (`my-mini` or the FQDN `my-mini.<tailnet>.ts.net`), per the hostname-first principle in Layer 3.

**Prerequisite.** The server-side tool must have direct-IP access enabled and the port must be listening on the Tailscale interface. For RustDesk on the Mini, confirm from a shell:

```bash
lsof -i :21118 -P -n | grep RustDesk
# Expect: TCP *:21118 (LISTEN)
```

If the listening line isn't there, enable it in the RustDesk UI: Settings → Security → "Enable Direct IP Access".

**Why this works.** Tailscale gives you a direct WireGuard mesh between your devices. Once the listening port is reachable on the server-side Tailscale IP, the client connects peer-to-peer regardless of what the public relay is doing. As a bonus: lower latency (no NY round-trip), no MDM interference, no dependence on the vendor's infrastructure.

**Why this belongs in this skill.** Same hostname-first principle as Layer 3 (the Tailscale mesh is the canonical durable path between the user's machines), and the same machines are involved — the fallback is "skip whatever broken middlebox the tool was trying to use, go direct via the mesh you already have working".

## Related failure mode: `mosh-server: command not found`

Different symptom, same `mosh mini` family of problems. From the client:

```
mosh mini
zsh:1: command not found: mosh-server
```

**Cause:** mosh runs `mosh-server` on the remote via a **non-interactive, non-login** zsh invocation. That shell sources `~/.zshenv` but NOT `~/.zshrc`. If Homebrew's PATH is only in `~/.zshrc` (the common default), mosh's remote invocation can't find `/opt/homebrew/bin/mosh-server`.

**Fix:** ensure `~/.zshenv` on the remote (Mac mini) exports the Homebrew PATH:

```bash
# In ~/.zshenv on the Mac mini:
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"
```

**Stopgap** (if you can't edit zshenv right now):

```bash
mosh --server=/opt/homebrew/bin/mosh-server mini -- tmux a -t <session>
```

Canonical reference: [`docs/setup/terminal-setup/terminal-setup.tex`](../../docs/setup/terminal-setup/terminal-setup.tex) § Mosh for Resilient Connections → Non-interactive Shell PATH.

### Origin

This skill was extracted on 2026-05-18 from a real diagnostic session: the Mac mini's Tailscale GUI app auto-updated, daemon disconnected, headless box couldn't run the GUI daemon, switched to Homebrew/launchd, re-auth gave a new Tailscale IP, existing mosh-servers stranded on the old IP. Original conversation: `~/Library/Mobile Documents/com~apple~CloudDocs/Cloud Downloads/mosh-tailscale.md` (iCloud — TCC-gated; copy to `/tmp/` to read from Claude Code).
