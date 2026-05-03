# Atlas Schema Reference

## Vault paths

The Research Vault (`~/Research-Vault`) is the canonical store for atlas data. Themes are stored in `~/Research-Vault/themes/{slug}.md` and topics as markdown files at `~/Research-Vault/atlas/{theme}/{slug}.md`. Frontmatter values use Obsidian wiki-link format (`[[...]]`) — strip brackets when parsing.

## Theme → Vault Path Mapping

When creating an atlas topic file, use Obsidian wiki-link format (`[[...]]`) for relational fields (theme, connected_topics, co_authors, venue) to match existing vault files and enable Obsidian linking.

```yaml
theme: '[[Theme Name]]'  # Must match a theme in ~/Research-Vault/themes/
```

## YAML Frontmatter Template

```yaml
---
title: "Topic Name"
theme: '[[Theme Name]]'  # Wiki-link to theme file
status: "Idea"  # Idea | Exploring | Drafting | Pre-submission | Submitted | R&R | Accepted | Rejected | Parked | Active Project
institution: "[University]"  # [University 1] | [University 2] | [University 3] | [University 4] | None
project_path: "ThemeAbbrev/slug"  # Relative to Projects/
linked_projects: []
connected_topics:  # kebab-case slugs in wiki-link format
  - '[[slug-1]]'
  - '[[slug-2]]'
methods:
  - Game Theory
  - Formal Model
co_authors:
  - '[[Name]]'
outputs:
  - venue: '[[Venue Name]]'
    format: "Full paper"  # Full paper | Extended abstract | Perspective | Working paper
    status: "Idea"  # Idea | Drafting | Submitted | R&R | Accepted | Rejected | Parked
    label: ""  # Optional: short label for multi-output topics
    deadline: ""  # Optional: YYYY-MM-DD
feasibility: "High"  # High | Medium | Low
data_availability: "None"  # Open Data | Exists (needs access) | Needs Collection | None
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

## Vault Methods Multi-Select Options

Only these values are valid (others will error):
`MCDM`, `Experiment`, `Formal Model`, `Survey`, `Simulation`, `Econometrics`, `Game Theory`, `Meta-Analysis`, `Qualitative`, `NLP/ML`

If a topic uses methods not in this list (e.g., "Mechanism Design", "Cryptography"), map to the closest valid option or omit.

## File Naming

- Topic file: `kebab-case-slug.md` in `~/Research-Vault/atlas/{theme-dir}/`
- Theme directories: `operations-research/`, `behavioural-decision-science/`, `ai-safety-governance/`, `human-ai-interaction/`, `mechanism-design/`, `nlp-computational-ai/`, `political-science/`, `organisation-strategy/`, `environmental-economics/`, `industrial-organisation/`
- Atlas tooling (schema.py, generate_recap.py, compile_atlas.py): `$TM/packages/atlas-vault/`

## Research Project Path

```
$RESEARCH_ROOT/{ThemeAbbrev}/{slug}/
```

Where `$RESEARCH_ROOT` is read from `~/.config/task-mgmt/research-root`. Theme abbreviations: ASG, BDS, EnvEcon, HAI, IO, MechDes, NLP, OR, OrgStrat, PolSci. Folder name = kebab-case slug (same as atlas topic filename).
