# Research query routing

Use the user's evidence request—not the presence of a venue name—to choose the route.

| Intent | Primary route | Boundary |
|---|---|---|
| Existing portfolio state: “do I have,” “which of my,” “what is recorded” | `task-management` → `taskflow-cli` | Query structured vault records; do not run a recommendation workflow merely because a venue is named. |
| Topic–venue suitability: “would this fit,” “should I target,” “where should I publish” | Load existing state with `taskflow-cli`, then use the installed venue-recommendation workflow | Label its results as recommendations or inference, never recorded state. |
| Venue deadline, format, or policy | Vault venue record and `conf-timeline`; verify current policy against the official CFP when needed | Do not infer time-sensitive policy from stored model knowledge. |

## Evidence order

1. Establish the requested population from structured topic metadata, including `institution`, status, theme, collaborators, or another named field.
2. Join topic records to paper outputs, submissions, and canonical venue records.
3. Separate recorded possibilities from active/historical venue events.
4. Add suitability analysis only if the user asks for it, and keep it visibly distinct from stored facts.


## Regression examples

| Prompt | Expected route |
|---|---|
| “Venue Y: do I have any institution-X topics that list it as a possible venue?” | `task-management` and `taskflow-cli`; filter the structured `institution` field, then join outputs/submissions/venues. |
| “Which of my institution-X topics should target venue Y?” | Taskflow inventory first, then venue suitability analysis. |
| “When is the next venue-Y deadline?” | Venue record/conf-timeline plus official verification if freshness matters. |
| “Audit the visual design of the Atlas venue page.” | `ui-critic`. |

Missing MCP registration is not a routing failure. In Codex, Taskflow is intentionally CLI-first; in Claude, an MCP adapter may coexist with the same portable CLI.
