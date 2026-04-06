# Atlas Schema Reference

## Vault paths

| Database | Data Source ID |
|----------|---------------|
| Research Themes | `2e8baef4-3e2e-4ea5-b25a-18a71ed47690` |
| Topic Inventory (Atlas) | `0a227f82-60f4-451a-a163-bff2ce8fa9c3` |

## Theme → Vault Path Mapping

Look up the theme page ID before creating atlas entries. Theme is a **relation** property — pass as JSON array of page URLs.

To find a theme's page ID: query the Research Themes database or use `mcp__taskflow__search_tasks` for the theme name.

Format for the Theme relation property:
```
"Theme": "[\"~/Research-Vault/<theme-page-id-no-dashes>\"]"
```

## YAML Frontmatter Template

```yaml
---
title: "Topic Name"
theme: "Theme Name"  # Must match a theme in themes.md
status: "Idea"  # Idea | Exploring | Active Project | Parked | Archived
institution: "Bath"  # Warwick | Bath | Southampton | UPF | None
project_path: "Theme Name/Project Name"  # Relative to Projects/
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

## Vault Methods Multi-Select Options

Only these values are valid (others will error):
`MCDM`, `Experiment`, `Formal Model`, `Survey`, `Simulation`, `Econometrics`, `Game Theory`, `Meta-Analysis`, `Qualitative`, `NLP/ML`

If a topic uses methods not in this list (e.g., "Mechanism Design", "Cryptography"), map to the closest valid option or omit.

## File Naming

- Topic file: `kebab-case-slug.md` in `packages/atlas/topics/{theme-dir}/`
- Theme directories: `operations-research/`, `behavioural-decision-science/`, `ai-safety-governance/`, `human-ai-interaction/`, `mechanism-design/`, `nlp-computational-ai/`, `political-science/`, `organisation-strategy/`, `environmental-economics/`

## Research Project Path

```
$RESEARCH_ROOT/{Theme Name}/{Project Name}/
```

Where `$RESEARCH_ROOT` is `~/Library/CloudStorage/YOUR-CLOUD/Research` (MacBook) or `~/Projects` (Mac Mini).
