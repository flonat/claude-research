# Scott Cunningham — Multi-Analyst Agent Designs & Non-Standard Errors

> Source: Substack posts 21, 25, 26, 27 (Feb–Mar 2026). Series on Claude Code for causal inference.

## Post 26: Computational Many-Analysts Design (DiD Part 2)

### Core Idea

Run N independent AI agents on the same dataset + estimator, isolating each in a temp directory with no shared memory. This approximates a many-analysts design (Silberzahn et al. 2018, Huntington-Klein et al. 2021, Menkveld et al. 2024 "non-standard errors") at near-zero marginal cost.

### Experiment

- 15 agents × 5 packages (csdid, csdid2, did, differences, diff-diff) × 3 languages
- Each launched via `claude -p` in isolated temp dirs, no shared history
- Instructions: Callaway & Sant'Anna estimator, universal base period, not-yet-treated controls
- **Primary discretionary node:** covariate selection for conditional parallel trends

### Key Findings

- **Structural decisions unanimous (15/15):** control group, base period, balanced cohorts, trimming
- **All variation in covariate selection:** log GDP (14/15), population (12/15), poverty (10/15), health spending (7/15), Bolsa Familia (2/15), geographic vars (1/15)
- Agents drew the confounder/mediator boundary differently — same reasoning, different thresholds
- All 15 chose doubly robust; Stata agents split on DRIPW vs DRIMP variant

### Relevance

- Demonstrates that agent-based many-analysts designs are feasible and cheap
- Covariate selection as the key discretionary node in DiD — directly measurable
- Forest plots of agent estimates could become a standard robustness diagnostic
- The spread across agents quantifies researcher degrees of freedom computationally

## Post 21: Attention, Verification, and Convex Costs

### Framework

Isoquants for cognitive work have flattened → human time ≈ machine time for many tasks → rational substitution toward cheaper machine time → reduced human attention despite more output.

### Key Claims

1. **5x productivity, >5x mess.** "Stock pollutants" (excess files, duplicate outputs, hard-coded results, branching pipelines) grow convex in productivity, not linearly.
2. **Three binding constraints in human-AI research:**
   - Human verification (Karpathy: "the new skill is verification")
   - Sustained attention (resist automation of the learning process itself)
   - Congestion management (finding things in your own output)
3. **Legacy projects are harder.** New projects scaffold cleanly; revived R&Rs become "Frankenstein hodge-podge" of old and new organisation.

### Relevance

- Empirical account of human-AI collaboration friction from a power user
- The convex cost function is testable: does error rate grow faster than output rate?
- "Beautiful decks" as attention maintenance strategy — works at low volume, breaks at scale
- Directly maps to the user's research themes (human-AI collaboration, org behaviour)

## Post 25: OpenClaw Security & Anthropic's Response

### What Happened

OpenClaw (always-on WhatsApp AI agent, 230K GitHub stars) had critical security failures:
- No authentication by default; ~1000 open installations found via Shodan
- Prompt injection: embedded instructions in emails forwarded data to attackers
- 230+ malicious plugins in one week on unmoderated skill marketplace
- Cisco found a #1-ranked skill that was literal malware (curl exfiltration)

### Anthropic's Response

- Cowork (scheduled tasks) and Remote Control (phone → local machine)
- Key architectural differences: no inbound ports, short-lived credentials, sandboxed, TLS encryption
- Trade-off: more constrained but safer; computer must be awake for Cowork

### Relevance

- Case study in safety norms emerging in AI agent ecosystems
- The semantic attack surface (prompt = attack vector) vs traditional code exploits
- Anthropic's "safety as brand equity" thesis — early safety investment paying off in agent era

## Post 27: Research vs Publishing Economics

### Core Argument

AI collapses the cost of producing submission-quality manuscripts → 5x submissions → acceptance rates crater → journals earn windfall fees → referee system breaks → prisoner's dilemma.

### Numbers

- ~12,000 research-active economists, ~39,000 submissions/year currently
- At 5x: top-5 acceptance drops from 5% to 1%; 87 journals go from $6.2M to $31M in fees
- Referee need: 146K reports/year against ~54K realistic supply
- Individual cost of 3x scaling: ~$3,200/year (fees + Claude Max)

### Project APE (Zurich Social Catalyst Lab)

- 204 fully automated econ papers; 60 added in one week
- 4.7% win rate vs AER-equivalent in head-to-head, improving to 7.6% in latest cohort
- Goal: 1,000 papers

### Cunningham's Own Test

Fully automated a paper end-to-end: idea generation → shift-share IV → web data → analysis → writing → refine.ink review ($40-50) → revision → referee2 audit → cross-language code audit. Total: ~$100, few hours.

### Relevance

- The "binding constraint shifts from production to evaluation" thesis
- 75 working papers on a website = "lottery player" signal, not "serious researcher"
- Refine.ink as a verification service that gets paid multiple times per paper (polishing → submission → desk screen → R&R)
- For the user: the institutional response to auto-generated research volume is a research topic in itself (org behaviour, mechanism design)
