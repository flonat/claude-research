# Phase 3: Chapter Scaffolding Guide

Eight chapters. For each, you write substantive prose grounded in the paper, **not placeholders**. Chapter responsibilities:

| Chapter | Role | Length | Key sources from paper |
|---|---|---|---|
| `intro.md` | One-chapter version: headline + 3-bullet result + why it matters | ~600 words | abstract, intro §1, contributions list |
| `background.md` | What the reader needs to know before §3 of the paper | ~800 words | related work, setup primitives |
| `setup.md` | Notation table, threat model / problem statement, worked example if applicable | ~700 words | §2 / setup section, notation table |
| `method.md` | Definitions → propositions → theorems with proof sketches and intuition | ~1200 words | §3 / method section, §4 / theorem statements |
| `results.md` | Headline result, deterministic case study, stress test, figures, comparison tables | ~1000 words | §5 / experiments, figures, tables |
| `limitations.md` | What's NOT claimed, where the framework cracks, what's next | ~600 words | §6 / discussion, §7 / limitations |
| `extend.md` | Worked steps for adopting the framework — code skeletons, extension paths, reproducibility checklist | ~900 words | §8 / instructions, reproducibility manifest |
| `appendix.md` | Notation glossary (consolidated), theorem summary table, reproducibility manifest, links | ~500 words | full paper + atlas topic |

For each chapter:
- Start with a frontmatter block: `title:` (long) and `short_title:` (~1 word for sidebar).
- **Do NOT include a `# Heading` H1 in chapter bodies.** Atlas's template renders the chapter title from `index.yaml` as `<h1 class="page-title">` — a body H1 produces a duplicate. Start the body with prose (or, for `intro.md`, the lede + definition-list masthead — see "Intro masthead format" below).
- **`intro.md` masthead.** Use the definition-list pattern (see "Intro masthead format"). Pull authors and affiliations from the atlas topic's `institution:` field; venue from `outputs[]`. Add the Source/Overleaf line per the decision rule (omit if accepted/published).
- Use mystmd-style callouts for asides: `` ```{important} `` for headline statements, `` ```{tip} `` for reading-order hints, `` ```{warning} `` for caveats, `` ```{caution} `` for hazards.
- Use markdown tables for notation + comparison + result tables. Atlas styles tables with hairline dividers + tabular nums.
- Use $...$ and $$...$$ for math. Atlas's arithmatex extension preserves these for MathJax.
- Cross-reference paper sections inline ("paper §4.2") rather than via book chapter numbers.
- For citations, use mystmd-style `{cite:t}\`Key\`` — atlas converts to `/book/<slug>/references#ref-Key` when the key is in the book's local `references.bib` (the common case), or to `https://atlas.example.com/paper/Key` as a fallback for keys only in the global library.
- **Include the accessibility floor verbatim in every Phase 3 sub-agent prompt** (see hard rule 14). Sub-agents do not inherit project conventions — paste the floor in.
