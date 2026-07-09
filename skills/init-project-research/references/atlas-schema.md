# Atlas Schema Reference

## Vault paths

The Research Vault (`~/vault`) is the canonical store for atlas data. Themes are stored in `~/vault/themes/{slug}.md` and topics as markdown files at `~/vault/atlas/{theme}/{slug}.md`. Frontmatter values use Obsidian wiki-link format (`[[...]]`) — strip brackets when parsing.

## Theme → Vault Path Mapping

When creating an atlas topic file, use Obsidian wiki-link format (`[[...]]`) for relational fields (theme, connected_topics, co_authors, venue) to match existing vault files and enable Obsidian linking.

```yaml
theme: '[[Theme Name]]'  # Must match a theme in ~/vault/themes/
```

## YAML Frontmatter Template

```yaml
---
title: "Topic Name"
theme: '[[Theme Name]]'  # Wiki-link to theme file
status: "Idea"  # Idea | Exploring | Drafting | Pre-submission | Submitted | R&R | Accepted | In Press | Published | Rejected | Parked | Active Project
institution: "[University]"  # [University 1] | [University 2] | [University 3] | [University 4] | None
project_path: "ThemeAbbrev/slug"  # Relative to Projects/
linked_projects: []
connected_topics:  # kebab-case slugs in wiki-link format
  - '[[slug-1]]'
  - '[[slug-2]]'
methods:  # controlled vocabulary — see VALID_METHODS in schema.py (40 canonical)
  - Game Theory
  - Analytical Modelling / Formal Theory
domains: []  # optional — subject-domain tags (e.g. Category D); open list, NOT a method
co_authors:
  - '[[Name]]'
outputs:
  - venue: '[[Venue Name]]'
    format: "Full paper"  # Full paper | Extended abstract | Perspective | Working paper
    status: "Idea"  # Idea | Drafting | Submitted | R&R | Accepted | In Press | Published | Rejected | Parked
    label: ""  # Optional: short label for multi-output topics
    deadline: ""  # Optional: YYYY-MM-DD
feasibility: "High"  # High | Medium | Low
data_availability: "None"  # None | Open | Existing | New | Synthetic | Mixed
data_modality: ""  # omit if availability=None; else: Experiment | Survey | Platform / Web / API | Administrative / Panel / Registry | Secondary dataset | Simulation / Synthetic | Interview / Fieldwork
priority: "Medium"  # Critical | High | Medium | Low
type: topic
---
```

## Body Template

```markdown
## Description

[1-3 sentences: core research question and approach]

## Key References

- [Source: Scout report or existing paper]
- [Scout novelty score if available]

## Open Questions

- [Key unknowns]
```

## Methods Controlled Vocabulary (40 canonical)

`methods:` values MUST be drawn from `VALID_METHODS` in `packages/atlas-vault/schema.py` (the source of truth) — anything else fails the `validate-topic-frontmatter` hook. Full list with scope notes + a plain-English quick-reference card: `~/vault/reports/portfolio/2026-05-31-atlas-methods-taxonomy.md`. The 9 families:

- **A. Formal/Strategic/Logical:** Analytical Modelling / Formal Theory · Game Theory · Category I · Social Choice Theory · Decision Theory · Information Theory · Algorithms & Complexity · Formal Methods, Logic & Argumentation
- **B. Optimisation/MCDM/Preference:** Mathematical Optimisation · Multi-Objective Optimisation · Multi-Criteria Decision Analysis · Preference Elicitation & Learning
- **C. Statistical/Bayesian/Causal:** Bayesian Inference · Statistical Modelling & Inference · Causal Inference · Econometrics
- **D. ML & AI:** Machine Learning · Reinforcement Learning · Natural Language Processing & Language Models · Model Interpretability & Explainability · AI Evaluation & Benchmarking · Federated Learning · Adversarial Methods & Robustness
- **E. Security & Privacy:** Cryptography · Differential Privacy · Security & Privacy Engineering
- **F. Agents & Simulation:** Multi-Agent Systems · Simulation & Computational Experiment
- **G. Empirical/Human/Social:** Experiment · Survey · Psychometrics & Measurement · Cognitive & Behavioural Modelling · Empirical Measurement & Audit · Qualitative · Mixed Methods · Evidence Synthesis
- **H. Knowledge/Systems/Data:** Knowledge Representation & Ontologies · Design Science & Systems Building
- **I. Policy/Legal/Normative:** Legal, Regulatory & Institutional Analysis · Conceptual & Normative Analysis

Subject-domain labels (Category D, Information Economics, …) are NOT methods — put them in `domains:`.

## File Naming

- Topic file: `kebab-case-slug.md` in `~/vault/atlas/{theme-dir}/`
- Theme directories: `operations-research/`, `behavioural-decision-science/`, `ai-safety-governance/`, `human-ai-interaction/`, `mechanism-design/`, `nlp-computational-ai/`, `political-science/`, `organisation-strategy/`, `environmental-economics/`, `industrial-organisation/`
- Atlas tooling (schema.py, generate_recap.py): `$TM/packages/atlas-vault/`

## Research Project Path

```
$RESEARCH_ROOT/{ThemeAbbrev}/{slug}/
```

Where `$RESEARCH_ROOT` is read from `~/.config/task-mgmt/research-root`. Theme abbreviations: T1, T2, T3, T4, T5, T6, T7, T8, T9, T10 (define your own theme codes). Folder name = kebab-case slug (same as atlas topic filename).
