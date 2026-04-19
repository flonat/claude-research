# Knowledge Acquisition Protocol

> Shared reference for review agents. Constructs dynamic external context before the review itself, grounding critiques in verified literature rather than parametric knowledge alone.

## Why This Matters

Review agents operating without real-time literature context critique papers in a "parametric vacuum" — they can only assess novelty, baselines, and literature coverage using training data. This protocol constructs C_dynamic at inference time: a verified, structured knowledge base that sub-agents consume as read-only context files.

**Adapted from:** ScholarPeer (Zhu et al., 2026, arXiv:2601.22638) — multi-agent peer review with dynamic context retrieval.

---

## Architecture

```
Main orchestrator context (has MCP tools + WebSearch)
    │
    ├─ Step 1: Extract paper summary
    ├─ Step 2: Literature Expansion (Paperpile → scholarly MCP → WebSearch)
    ├─ Step 3: Baseline Scout
    ├─ Step 4: Domain Narrative
    └─ Step 5: Handoff — serialize to /tmp/ka-* files
                │
                ▼
        Sub-agents read /tmp/ka-* via Read tool (no MCP needed)
```

**Note on tool access:** Most MCP tools are only available in the main orchestrator context — sub-agents cannot call them. **Exception:** `scholarly` and `paperpile` CLIs work in sub-agents (shell out directly). This protocol still runs in the orchestrator for efficiency, producing files that sub-agents consume.

---

## The KA Protocol (5 Steps)

### Step 1: Paper Summary

Extract from the paper under review (already read during split-PDF or initial reading):

| Field | Source |
|-------|--------|
| `title` | Title page |
| `authors` | Title page |
| `abstract` | Abstract |
| `claimed_contributions` | Introduction — exact claims with page refs |
| `method_name` | Methods section |
| `datasets_used` | Data section — names, sizes, time periods |
| `reported_baselines` | Results/experiments — methods compared against |
| `submission_date` | Stated date, or year of latest cited reference |

