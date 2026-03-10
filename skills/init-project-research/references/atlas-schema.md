# Atlas Schema Reference

## Notion Database IDs

| Database | Data Source ID |
|----------|---------------|
| Research Themes | `YOUR-THEMES-DB-ID` |
| Topic Inventory (Atlas) | `YOUR-ATLAS-DB-ID` |

## Theme → Notion Page ID Mapping

Look up the theme page ID before creating atlas entries. Theme is a **relation** property — pass as JSON array of page URLs.

To find a theme's page ID: query the Research Themes database or use `notion-search` for the theme name.

Format for the Theme relation property:
```
"Theme": "[\"https://www.notion.so/<theme-page-id-no-dashes>\"]"
```

## YAML Frontmatter Template

```yaml
---
title: "Topic Name"
theme: "Theme Name"  # Must match a theme in themes.md
status: "Idea"  # Idea | Exploring | Active Project | Parked | Archived
institution: "Institution A"  # Institution A | Institution B | Institution C | None
project_path: "Theme Name/Project Name"  # Relative to Research Projects/
linked_projects: []
connected_topics: ["slug-1", "slug-2"]  # kebab-case slugs of related topics
methods: ["Game Theory", "Formal Model"]
co_authors: "Name"
outputs:
  - venue: "Venue Name"
    format: "Full paper"  # Full paper | Extended abstract | Perspective | Working paper
    status: "Planned"  # Planned | Drafting | Submitted | Accepted | Published
    label: ""  # Optional: short label for multi-output topics
    deadline: ""  # Optional: YYYY-MM-DD
feasibility: "High"  # High | Medium | Low
data_availability: "None"  # Open Data | Exists (needs access) | Needs Collection | None
priority: "Medium"  # Critical | High | Medium | Low
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

## Notion Methods Multi-Select Options

Only these values are valid (others will error):
`MCDM`, `Experiment`, `Formal Model`, `Survey`, `Simulation`, `Econometrics`, `Game Theory`, `Meta-Analysis`, `Qualitative`, `NLP/ML`

If a topic uses methods not in this list (e.g., "Mechanism Design", "Cryptography"), map to the closest valid option or omit.

## File Naming

- Topic file: `kebab-case-slug.md` in `research/atlas/topics/{theme-dir}/`
- Theme directories: `operations-research/`, `behavioural-decision-science/`, `ai-safety-governance/`, `human-ai-interaction/`, `mechanism-design/`, `nlp-computational-ai/`, `political-science/`, `organisation-strategy/`, `environmental-economics/`

## Dropbox Project Path

```
~/Library/CloudStorage/YOUR-CLOUD/Research/{Theme Name}/{Project Name}/
```
