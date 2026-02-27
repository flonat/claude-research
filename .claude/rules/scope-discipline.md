# Rule: Scope Discipline

## Principle

**Only make changes the user explicitly requested.** Do NOT fix additional issues you notice (e.g., extra proofreading, reformatting, style improvements) unless asked. When in doubt, list what you'd like to also fix and ask for permission.

## What This Means

- If asked to fix 6 issues, fix exactly those 6 — not 6 plus 3 more you spotted
- If asked to proofread major issues, do not also fix minor ones
- If asked to update one file, do not "while I'm here" edit neighbouring files
- If asked to add a feature, do not also refactor surrounding code

## When You Notice Something Else

1. Complete the requested task first
2. At the end, mention what else you noticed: "I also spotted X, Y, Z — want me to fix those too?"
3. Wait for explicit approval before touching anything beyond scope

## Exceptions

- **Security vulnerabilities** — fix immediately and flag to the user
- **Broken compilation** caused by your own changes — fix as part of the current task
- **Trivial typos in lines you're already editing** — acceptable if truly on the same line

## Why This Matters

Scope overreach forces reverts, wastes time, and erodes trust. Doing less than asked is annoying; doing more than asked is destructive.
