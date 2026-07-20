# Skill template

Use this client-neutral structure for a new skill or a substantial rewrite.

```markdown
---
name: skill-name
description: "Use when ..."
allowed-tools: <optional client-supported tools>
argument-hint: "[optional arguments]"
---

# Skill title

One-sentence purpose.

## Hard rules

1. Rules whose violation invalidates the result.

## When to use

- Explicit triggers.

## When not to use

- Anti-triggers and named alternatives.

## Phase 1: Discover

### 1.1 Validate inputs

## Phase 2: Execute

### 2.1 Produce bounded outputs

## Phase 3: Verify

### 3.1 Confirm every claimed output and acceptance criterion
```

Keep the protocol to three to five named phases. Use `N.M` substeps rather than
lettered or fractional phases. Resolve sibling resources with relative paths;
do not embed a client home or machine-specific absolute path in a skill intended
for both clients. Put output verification inside the final write phase before
any commit step.
