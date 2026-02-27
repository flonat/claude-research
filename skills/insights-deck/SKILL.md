---
name: insights-deck
description: "Generate timestamped Claude Code insights report and Beamer presentation. Runs /insights, archives HTML, then builds a rhetoric-driven deck from the findings."
allowed-tools: Bash(latexmk*), Bash(pdflatex*), Bash(xelatex*), Bash(mkdir*), Bash(ls*), Bash(cp*), Read, Write, Edit, Glob, Grep, Task
argument-hint: (no arguments)
---

# Insights Deck Skill

> Archive a Claude Code `/insights` HTML report and generate a Beamer presentation summarising the findings. All outputs go to `log/insights/` with date stamps.

## When to Use

- After running `/insights` to review your Claude Code usage patterns
- When you want a shareable deck summarising how you use Claude Code
- For periodic self-reflection on AI-assisted workflow

## Scope

This skill produces **two outputs only**: an archived HTML report and a Beamer deck. Do NOT use insights suggestions to create plans, rules, CLAUDE.md edits, or other follow-up actions during this skill's execution. If the user wants to act on suggestions, that happens after the deck is delivered — as a separate conversation.

---

## Phase 1 — Generate & Archive Insights

### Step 1: Prompt the user to run `/insights`

`/insights` is a built-in Claude Code command that cannot be invoked programmatically. Tell the user:

> Please run `/insights` now. Once the HTML report opens in your browser, let me know and I'll continue.

### Step 2: Locate the generated HTML

After `/insights` completes, find the most recent insights HTML file:

```bash
ls -t /tmp/claude-insights-*.html 2>/dev/null | head -1
```

If not found in `/tmp/`, check the user's home directory and common download locations. Ask the user for the path if it can't be located automatically.

### Step 3: Archive the HTML

Each insights run gets its own date folder:

```bash
mkdir -p log/insights/YYYY-MM-DD
cp <source-html> log/insights/YYYY-MM-DD/insights-YYYY-MM-DD-log.html
```

Use today's date for the timestamp.

---

## Phase 2 — Build Beamer Deck

### Step 1: Read and extract findings

Read the archived HTML file (`log/insights/YYYY-MM-DD/insights-YYYY-MM-DD-log.html`). Extract:

1. **Usage patterns** — most-used tools, session frequency, typical session length
2. **Strengths** — what's working well in the workflow
3. **Friction points** — repeated failures, slow patterns, underused features
4. **Recommendations** — suggested improvements

### Step 2: Design the deck structure

Apply rhetoric principles from the `beamer-deck` skill (condensed — no sub-agent reviews needed for an internal deck):

- **Assertion titles** — every frame title states a claim, not a label
- **One idea per slide** — split if a slide has two ideas
- **Three-act arc:**
  - Act I (Tension): Current usage snapshot — what does the data show?
  - Act II (Development): Patterns, strengths, friction points
  - Act III (Resolution): Recommendations and next steps
- **MB/MC balance** — vary dense and light slides deliberately
- **Pyramid principle** — lead with conclusions, then support

### Step 3: Generate the `.tex` file

Write to `log/insights/YYYY-MM-DD/insights-YYYY-MM-DD-deck.tex` with:

- `\documentclass[aspectratio=169,11pt]{beamer}`
- Original inline theme (no default Beamer themes)
- Professional colour palette:
  ```latex
  \definecolor{Midnight}{HTML}{1A1A2E}
  \definecolor{DeepBlue}{HTML}{16213E}
  \definecolor{RoyalBlue}{HTML}{0F3460}
  \definecolor{Coral}{HTML}{E94560}
  \definecolor{SoftGray}{HTML}{BDC3C7}
  \definecolor{CloudWhite}{HTML}{FAFBFC}
  ```
- Suggested structure (adapt based on findings):
  1. Title slide — "Claude Code Usage: [Month Year]"
  2. Opening claim — lead with the most striking finding
  3. Usage overview — session count, tool distribution, time patterns
  4. Top strengths (1–2 slides)
  5. Key friction points (1–2 slides)
  6. Recommendations (1–2 slides)
  7. Closing — single actionable takeaway

### Step 4: Compile

Create a `.latexmkrc` in the date folder if not present:

```perl
$out_dir = 'out';
# Copy PDF back to source directory after build
END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
```

Then compile:

```bash
cd log/insights/YYYY-MM-DD && latexmk -pdf insights-YYYY-MM-DD-deck.tex
```

### Step 5: Fix all warnings

Parse `out/*.log` for overfull/underfull hbox/vbox warnings. Fix every one. Recompile until clean.

The `.latexmkrc` copies the PDF from `out/` back to the date folder automatically.

---

## Output

When complete, the date folder should contain:

```
log/insights/YYYY-MM-DD/
├── insights-YYYY-MM-DD-log.html     # Archived /insights HTML
├── insights-YYYY-MM-DD-deck.tex     # Beamer source
├── insights-YYYY-MM-DD-deck.pdf     # Compiled PDF
├── .latexmkrc                       # Build config
└── out/                             # Build artifacts
```

Each `/insights-deck` run creates a new date folder, keeping the parent `log/insights/` clean.

---

## Cross-References

| Skill | Relationship |
|-------|-------------|
| `/beamer-deck` | Full rhetoric framework and multi-agent review (this skill uses a condensed version) |
| `/latex-autofix` | **Default compiler** — use for compilation with auto error resolution |
| `/latex` | Manual compilation config details, `.latexmkrc` setup |
| `/session-log` | Complements insights with session-level detail |