The `submission_date` becomes `{cutoff_date}` — all literature searches are constrained to papers published before this date to prevent temporal leakage (citing work that didn't exist when the paper was written).

### Step 2: Literature Expansion

**Goal:** Build a structured literature context of 20-30 relevant papers, prioritising the user's indexed library.

**Priority chain (Paperpile first per bibliography-routing rule):**

| Priority | Tool | Use for |
|----------|------|---------|
| 0 | `search_library` (RefPile MCP) | Search the user's indexed PDFs (~28K papers, full-text vectorized) |
| 0 | `get_paper` (RefPile MCP) | Retrieve full content for known citekeys |
| 1 | `scholarly scholarly-search` | Multi-source broad search (papers NOT in Paperpile) |
| 2 | `scholarly openalex-search-works` | Structured metadata + citation counts |
| 3 | `scholarly dblp-search` | CS venue-specific search |
| 4 | `scholarly scholarly-verify-dois` | Batch DOI verification |
| 5 | WebSearch | Fallback for preprints, blogs, GitHub |

**Why Paperpile first:** It contains full-text content, not just abstracts. When assessing novelty or methodology, having the actual paper content produces richer context than metadata-only results from scholarly APIs.

**Process:**

1. **Paperpile sweep:** Use `search_library` with the paper's research question, method name, and key terms. For each hit, use `get_paper` to retrieve detailed content. Mark these as `in_paperpile: true`.

2. **External sweep:** Use `scholarly scholarly-search` + `scholarly openalex-search-works` for papers NOT found in Paperpile. Target 15-20 additional papers. Constrain to `{cutoff_date}`.

3. **Expansion pass:** Check for gaps:
   - Foundational papers (high-citation seminal works) — present?
   - Temporal gaps (e.g., nothing from 2020-2023 in a 2024 submission)?
   - Direct competitors (same method + same task)?
   - Adjacent fields using different terminology?

4. **Per-paper output format:**

```json
{
  "title": "Paper Title",
  "authors": "Last1, Last2, Last3",
  "venue_year": "ICML 2024",
  "doi": "10.xxxx/xxxxx",
  "core_method": "One-sentence method description",
  "datasets_and_performance": "Dataset X: 85.2% accuracy",
  "is_foundational": false,
  "is_sota_candidate": true,
  "in_paperpile": true,
  "relevance": "Directly competes with reviewed paper's method on benchmark Y"
}
```

5. **Serialize** to `/tmp/ka-literature-{timestamp}.json` (array of paper objects).

### Step 3: Baseline Scout

**Goal:** Identify missing baselines and datasets that weaken the paper's empirical claims.

**Adapted from ScholarPeer's "ferocious benchmarking expert" prompt:** The Baseline Scout is adversarial — its job is to find what the authors are hiding or overlooked.

**Process:**

1. **Identify task and benchmarks** from the paper's experiments section.

2. **Check Paperpile first:** Use `search_library` with task + benchmark keywords. the user may already have SOTA papers for these benchmarks.

3. **External search:** Use `scholarly openalex-search-works` + `scholarly dblp-search` for methods not found in Paperpile. Search for:
   - SOTA methods on the paper's benchmarks (are there stronger baselines?)
   - The paper's method applied to other benchmarks (are they cherry-picking datasets?)
   - Related benchmarks the paper doesn't use (standard in the field but omitted?)

4. **Cross-reference** against the paper's reported baselines. For each:
   - Is the baseline's reported performance correct? (Authors sometimes under-report competitor results.)
   - Is the baseline implementation fair? (Same hyperparameter budget? Same data splits?)

5. **Output format:**

```json
{
  "missing_baselines": [
    {
      "method": "Method Name",
      "reference": "Author et al. (Year)",
      "doi": "10.xxxx/xxxxx",
      "reason": "SOTA on benchmark X as of {cutoff_date}, not compared",
      "in_paperpile": false
    }
  ],
  "missing_datasets": [
    {
      "dataset": "Dataset Name",
      "reason": "Standard benchmark for this task, used by 8/10 related papers",
      "papers_using_it": ["Ref1", "Ref2"]
    }
  ],
  "baseline_concerns": [
    {
      "baseline": "Baseline Name",
      "concern": "Reported accuracy (72.1%) is lower than the original paper's claim (74.3%)"
    }
  ]
}
```

6. **Serialize** to `/tmp/ka-baselines-{timestamp}.json`.

### Step 4: Domain Narrative

**Goal:** Synthesise a ~300-word narrative that positions the reviewed paper within its research arc.

**Adapted from ScholarPeer's Sub-Domain Historian Agent.**

**Process:**

1. Organise papers from Step 2 chronologically.
2. Write three sections:

   **Arc of Progress:** What were the key milestones? How did the field evolve from early approaches to current SOTA? (100 words)

   **Open Problems:** What remains unsolved? Where is the field heading? (100 words)

   **Positioning:** Where does this paper sit in the arc? Is it pushing the frontier, filling a gap, or revisiting solved problems? (100 words)

3. **Serialize** to `/tmp/ka-narrative-{timestamp}.md`.

### Step 5: Handoff

Report to the user:

> "KA complete: found N papers (M from Paperpile), K missing baselines, J missing datasets. Files written to `/tmp/ka-literature-*.json`, `/tmp/ka-baselines-*.json`, `/tmp/ka-narrative-*.md`. Proceeding to sub-agents."

All `/tmp/ka-*` files are now available for sub-agents to read via the Read tool.

---

## Integration Points

### peer-reviewer (Phase 1.5)

Runs between Phase 1 (Split-PDF Reading) and Phase 2 (Sub-Agent Deployment). The orchestrator executes all 5 KA steps, then passes file paths to sub-agents in their prompts.

### referee2-reviewer (Step 0.5)

Runs before the 6 audits begin. KA outputs feed into Audit 5 (Methods — missing baselines) and Audit 6 (Novelty & Literature — full context).

### paper-critic (Context Files)

Paper-critic has no MCP access (Read/Glob/Grep only). The **main session** runs KA before spawning paper-critic, then passes `/tmp/ka-*` file paths in the agent prompt. Paper-critic reads these files to enrich checks 4 (Literature & Citations) and 7 (Novelty & Contribution).

---

## Graceful Degradation

Reference: `skills/shared/mcp-degradation.md`

If MCP tools are unavailable:

| Unavailable | Fallback | Impact |
|-------------|----------|--------|
| RefPile MCP | Skip Paperpile sweep; proceed with scholarly MCP | Lose full-text library context |
| Scholarly MCP | Use WebSearch for all literature queries | Lose structured metadata, citation counts |
| Both RefPile + Scholarly | WebSearch-only mode | Significantly reduced context quality |

When operating in degraded mode, flag reduced confidence prominently:

> "**KA degraded mode:** [unavailable tools]. Literature context is based on [available tools] only. Novelty and baseline assessments should be treated as preliminary."

---

## When to Skip KA

- **Short informal reviews** — quick feedback on early drafts where deep literature grounding isn't needed
- **Code-only reviews** — referee2-reviewer auditing code, not a paper
- **Repeat reviews (R&R)** — the literature context from Round 1 is still valid; only re-run if the author substantially changed their positioning
- **User says "skip KA"** — respect explicit opt-out

When KA is skipped, sub-agents operate as before (no regression). The absence of `/tmp/ka-*` files is the signal — sub-agents check for their existence and proceed without them if absent.
