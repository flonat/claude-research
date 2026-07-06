# Reference Manager Cross-Reference

> Referenced from: `bib-validate/SKILL.md`

After the disk-based cross-reference, check every `.bib` key against the Paperpile library. Produces a status table (HEALTHY / DRIFT / SUGGESTED / AMBIGUOUS / NOT_FOUND).

## Primary method: local resolver (fast, no CLI spawns)

Run ONE command — the canonical resolver in Task-Management:

```bash
python3 "$(cat ~/.config/task-mgmt/path)/scripts/bib/rekey_to_canonical.py" <project.bib> [tex_path ...]
```

It matches all entries against the local library backup JSON (`PAPERPILE_MCP_LIBRARY_PATH`, ~5s for a 40-entry bib against 30k items) via DOI → exact-title → fuzzy-title(+author/year) → surname+year fallback, and prints the full status table plus how many `\cite` keys each `.tex` would need remapped. Dry-run by default — safe to run during validation.

**Do NOT loop `paperpile search-library` per key, and do NOT dispatch lookup sub-agents for library membership.** The 2026-07-02 weber-fechner-mcda incident: per-key CLI searches via 3 parallel sub-agents were slow (uv startup contention, one batch took 17 min) and one sub-agent fabricated 13 "not found" results. The resolver replaced all of it with one 5-second command and independently reproduced the correct mapping.

## Fallback: per-key CLI lookup

Only for entries the resolver leaves `SUGGESTED` / `AMBIGUOUS` / `NOT_FOUND` (typically retitled working papers), confirm individually:

1. `paperpile lookup-by-doi "<doi>"` if a DOI exists
2. `paperpile search-library "<title or author year distinctive-words>"`
3. Confirmed matches feed back as `--extra-map OLD=NEW` on the resolver's apply step

**Additional checks (unchanged):**
- Call `paperpile get-labels` to verify label organisation matches project themes
- For projects with a known Paperpile label, call `paperpile get-items-by-label` to find papers in the label but not cited (potential missing citations)

## Status Categories

| Resolver status | Meaning | Report |
|------|-----------|--------|
| `HEALTHY` | key exists in library as-is | `✓ In sync` |
| `DRIFT` | same paper in library under a DIFFERENT citekey (locally-minted lookalike) | `⚠ Rekey to canonical (fix mode: resolver --apply → rebuild → lint)` |
| `SUGGESTED` | surname+year match with reworked title — needs human confirm | `? Confirm via --extra-map` |
| `AMBIGUOUS` | multiple library candidates | `? Confirm via --extra-map` |
| `NOT_FOUND` | genuinely absent from library | `✗ Stage for Paperpile import in Fix Mode` |

Include this as a "Reference Manager Sync" section in the report, after cross-reference results and before quality checks.

**Staleness caveat:** the backup JSON lags the live library (check its mtime). A key present in the JSON may have been deleted or merged in the Paperpile UI since — if the user reports a key missing that the resolver shows present, trust the user and remap via `--extra-map` (2026-07-02: `Haidinger2026-hc` was in the stale JSON but gone from live Paperpile).

**Graceful degradation:** if the backup JSON is missing, fall back to the `paperpile` CLI — batch membership into ONE `paperpile export-bib --citekeys k1,k2,...` call (never per-key searches). If the CLI is also unavailable, skip with a warning and continue with disk-only validation.
