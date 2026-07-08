# Phase 5: Register + Smoke-Test

```bash
# Append to registry
cat >> ~/vault/books/index.yaml <<EOF

${SLUG}:
  title: "<book title — paper title or descriptive variant>"
  atlas_topic: "<theme>/<slug>"
  bibliography: references.bib
  chapters:
    - intro
    - background
    - setup
    - method
    - results
    - limitations
    - extend
    - appendix
EOF

# Reload atlas (Mac Mini only — see multi-machine rule)
launchctl bootout gui/$(id -u)/com.user.atlas
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.atlas.plist
sleep 4

# HTTP smoke test (necessary but not sufficient — see Playwright check below)
for ch in intro background setup method results limitations extend appendix references; do
    code=$(curl -s --max-time 8 -o /dev/null -w "%{http_code}" \
        "http://localhost:8770/book/${SLUG}/${ch}")
    echo "  ${ch}: ${code}"
done

# Update atlas topic frontmatter with book_url
python3 ~/Task-Management/.scripts/update_atlas_book_url.py \
  --slug "$SLUG" \
  --url "https://books.example.com/${SLUG}/"
```

## Visual smoke-test via Playwright (MANDATORY)

A 200 HTTP code only confirms the page served — it does NOT confirm math rendered, callouts rendered, figures resolved, citations linked, or the sidebar shows correct chapter order. Several real failure modes (mystmd → atlas converter regressions, missing `def_list` extension, broken figure paths, sidebar truncation) return 200 but render broken pages.

Use the `playwright-cli` skill (or Playwright CLI directly) to render each chapter and verify visual invariants:

```bash
# For each chapter, screenshot + DOM probe
for ch in intro background setup method results limitations extend appendix references; do
    npx playwright screenshot \
        --viewport-size=1280,900 \
        --wait-for-selector="article.book-chapter" \
        "http://localhost:8770/book/${SLUG}/${ch}" \
        "/tmp/init-paper-book-${SLUG}-${ch}.png" 2>&1
done

# DOM-based assertions (one Playwright script — see references/visual_check.mjs)
node ~/.claude/skills/init-paper-book/references/visual_check.mjs \
    --slug "${SLUG}" \
    --base-url "http://localhost:8770" \
    --output /tmp/init-paper-book-visual-${SLUG}.json
```

Visual invariants the Playwright script checks (per chapter):

1. **Single H1**: exactly one `<h1>` (atlas renders chapter title; chapter body must not duplicate).
2. **No raw mystmd**: no occurrence of literal `` ```{important} ``, `` ```{tip} ``, `:::`, `{cite:t}`, or `$$` in the rendered HTML (would indicate converter failure).
3. **Math rendering**: every chapter with `$...$` source has at least one `<mjx-container>` or `<span class="MathJax">` element in DOM.
4. **Callout rendering**: callouts in source are rendered as `<aside class="callout-*">` or `<div class="callout-*">`, not raw text.
5. **Figures resolve**: every `<img>` element has a 200-status response (probe each `src` URL).
6. **Citation links**: every `{cite:t}` in source becomes an `<a href="/book/<slug>/references#ref-*">` or `<a href="/paper/*">` in DOM.
7. **Sidebar chapter list**: 8 chapters + references = 9 entries in the sidebar `<nav>`.
8. **No console errors**: `page.on('console', msg => …)` collects all console output; non-empty error stream fails the page.

Output JSON: `{chapter: {pass: bool, failures: [<list>]}}`. Any chapter with `pass: false` → end-of-run report lists the failure and the screenshot path; this does NOT block the skill from completing (the book is already live), but it surfaces the issue for fix in a follow-up `/audit-paper-book` run.

Acceptance: every chapter returns 200 in HTTP smoke; Playwright visual check returns `pass: true` for every chapter; references chapter shows ≥1 ref-card in DOM.
