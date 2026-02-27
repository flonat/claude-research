---
name: quarto-deck
description: "Generate Reveal.js HTML presentations from Markdown. Applies rhetoric principles (assertion titles, one idea per slide, narrative arc). Best for teaching, informal talks, and web-shareable decks."
allowed-tools: Bash(reveal-md*), Bash(npx*), Bash(mkdir*), Bash(ls*), Bash(cp*), Bash(open*), Bash(R*), Bash(Rscript*), Bash(python*), Read, Write, Edit, Task
argument-hint: [topic, content-path, or project-name]
---

# Reveal.js Deck Skill

> Generate HTML presentations from Markdown using reveal-md. Applies the same rhetoric framework as `/beamer-deck` but outputs browser-native slides ideal for teaching, informal talks, and web sharing.

## Purpose

Create polished Reveal.js presentations from Markdown files. Every deck gets assertion-driven titles, narrative arc, and rhetoric review. Output is an HTML presentation that runs in any browser — no LaTeX needed.

**Use this for:** Teaching, informal research talks, web-shareable presentations, interactive demos.
**Use `/beamer-deck` for:** Conference talks, formal seminars, supervisor meetings, anything that needs PDF-native output.

## When to Use

- Teaching lectures (undergraduate or PhD) — interactive, live in browser
- Informal research presentations or lab meetings
- Talks where you want to share a URL instead of a PDF
- Presentations with live code demos or embedded content
- Quick decks where LaTeX overhead isn't justified

**Python:** Always use `uv run python`. Never bare `python`, `python3`, `pip`, or `pip3`.

## Prerequisites

- `reveal-md` (installed globally): `npm install -g reveal-md`
- Node.js 18+ (via nvm)

---

## Critical Rules

0. **Python: ALWAYS use `uv run python` or `uv pip install`.** Never use bare `python`, `python3`, `pip`, or `pip3`. Include this instruction in any sub-agent prompts that may run Python.
1. **One Markdown file = one presentation.** All slides live in a single `.md` file with `---` separators.
2. **Titles are assertions, not labels.** "Distance increases abortion rates" — not "Results". Every slide title states a claim.
3. **One idea per slide.** Not a guideline. A law. If a slide has two ideas, split it.
4. **Speaker notes use the `Note:` keyword.** Place after slide content, before the next `---`.
5. **Custom CSS goes in a separate file.** Never inline styles in the Markdown.
6. **Figures first, slides second.** Generate figures via R or Python scripts before referencing them.
7. **Test in browser before finalising.** Run `reveal-md <file>.md` and check every slide.

---

## Rhetoric Principles

