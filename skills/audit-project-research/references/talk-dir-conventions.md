# Talk Directory Conventions (audit reference — Phase 4.7)

Conventions for conference/seminar talk decks and their `links.example.com` landing pages.
Produced by `/talk-deck` (deck) + `/talk-page` (QR slide + landing page). **Report-only** in
the audit — talk artefacts are not scaffolded by `/init-project-research`.

## Two folder patterns

| Pattern | Use when | Talk dir | Deck filename |
|---|---|---|---|
| **Archival venue talk** (default) | the talk presents a paper published *at that venue* (GECCO, FAccT proceedings) | `paper-{venue}/talk/` | `{venue}-talk.tex` |
| **Non-archival / seminar talk** | work *not* published at the host (a seminar, invited talk, non-archival workshop) | `presentations/` (shared, multi-deck) | descriptive, e.g. `{event}-{year}.tex` |

`presentations/` is correct — not a defect — for non-archival talks. Do **not** flag an
mcdm-style seminar deck for living outside `paper-{venue}/talk/`.

## Expected `talk/` layout (archival pattern)

```
paper-{venue}/talk/
├── {venue}-talk.tex          # deck (user-beamer[inst] OR a conference official template)
├── user-beamer.sty         # present iff using user-beamer (not a conference template)
├── speaker-script.md         # timed spoken script (cumulative timings, cue markers, Q&A)
├── references.bib            # only what the deck cites; every entry verified
├── .latexmkrc                # engine per template: lualatex (fontspec) or pdflatex+bibtex
├── figures/                  # result figures + qr-{slug}.png
├── links/{slug}/index.html   # landing-page SOURCE OF TRUTH ({slug} = {venue}{year})
└── out/                      # build artefacts
```

The deployed copy lives separately in `Task-Management/deploy/vps/links/{slug}/`
(index.html + slides.pdf + institution logo) — served at `links.example.com/{slug}/`.

## What to flag

| Check | Flag if… |
|---|---|
| **Source-of-truth** | landing page exists only in `deploy/vps/links/{slug}/` with no project-local `talk/links/{slug}/index.html`. |
| **Speaker script** | no `speaker-script.md` next to the deck. |
| **Deck naming** | archival deck not named `{venue}-talk.tex` (cosmetic — note, don't block). |
| **QR subtitle accuracy** | the thank-you slide's "slides · paper · …" subtitle promises a resource (e.g. "related work") the landing page has no card for. |
| **Paper link** | landing page links a local `paper.pdf` when a DOI exists — prefer the DOI (resolves by talk time, lighter to serve). |
| **Build engine** | `.latexmkrc` engine mismatched to the template (user-beamer needs lualatex/xelatex for fontspec; conference pdflatex templates need `$pdf_mode=1`). |
| **Overleaf separation** | the `talk/` dir is fine for `.tex`/`.bib`/figures/`scripts/`; flag stray data or the deck being placed inside the `paper/` Overleaf symlink. |
| **QR target** | `qr-{slug}.png` should encode `https://links.example.com/{slug}` (the trailing-slash URL is used in shared links to avoid the relative-asset 404). |

## Reference instances

- `ASG/example-project-c/paper-acm-facct/talk/` — canonical template (user-beamer `[bath]`).
- `OR/example-project-i/paper-acm-gecco/talk/` — conference official-template variant (GECCO).
- `OR/example-project-f/presentations/` — non-archival/seminar pattern.

## Cross-references

- `skills/talk-deck/SKILL.md` — builds the deck + speaker script.
- `skills/talk-page/SKILL.md` — QR thank-you frame + landing page + deploy.
- `docs/guides/small-websites.md` — the `links.example.com` serving model.
