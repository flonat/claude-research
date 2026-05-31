# Literature & Discovery — Phase 9 Details

> Referenced from: `init-project-research/SKILL.md` Phase 9


## Known failure mode (incident 2026-05-31)

**Sub-agent dispatch for `/literature` and  regularly returns without writing files** because sub-agents launched via the `Agent` tool do not inherit the parent session's Bash permissions, and the underlying skills shell out to paperpile / scholarly / refpile / scout CLIs. One failure mode is honest ("I need Bash permission"); a worse one is **hallucinated success** — the sub-agent claims files exist that were never written. See `log/incidents/2026-05-31_subagent-bash-failure-and-hallucinated-success.md`.

**Default execution model:** run `/literature` and  **in the main session context**, not as sub-agents. The main session has all the perms the user granted to the project.

If you do dispatch as sub-agents (e.g. for parallelism on a long deep-pull):

1. Apply the failure-mode contract from `rules/subagent-prompt-discipline.md` § Failure-mode contract — the sub-agent prompt MUST require honest failure reporting.
2. After each sub-agent returns, `ls` every claimed output path. If any file is missing, treat the dispatch as failed and fall back to main-context execution. Do NOT trust the sub-agent's summary.
3. Time-box at ~5 minutes; if the sub-agent has not produced the expected files by then, fall back.

## 9a. Literature Review

Launch `/literature` targeting the project's research topic. Uses the working title, abstract, key research questions, and any references from the Atlas topic file as search seeds.

1. Spawn a sub-agent (`Task` tool) that runs the literature skill:
   - Search query: derived from the working title + key concepts from the interview
   - Sources: OpenAlex + Scopus (or multi-source if available)
   - Output: `docs/literature-review/YYYY-MM-DD-initial-review.md` — structured literature map with verified citations
   - Also generate: `docs/literature-review/references.bib` — verified BibTeX entries for discovered papers
2. Scope: foundational papers + recent work (last 3 years) + closest competitors
3. Target: 15-25 papers for an initial literature map

## 9b. Scout Discovery Audit

Launch  in novelty mode to assess the topic's competitive landscape.

```bash
scout novelty "<working-title-or-research-question>" --source multi
```

1. Save the scout report to `docs/YYYY-MM-DD-scout-novelty.md`
2. If the novelty score is **below 5/10**, flag in the confirmation report: "Low novelty score — consider reframing before investing further"
3. If the novelty score is **above 7/10**, note as a positive signal

## 9c. Results Integration

After both complete:

1. Update the Atlas topic file's `## Key References` section with the top 5-8 foundational papers discovered
2. Add the novelty score to the Atlas topic file: `## Novelty Assessment\n\n**Score: X/10** (scouted YYYY-MM-DD). [one-line summary]`
3. If scout identifies specific competitors, add them to `## Key References` with differentiation notes

## Error Handling

- If literature search returns no results: note in report, continue (topic may be too novel or too niche for API coverage)
- These phases should NOT block project creation — if they fail, the project is still fully scaffolded