Same framework as `/beamer-deck`. Full reference (Three Laws, MB/MC, Aristotelian Triad, Narrative Arc, Pyramid Principle, Devil's Advocate, audience-specific guidance): [`../shared/rhetoric-principles.md`](../shared/rhetoric-principles.md)

---

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Compute the score in Phase 6 and report it in the final output.

## Reveal.js Markdown Format

Full format reference with basic structure, vertical slides, fragments, custom themes, and CSS examples: [`references/markdown-format.md`](references/markdown-format.md)

**Reference palettes** (Professional, Energetic, Academic) with both LaTeX and CSS variants: [`../shared/palettes.md`](../shared/palettes.md)

---

## Workflow: 6 Phases

```
You (orchestrator)
├── Phase 1: Gather context        (direct)
├── Phase 2: Design structure       (direct)
├── Phase 3: Build deck             (direct)
├── Phase 4: Preview & fix          (direct)
├── Phase 5: Rhetoric review        (sub-agent — Explore)
└── Phase 6: Apply & finalise       (direct)
```

### Phase 1: Gather Context (Direct)

Read project files, content sources, and audience brief. Ask the user:

- **Audience**: Teaching? Lab meeting? Informal talk?
- **Duration**: How long?
- **Content source**: Paper draft? Notes? Existing slides?
- **Special requirements**: Code demos? Interactive elements? Specific theme?
- **Export needs**: Browser only, or also need static HTML/PDF?

### Phase 2: Design Structure (Direct)

1. **Choose rhetoric balance** based on audience
2. **Outline slide sequence** with assertion titles
3. **Plan narrative arc** — identify Act I/II/III transitions
4. **Choose colour palette** — create `custom.css`
5. **Identify figures needed** — which need code generation?

Present outline to the user for approval.

### Phase 3: Build Deck (Direct)

1. **Generate figures first** — R/Python scripts, save to `figures/`
2. **Write the `.md` file** with YAML frontmatter and slide content
3. **Write `custom.css`** if custom theming is needed
4. **Test locally**: `reveal-md deck.md`
5. **Add speaker notes** using `Note:` blocks

### Phase 4: Preview and Fix (Direct)

1. Run `reveal-md deck.md` to preview in browser
2. Check every slide for:
   - Text overflow or cramped content
   - Figure sizing and alignment
   - Math rendering (MathJax)
   - Code highlighting
   - Transitions between slides
3. Fix issues and re-preview

### Phase 5: Rhetoric Review (Sub-Agent — Explore)

Launch the same rhetoric review as `/beamer-deck`, adapted for Markdown:

```
subagent_type: Explore
prompt: |
  You are a rhetoric reviewer for an academic Reveal.js presentation.

  Read the file at: [PATH TO .md FILE]

  Evaluate against these criteria:

  ## 1. Narrative Arc
  - Three-act structure (Problem → Investigation → Resolution)?
  - Opening: provocative question, statistic, or bold claim?
  - Closing: single memorable takeaway?

  ## 2. MB/MC Balance
  - Cognitive load distributed smoothly?
  - Overloaded or underloaded slides?

  ## 3. Title Quality
  - Every title an assertion (a claim), not a label?

  ## 4. One Idea Per Slide
  - Any slide trying to convey multiple ideas?

  ## 5. Transitions
  - Are transitions between slides explicit?
  - Does the audience know where they are in the argument?

  ## 6. Pyramid Principle
  - Conclusions before support?

  Return structured markdown with ratings and specific slide suggestions.
```

### Phase 6: Apply and Finalise (Direct)

1. Incorporate rhetoric review feedback
2. Re-preview in browser
3. **Compute quality score** — read `references/quality-rubric.md`, log all issues from Phases 4-5, compute score and verdict
4. **Export if needed:**
   - Static HTML: `reveal-md deck.md --static _site`
   - PDF: `reveal-md deck.md --print deck.pdf`
5. Confirm all files are in place

---

## Commands Reference

| Command | What it does |
|---------|-------------|
| `reveal-md deck.md` | Live preview with hot reload (default port 1948) |
| `reveal-md deck.md --css custom.css` | Preview with custom CSS |
| `reveal-md deck.md --static _site` | Export to static HTML (shareable folder) |
| `reveal-md deck.md --print deck.pdf` | Export to PDF (uses Puppeteer) |
| `reveal-md deck.md --port 3000` | Preview on custom port |
| `reveal-md deck.md --theme moon` | Use built-in theme (moon, night, serif, etc.) |

Press `s` during preview to open **speaker notes view**.
Press `f` for fullscreen. Press `o` for slide overview.

---

## Output Checklist

A completed deck directory should contain:

```
project/
├── deck.md               # Markdown presentation
├── custom.css             # Custom theme (if used)
├── figures/               # Generated figures (if any)
│   ├── figure_1.png
│   └── ...
├── scripts/               # R/Python scripts for figures (if any)
│   ├── figure_1.R
│   └── ...
├── _site/                 # Static HTML export (if generated)
└── deck.pdf               # PDF export (if generated)
```

- [ ] All slide titles are assertions
- [ ] One idea per slide
- [ ] Narrative arc: Problem → Investigation → Resolution
- [ ] Rhetoric review completed (Phase 5)
- [ ] Speaker notes present for key slides
- [ ] Math renders correctly (if used)
- [ ] Tested in browser — no overflow or layout issues
- [ ] Quality score computed and reported

---

## Cross-References

| Skill | When to use instead/alongside |
|-------|-------------------------------|
| `/beamer-deck` | For formal academic presentations (conferences, seminars) that need PDF-native output |
| `/project-deck` | For project status updates (supervisor meetings, coauthor handoffs) |
| `/proofread` | For post-hoc review of text quality |
| `/literature` | For finding and verifying citations to include |
| `/quarto-course` | For full course websites with multiple lectures, exercises, and navigation |
