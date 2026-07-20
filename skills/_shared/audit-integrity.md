# Shared audit and review integrity

Use this contract whenever a workflow delegates audit, counting, scoring, or
review work and then consumes the returned findings.

## Rules

1. Objective counts and coverage claims come from deterministic commands run by
   the orchestrator. A delegated reviewer may quote those values but must not
   estimate replacements.
2. Every finding cites an exact `path:line` (or document section) and quotes the
   evidence it evaluates. A claim without a verifiable anchor is omitted.
3. The orchestrator confirms every claimed output exists before trusting a
   completion summary.
4. Before synthesis, the orchestrator spot-checks at least three findings or 20
   percent of the batch, whichever is larger. A failed sample triggers wider
   verification or rejection of that batch.

## Dispatch clause

Include this text in delegated audit and review prompts:

```text
Do not state counts that were not supplied as verified ground truth. Every
finding must cite a path and line or document section and quote the exact
evidence. Do not claim an output exists unless you wrote it in this run. Omit
claims that cannot be grounded.
```

The caller remains responsible for computing ground truth, reconciling returned
claims, spot-checking evidence, and confirming outputs.
