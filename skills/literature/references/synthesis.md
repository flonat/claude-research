# Literature — Phase 7: Synthesize Narrative

> Direct or CLI council. Produces thematic narrative, structured gaps, and priority reading list.

## Synthesis Steps

1. **Identify themes** — group papers by approach, finding, or debate
2. **Map intellectual lineage** — how did thinking evolve?
3. **Note current debates** — where do researchers disagree?
4. **Structured gap analysis** — decompose gaps into three categories (do not collapse into a generic "more research needed"):
   - **Methodological gaps** — weak designs, underpowered samples, definition inconsistencies, only observational where experiments are feasible
   - **Population/context gaps** — who or what hasn't been studied (e.g., non-Western samples, specific sectors, field vs lab conditions)
   - **Conceptual/theoretical gaps** — unreconciled contradictions, proposed but untested mechanisms, adjacent fields not integrated
   For each gap, state **why it matters** — not "X hasn't been studied" but "X hasn't been studied, which means we don't know whether [implication]."
5. **Negative evidence** — per cluster, include ≥1 null finding, failed replication, or measurement critique when such work exists. If none exists for a cluster, state this explicitly: "No null or replication evidence found for [cluster]." This is mandatory, not optional — negative evidence is as important as positive evidence for positioning a project.
6. **Cross-cluster synthesis** — after all clusters, write 1-2 paragraphs identifying: (a) how clusters connect or depend on each other; (b) tensions between clusters (e.g., theory in Cluster 1 predicts X, but empirical work in Cluster 3 finds the opposite); (c) what the combined landscape implies for the user's project. Do not just list clusters in isolation.
7. **Priority Reading Order (5–7 papers)** — curate a sequenced reading list for a newcomer. Ordering logic: (i) best recent review or meta-analysis first (broadest orientation, least effort); (ii) foundational/seminal paper(s); (iii) 2–3 current-frontier papers; (iv) end with a paper that surfaces a key gap or controversy. For each entry include: (a) clickable link or DOI, (b) one sentence on what it contributes in this sequence, (c) one sentence on what to pay attention to while reading (e.g., "Table 3 compares effect sizes across RCTs", "discussion maps unresolved debates"). This is the most actionable artefact for a researcher entering a new field — treat it as mandatory, not optional.

Output types: narrative summary (LaTeX), literature deck, annotated bibliography, concise field synthesis.

**After deep loop (Phase 4.5):** If the deep loop ran, include an explicit "Remaining Gaps" section in the synthesis — document what couldn't be found and suggest manual search strategies. This turns gaps into actionable next steps rather than hiding them.

## Concise Field Synthesis (~400 words)

When the user asks for a "quick synthesis", "field overview", or "what does the literature say", produce a tight ~400-word synthesis instead of a full narrative. No paper-by-paper summaries — write about the field, not individual papers.

Structure:

1. **What the field collectively believes** — established consensus (2-3 sentences)
2. **Where researchers disagree** — active debates with camps identified (2-3 sentences)
3. **What has been proven** — findings with strong, replicated evidence (2-3 sentences)
4. **The single most important unanswered question** — one question, why it matters, why it's hard (2-3 sentences)

Cite papers parenthetically (Author, Year) but never summarise individual papers. The goal is a helicopter view that a newcomer could read in 2 minutes and understand where the field stands.

## [VERIFY] Citation Tags

When synthesising, mark uncertain attributions with `[VERIFY]` tags for later resolution:

```markdown
Meraz and Papacharissi (2013) argue that gatekeeping power shifted
from institutional positions to network centrality [VERIFY: exact claim on p. 12?].
```

- **Drafting tier:** [VERIFY] tags are acceptable — resolve before finalising
- **Publication tier:** All [VERIFY] tags must be resolved (read the actual source)
- Run `/bib-validate` to catch any remaining [VERIFY] tags before submission

## Multi-Model Synthesis (Optional)

For comprehensive literature reviews, run the synthesis through `cli-council` to get three independent interpretations of the literature landscape. Different models identify different themes, debates, and gaps.

```bash
cd "packages/cli-council"
uv run python -m cli_council \
    --prompt-file /tmp/lit-synthesis-prompt.txt \
    --context-file /tmp/lit-papers.txt \
    --output-md /tmp/lit-synthesis-report.md \
    --chairman claude \
    --timeout 180
```

Where `--context-file` contains the verified paper list with titles, abstracts, and metadata, and the prompt asks for thematic grouping, intellectual lineage, and gap identification. The chairman synthesises three independent narratives into one.

## `literature_summary.md` Structure

The narrative output must include:

1. **Priority Reading Order** — curated 5–7 paper sequence per step 7 above (best review → foundational → frontier → controversy/gap). Each entry: link, "contributes because…", "pay attention to…". Place near the top of the document — this is the newcomer's launching pad.
2. **Thematic clusters** — grouped by approach, finding, or debate (typically 4-8 clusters)
3. **Per cluster:** intellectual lineage, current debates, negative/null evidence (or explicit statement that none exists)
4. **Cross-cluster synthesis** — 1-2 paragraphs on how clusters connect, where tensions exist, and implications for the project
5. **Structured gaps** — methodological / population-context / conceptual-theoretical (per step 4 above), each with a "why it matters" line
6. **Annotated bibliography** — each entry includes: confidence grade (A/B/C), pillar tag (Substantive/Empirical/Methodological), connection note linking to ≥1 other entry, WP criteria if applicable, and SciSciNet metrics if Phase 3b ran (disruption/novelty scores, hit flags)
7. **Confidence breakdown** — summary count of A/B/C grades across all entries
8. **Coverage gaps** — what was searched for but not found, and where negative evidence is absent
9. **SciSciNet summary** (if Phase 3b ran) — match rate, distribution of disruption/novelty scores across the corpus, notable hit-1% papers, and cross-field connections flagged during enrichment

## Output File Structure

```
project/
├── docs/
│   ├── literature-review/
│   │   ├── literature_summary.md      # Thematic narrative (always)
│   │   └── literature_summary.bib     # Standalone .bib (always)
│   └── readings/
│       ├── Smith2024.pdf              # Downloaded PDFs
│       └── ...
└── paper/
    └── references.bib                  # Canonical bib (merge if exists)
```
