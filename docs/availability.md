# AI surface availability

> Generated from `config/ai-contracts.yaml`; do not hand-edit counts or targeting.

This is the runtime availability inventory for **flonat-research**. Inclusion in this
distribution and client compatibility are separate decisions: every shipped asset
has an explicit client list, with no implicit `both` default.

## Summary

| Surface | Shipped | Claude | Codex |
|---|---:|---:|---:|
| Skills | 109 | 109 | 106 |
| Agents | 15 | 15 | 14 |
| Rules | 18 | 18 | 18 |
| Hooks | 9 | 9 | 0 |
| Mcps | 0 | 0 | 0 |
| Clis | 0 | 0 | 0 |

## Skills

| Asset | Claude | Codex | Requirements | Why / fallback |
|---|:---:|:---:|---|---|
| `audit-paper-book` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `audit-project-research` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `beamer-deck` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `bib-coverage` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `bib-filter` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `bib-parse` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `bib-validate` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `brief-compliance-check` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `camera-ready` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `causal-design` | Yes | Yes | filesystem, skill-routing, subagents | selected by the reviewed public distribution |
| `checkpoint` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `code-archaeology` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `compile-knowledge` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `computational-experiments` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `cross-language-check` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `data-analysis` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `devils-advocate` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `docs-consistency` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `docx` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `experiment-design` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `gather-readings` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `grill-me` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `handoff` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `ideas` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `init-paper-book` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `init-project` | Yes | No | claude-tool-syntax, filesystem, shell | Hand-maintained public scaffolder uses AskUserQuestion and remains Claude-only. |
| `init-project-course` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `init-project-light` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `init-project-orchestration` | Yes | Yes | filesystem, shell, skill-routing | reviewed client-neutral project orchestration with deterministic Claude and Codex adapters |
| `init-project-research` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `insights-deck` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `interview-me` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `knowledge-lint` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `latex` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `latex-diff` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `latex-health-check` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `latex-polish` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `latex-posters` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `latex-scaffold` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `latex-template` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `lean-check` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `literature` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `math-proof` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `mcp-builder` | Yes | Yes | filesystem, shell, subagents, web | selected by the reviewed public distribution |
| `meetings-cleanup` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `meetings-debrief` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `meetings-list` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `meetings-prep` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `meetings-recap` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `meetings-search` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `meetings-verify` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `meetings-weekly` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `memory-cleanup` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `method-audit` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `multi-perspective` | Yes | Yes | filesystem, skill-routing, subagents | selected by the reviewed public distribution |
| `numerical-check` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `pdf` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `pipeline-manifest` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `playwright-cli` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `postmortem` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `pre-commit-audit` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `pre-submission-report` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `preprint` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `preregister` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `project-deck` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `project-safety` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `proof-readability` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `proofread` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `python-env` | Yes | Yes | filesystem, shell | selected by the reviewed public distribution |
| `quarto-deck` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `rename-project-research` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `reorg` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `replication-audit` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `replication-package` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `retarget-journal` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `review-cluster` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `review-response` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `save-context` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `session-close` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `session-health` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `session-log` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `skill-creator` | Yes | No | claude-client-instruction, filesystem, shell, subagents, web | selected by the reviewed public distribution |
| `skill-extract` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `skill-health` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `skill-preflight` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `split-pdf` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `strategic-revision` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `symbolic-check` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `sync-permissions` | Yes | No | claude-home-layout, filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `synthesise-reviews` | Yes | Yes | filesystem, skill-routing, subagents | selected by the reviewed public distribution |
| `synthetic-data` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `system-audit` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `tailscale-mosh-recover` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `task-management` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `test-iterate-loop` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `tikz` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `update-focus` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `update-project-doc` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `venue-fork` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `verify-math` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `voice-analyzer` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `voice-editor` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `weakness-scanner` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `webapp-testing` | Yes | Yes | filesystem, shell, web | selected by the reviewed public distribution |
| `wiki-curate` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `wiki-grow` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `wiki-merge` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `wire-shared-package` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `xlsx` | Yes | Yes | filesystem, shell, web | selected by the reviewed public distribution |

## Agents

| Asset | Claude | Codex | Requirements | Why / fallback |
|---|:---:|:---:|---|---|
| `artifact-coherence-auditor.md` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `blindspot.md` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `claim-verify.md` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `code-paper-auditor.md` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `code-review.md` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `codex-research.md` | Yes | No | external-codex-delegation, filesystem, shell, skill-routing | selected by the reviewed public distribution |
| `domain-reviewer.md` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `fatal-error-check.md` | Yes | Yes | filesystem, skill-routing | selected by the reviewed public distribution |
| `fixer.md` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `gemini-research.md` | Yes | Yes | filesystem, shell, skill-routing, web | selected by the reviewed public distribution |
| `paper-critic.md` | Yes | Yes | filesystem, shell, skill-routing, subagents | selected by the reviewed public distribution |
| `peer-reviewer.md` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `proposal-reviewer.md` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `referee2-reviewer.md` | Yes | Yes | filesystem, shell, skill-routing, subagents, web | selected by the reviewed public distribution |
| `reproducibility-auditor.md` | Yes | Yes | filesystem, shell, skill-routing | selected by the reviewed public distribution |

## Rules

| Asset | Claude | Codex | Requirements | Why / fallback |
|---|:---:|:---:|---|---|
| `audit-before-fix.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `client-guidance-ownership.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `design-before-results.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `doi-verification.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `latex-hygiene.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `lean-guidance-files.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `learn-tags.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `mark-unverified.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `no-hardcoded-results.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `overleaf-separation.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `paper-code-consistency.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `plan-first.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `python-uv.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `read-docs-first.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `scope-discipline.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `severity-gradient.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `spec-before-quality.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |
| `subagent-write-guard.md` | Yes | Yes | filesystem | selected by the reviewed public distribution |

## Hooks

| Asset | Claude | Codex | Requirements | Why / fallback |
|---|:---:|:---:|---|---|
| `block-destructive-git.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `context-monitor.py` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `handoff-read.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `postcompact-restore.py` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `precompact-autosave.py` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `promise-checker.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `protect-source-files.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `resume-context-loader.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |
| `startup-context-loader.sh` | Yes | No | claude-hooks, filesystem | selected by the reviewed public distribution |

## MCP registrations and CLIs

This downstream framework does not install credentials or private MCP registrations.
MCP servers are optional client adapters and are documented separately. Skills that
need an external capability must name a portable CLI or a clearly documented manual
fallback; installing the framework does not silently install those third-party services.

## Interpreting an unavailable entry

`No` means the distribution deliberately does not install that asset for the client.
It is not a discovery failure. Use the stated fallback, adapt the canonical source and
contract, or run a different shipped workflow; do not copy files between client homes.
