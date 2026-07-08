# Design Notes

- **Zero questions except git.** All applicable actions run automatically. The only interaction is the commit/push decision.
- **Auto-detection replaces manual routing.** Previously split into `/general-session-recap` and `/research-session-recap` -- now a single skill that detects project type and applies the right protocol.
- **Parallel agents** for independent actions. Focus, docs, vault, and session log don't depend on each other.
- **Memory is automatic but visible.** Always saved (it's never destructive), but shown for review in Phase 2.5 so you can veto or adjust before git commit.
- **Git is always last.** It captures all file changes from the parallel agents.
- **Check, don't sync blindly.** The drift checks in Phase 1.5 *report* mismatches. The *fixes* are optional actions in the interview. This avoids silent overwrites.
- **Atlas is the source of truth for outputs.** Local `paper*` dirs and vault submission entries should match what the atlas topic file declares. If they diverge, the atlas gets updated first, then vault submissions follow.
- This skill replaces the old stop-reminder hook (deleted -- it was too noisy). `/session-close` is **opt-in** -- the user invokes it when ready.
