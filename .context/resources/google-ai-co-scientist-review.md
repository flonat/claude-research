# Paper Note: Towards an AI Co-Scientist (Google, Feb 2025)

> arXiv 2502.18864 | 81 pages | Saved at `to-sort/downloads/2502.18864-ai-co-scientist.pdf`

## Summary

Multi-agent system built on Gemini 2.0 for scientific hypothesis generation and refinement. Six specialized agents (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review) orchestrated by a Supervisor agent. Applied to three biomedical domains with wet-lab validation.

## Architecture

- **Generation agent**: Literature search, simulated scientific debates (self-play), iterative assumption identification, research expansion
- **Reflection agent**: Multi-tier review (initial safety screen, full literature-grounded review, deep verification, observational review, recontextualized tournament review)
- **Ranking agent**: Pairwise tournament using Elo ratings. Evaluates on alignment, plausibility, novelty, testability, safety
- **Proximity agent**: Builds similarity graph over hypotheses for clustering and gap identification
- **Evolution agent**: Refines top-ranked hypotheses via enhancement, feasibility improvement, combination, simplification, out-of-box thinking
- **Meta-review agent**: Synthesizes patterns across all reviews, provides feedback to other agents' prompts (learning without backpropagation)

Key design: tournament-based evolution with Elo ratings replaces "pick best from list" with a scalable ranking mechanism. More compute = monotonically better results (test-time compute scaling).

## Key Results

| Metric | Result |
|--------|--------|
| GPQA diamond accuracy (top-1) | 78.4% |
| Expert preference ranking | 2.36/4 (best among all systems) |
| Expert novelty rating | 3.64/5 |
| Expert impact rating | 3.09/5 |
| Drug repurposing (AML) | 3/6 expert-selected drugs confirmed in vitro; KIRA6 is a genuine novel discovery |
| Liver fibrosis targets | 2/3 epigenetic modifiers showed anti-fibrotic activity |
| AMR (cf-PICIs) | Independently recapitulated an unpublished finding in 2 days vs. decade-long conventional programme |

Expert-in-the-loop results (Fig 6): AI-augmented expert hypotheses eventually surpass both pure-AI and pure-expert baselines.

## Limitations (Acknowledged)

- Open-access literature only (misses paywalled papers)
- No negative results data (published literature skews positive)
- No multimodal reasoning (can't read figures, charts, omics data)
- Elo is self-evaluated, not grounded in external truth
- Biomedical only (no social science, economics, or humanities validation)
- Small expert evaluation (11 goals, 7 experts)

## Relevance to the user's Research

### For human-AI collaboration research
- Concrete case study of human-AI complementarity (citable: Fig 6 shows AI+expert > either alone)
- Expert-in-the-loop design: scientists refine goals, provide manual reviews, contribute hypotheses that compete alongside AI-generated ones
- Gap in their framework: no MCDM perspective on how scientists should *decide* which AI-generated hypotheses to pursue (novelty vs. feasibility vs. resource cost vs. alignment)

### For multi-agent systems research
- Well-documented architecture with emergent capabilities through orchestration
- Tournament + meta-review loop is a novel coordination mechanism distinct from sequential pipelines or debate protocols
- Proximity graph for idea deduplication and exploration-space mapping

### Borrowed for Claude Code infrastructure
- **Multi-turn debate** added to `/devils-advocate` (3-round: critic -> defense -> adjudication)

### Not worth implementing
- Full tournament/Elo infrastructure (overkill for 6 projects vs. hundreds of hypotheses)
- Proximity graphs (not enough parallel outputs to need clustering)
- Evolution agent (existing review cycles already iterate)

## Citation

```bibtex
@article{gottweis2025towards,
  title={Towards an AI Co-Scientist},
  author={Gottweis, Juraj and others},
  year={2025},
  journal={arXiv preprint arXiv:2502.18864}
}
```
