#!/usr/bin/env python3
"""Batch audit of paper-book companions — deterministic Phase 1 + Phase 2.

Implementation of the read-only checks documented in:
  - skills/audit-paper-book/references/phase-1-diff-inventory.md
  - skills/audit-paper-book/references/phase-2-accessibility.md

Walks every book in the registry (or one named slug) and produces a
per-book audit report at `~/vault/books/<slug>/.audit-report-<date>.md`.

Reads atlas + book registry for paths — never hardcoded.

Usage:
    batch_audit.py            # audit every book in the registry
    batch_audit.py <slug>     # audit one book
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

VAULT = Path.home() / "vault"
BOOKS_ROOT = VAULT / "books"
ATLAS_ROOT = VAULT / "atlas"
REGISTRY = BOOKS_ROOT / "index.yaml"
RR_FILE = Path.home() / ".config" / "task-mgmt" / "research-root"
TODAY = date.today().isoformat()


def _research_root() -> Path:
    return Path(RR_FILE.read_text().strip()) if RR_FILE.exists() else Path()


def _registry() -> dict[str, dict]:
    if not REGISTRY.exists():
        return {}
    return {k: v for k, v in (yaml.safe_load(REGISTRY.read_text()) or {}).items()
            if isinstance(v, dict)}


def _atlas_topic_path(slug: str, entry: dict) -> Path | None:
    topic_ref = entry.get("atlas_topic", "")
    if "/" not in topic_ref:
        return None
    p = ATLAS_ROOT / f"{topic_ref}.md"
    return p if p.exists() else None


def _resolve_paper_tex(slug: str) -> Path | None:
    """Resolve the active paper's main.tex path.

    Resolution order:
      1. Registry entry's `paper_tex:` field (path relative to project root).
         Set this when the paper's .tex isn't named main.tex (e.g. ACM
         templates name it after the venue like `gecco2026.tex`).
      2. First `paper-*/paper/main.tex` under the project (canonical layout).
      3. First `paper-*/backup/main.tex` (fallback if Overleaf symlink down).

    Returns None if no candidate exists — the caller (audit driver)
    surfaces this as a visible error in the JSON summary.
    """
    reg = _registry()
    entry = reg.get(slug, {})
    topic = _atlas_topic_path(slug, entry)
    if not topic:
        return None
    m = re.match(r"^---\n(.*?)\n---\n", topic.read_text(), re.DOTALL)
    meta = (yaml.safe_load(m.group(1)) or {}) if m else {}
    project_path = meta.get("project_path", "")
    if not project_path:
        return None
    project = _research_root() / project_path

    # 1. Registry override
    override = (entry.get("paper_tex") or "").strip()
    if override:
        candidate = project / override
        if candidate.exists():
            return candidate
        # Fall through with a hint left in the caller's error path.

    # 2. Canonical Overleaf-symlink layout
    candidates = sorted(project.glob("paper-*/paper/main.tex"))
    if candidates:
        return candidates[0]
    # 3. Backup fallback
    candidates = sorted(project.glob("paper-*/backup/main.tex"))
    return candidates[0] if candidates else None

ACRONYM_ALLOW = {
    "DM", "GP", "BO", "MOBO", "MOO", "ABM", "EI", "EHVI", "MCDM", "VOI", "MAP",
    "DOI", "URL", "PDF", "JSON", "CSV", "CDF", "MSR", "ETS", "DTLZ", "DTLZ2",
    "BC", "NSGA", "SE", "KG", "DSA", "VLOP", "VLOSE", "EU", "UK", "US",
    "AI", "API", "LLM", "RAG", "IAA", "TEE", "DP", "RLHF", "SAE", "NIST",
    "OSA", "GDPR", "FAccT", "NeurIPS", "ICML", "AAAI", "CCS", "GECCO",
    "[Journal]", "AIJ", "WSC", "AAMAS", "ICPSR", "RDC", "FSRDC", "MCMC", "SOC", "ISO",
    "ACM", "IEEE", "PS", "IA", "RRE", "DGP", "MOEAs", "MOEA", "WFG", "ZDT",
    "T1", "T2", "T3", "PII", "ML", "DRL", "BNN", "FB", "MTM", "OEM", "QA",
    "GT", "TWFE", "RCT", "DAG", "OLS", "IV", "RDD", "DID", "PCA", "RBM",
    "BERT", "GPT", "T5", "VAE", "GAN", "GNN", "CNN", "RNN", "LSTM",
    "TODO", "FAQ", "HTTP", "HTTPS", "ID", "SQL", "HTML", "CSS",
    "CFP", "ECC", "BFGS", "ELBO", "KL", "MAE", "MSE", "RMSE", "AUC",
    "MIT", "EPSRC", "ESRC", "EA", "EAs", "RVEA", "SBX", "EIG", "VOC",
    "EMO", "PER", "MI", "MOR", "IDS", "SMC", "ESS", "C0", "QUIVER",
    "QUIVER-EA", "QUIVER-MOBO", "WFG4", "WFG9", "WFG6",
    "SCRTP", "HPC", "CDN", "GPU", "CPU", "SVM", "NLP", "QAOA", "OOD",
    # Decision-science / OR / stats vocabulary (universal in MCDA / OR books)
    "MCDA", "OR", "SPSS", "ICC", "UI", "OSF", "BDS",
    # Project file conventions (filenames, not jargon acronyms)
    "CLAUDE", "MEMORY", "README", "AGENTS",
    # ML / LLM universal vocabulary + hardware proper nouns
    "GLM", "DPO", "NP", "MF", "A100", "GPT-4", "GPT-3", "RLHF",
    "PEFT", "LoRA", "ICL", "CoT", "BPE",
    # Statistics / ML / benchmark vocabulary
    "YAML", "HELM", "BIG", "MPC", "SPRT", "LLR", "CUSUM",
    "HR", "RL", "CI", "FDA",
    # All-caps emphasis or Roman numerals catching the regex
    "NOT", "II", "III", "IV", "YOUR",
    # Formal-verification / theorem-proving / constraint-satisfaction tools
    "Z3", "PRISM", "SMT", "SMT-LIB2", "LP", "UNSAT", "SAT", "TAU",
    "MDP", "PCTL",
    # Academic-infrastructure / regulator roles
    "SSRN", "DSC",
    # Paper-specific algorithm / project names (per-book proper nouns)
    "CAPE-MOBO", "DES",
    # Numerical optimisation variants (hyphenated forms)
    "BFGS-B", "L-BFGS", "L-BFGS-B",
    # Evolutionary algorithm variants (hyphenated forms)
    "NSGA-II", "NSGA-III",
}


def _atlas_topic(slug: str) -> dict:
    reg = yaml.safe_load((BOOKS_ROOT / "index.yaml").read_text()) or {}
    entry = reg.get(slug, {})
    topic_ref = entry.get("atlas_topic", "")
    if "/" not in topic_ref:
        return {}
    p = ATLAS_ROOT / f"{topic_ref}.md"
    if not p.exists():
        return {}
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(), re.DOTALL)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def _expand_tex_inputs(tex_path: Path, _seen: set[Path] | None = None) -> str:
    """Read tex file and recursively expand \\input{} / \\include{} references.
    Stops at a cycle or missing file. Returns the concatenated source."""
    if _seen is None:
        _seen = set()
    tex_path = tex_path.resolve()
    if tex_path in _seen or not tex_path.exists():
        return ""
    _seen.add(tex_path)
    text = tex_path.read_text(errors="replace")
    base = tex_path.parent

    def _replace(m: re.Match) -> str:
        target = m.group(2).strip()
        candidates = [base / target, base / (target + ".tex")]
        for c in candidates:
            if c.exists():
                return "\n" + _expand_tex_inputs(c, _seen) + "\n"
        return ""

    return re.sub(r"\\(input|include|InputIfFileExists)\{([^}]+)\}", _replace, text)


def _cited_keys_from_tex(tex: str) -> set[str]:
    """Extract every key inside \\cite{...}, \\citet{...}, \\citep{...},
    \\citeauthor{...}, \\citeyear{...}. Splits comma-separated lists."""
    keys: set[str] = set()
    for m in re.finditer(r"\\cite[a-zA-Z]*\*?\{([^}]+)\}", tex):
        for k in m.group(1).split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


def _bib_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(
        r"@\w+\{([^,\s]+),", path.read_text(errors="replace")
    ))


# ── Paper section numbering ──────────────────────────────────────────────

def _paper_sections(tex: str) -> dict[str, str]:
    """Walk tex linearly. Return {section_number: title}.
    Section numbers are auto-assigned: 1, 1.1, 1.2, 2, 2.1, ...
    Honours \\appendix (resets to A, A.1, ...). Skips \\section*{} (starred)."""
    out: dict[str, str] = {}
    sec_n = 0
    sub_n = 0
    in_appendix = False
    appendix_n = 0
    for m in re.finditer(
        r"\\(?:appendix\b)|\\(section|subsection)\*?\{([^}]+)\}",
        tex,
    ):
        if m.group(0) == "\\appendix":
            in_appendix = True
            appendix_n = 0
            sub_n = 0
            continue
        # Star-form skipped
        if m.group(0).startswith("\\section*") or m.group(0).startswith("\\subsection*"):
            continue
        kind = m.group(1)
        title = m.group(2).strip()
        if kind == "section":
            if in_appendix:
                appendix_n += 1
                key = chr(ord("A") + appendix_n - 1)
            else:
                sec_n += 1
                key = str(sec_n)
            out[key] = title
            sub_n = 0
        elif kind == "subsection":
            sub_n += 1
            parent = (chr(ord("A") + appendix_n - 1) if in_appendix else str(sec_n))
            out[f"{parent}.{sub_n}"] = title
    return out


def _book_section_refs(text: str) -> list[tuple[int, str]]:
    """Find §X.Y references in book chapter text. Returns [(line_no, ref)].
    Only accepts refs whose top-level component is a digit (rejects `§X`,
    `§N` placeholders used in templates and other free letters)."""
    out: list[tuple[int, str]] = []
    # Top-level must start with a digit; subsections accept .digit or .letter.
    pat = re.compile(r"§\s*(\d+(?:\.[0-9]+)?)")
    seen_per_line: set[tuple[int, str]] = set()
    for line_no, line in enumerate(text.split("\n"), start=1):
        # Skip refs inside fenced code or table rows
        if line.lstrip().startswith("|") or line.startswith("```"):
            continue
        for m in pat.finditer(line):
            key = (line_no, m.group(1))
            if key in seen_per_line:
                continue
            seen_per_line.add(key)
            out.append(key)
    return out


# ── Numeric drift with normalisation ─────────────────────────────────────

def _normalise_numeric_haystack(text: str) -> str:
    """Normalise paper tex so book numeric tokens can be searched against it.
    Handles ±↔\\pm, %↔\\%, leading-zero variants."""
    n = text
    n = n.replace("\\pm", "±")
    n = n.replace("\\%", "%")
    # Strip whitespace around ±
    n = re.sub(r"\s*±\s*", "±", n)
    # Normalise leading-zero variants: '.91' → '0.91'
    n = re.sub(r"(?<![0-9])\.([0-9])", r"0.\1", n)
    # Strip whitespace before %
    n = re.sub(r"\s+%", "%", n)
    return n


def _normalise_numeric_needle(tok: str) -> str:
    n = tok
    n = re.sub(r"\s*±\s*", "±", n)
    n = re.sub(r"(?<![0-9])\.([0-9])", r"0.\1", n)
    n = re.sub(r"\s+%", "%", n)
    return n.strip()


_NUM_PAT = re.compile(r"[-+]?\d+\.?\d*(?:\s*[±]\s*\d+\.?\d*)?\s*%?")
_YEAR_PAT = re.compile(r"^(19|20)\d\d$")


_SECTION_REF_CTX = re.compile(
    r"(?:§|Section|Sec\.|Eq\.|Equation|Theorem|Thm\.|Fig\.|Figure|Table|Tab\.)\s*$"
)


def numeric_drift_for_chapter(chapter_text: str, paper_haystack: str,
                              limit: int = 30) -> list[dict]:
    out: list[dict] = []
    # Skip code fences and markdown tables
    cleaned = re.sub(r"```.*?```", "", chapter_text, flags=re.DOTALL)
    cleaned = re.sub(r"^\|.*$", "", cleaned, flags=re.MULTILINE)
    # Match markdown numbered list markers (`^\s*\d+\.` at line start)
    list_marker = re.compile(r"^\s*\d+\.\s")
    for line_no, line in enumerate(cleaned.split("\n"), start=1):
        # Skip lines that are pure markdown list markers — the `\d+\.` is
        # ordinal, not a numeric claim.
        if list_marker.match(line):
            line = list_marker.sub("", line, count=1)
        for m in _NUM_PAT.finditer(line):
            tok = m.group(0).strip()
            if not tok or len(tok) <= 1:
                continue
            if _YEAR_PAT.match(tok):
                continue
            # Skip pure-integer + period tokens that look like list markers
            # (e.g. "2." captured from "2. **Transparency...**")
            if re.match(r"^\d+\.\s*$", tok):
                continue
            # Skip if immediately preceded by a section/equation/figure marker
            preceding = line[: m.start()]
            if _SECTION_REF_CTX.search(preceding):
                continue
            # Skip if part of a filename like `gecco-2026.pdf`
            after = line[m.end():]
            if after.startswith(".pdf") or after.startswith(".png") or after.startswith(".csv"):
                continue
            # Skip if inside a markdown image attribute like `{#fig-X width=92%}`
            # — heuristic: % immediately after the token AND `width=` or
            # `height=` appears earlier on the same line.
            if tok.endswith("%") and (
                "width=" in preceding or "height=" in preceding
            ):
                continue
            needle = _normalise_numeric_needle(tok)
            if needle in paper_haystack:
                continue
            bare = re.sub(r"\s*%$", "", needle)
            if bare and bare != needle and bare in paper_haystack:
                continue
            if len(out) >= limit:
                return out
            out.append({"line": line_no, "value": tok, "normalised": needle})
    return out


# ── Accessibility (improved) ─────────────────────────────────────────────

def _table_line_set(text: str) -> set[int]:
    """Line numbers that are inside markdown tables (start with `|`)."""
    return {
        i for i, line in enumerate(text.split("\n"), start=1)
        if line.lstrip().startswith("|")
    }


def acronym_expanded(text: str, acronym: str) -> bool:
    """Either `Full Form (ACRONYM)` or `ACRONYM (Full Form)` form."""
    # Form 1: words... (ACRONYM)
    if re.search(rf"\([\s]*{re.escape(acronym)}[\s]*\)", text):
        return True
    # Form 2: ACRONYM (...word...)
    if re.search(
        rf"\b{re.escape(acronym)}\s*\([^)]{{4,}}\)", text
    ):
        return True
    return False


def acronyms_in_prose(text: str) -> Counter[str]:
    """Acronyms appearing outside markdown table rows, inline citations,
    and inline-code spans. Filters out citation keys (which trip the
    [A-Z][A-Z0-9]+ regex) and code identifiers."""
    # Strip mystmd citation directives ({cite:t}`Key`, {cite:p}`Key`, {cite}`Key`)
    text = re.sub(r"\{cite[a-z:]*\}`[^`]+`", "", text)
    # Strip raw LaTeX cite commands (\cite{Key}, \citep{...}, etc.)
    text = re.sub(r"\\cite[a-zA-Z]*\*?\{[^}]+\}", "", text)
    # Strip inline-code spans (`code`) — code identifiers shouldn't count
    text = re.sub(r"`[^`]+`", "", text)
    table_lines = _table_line_set(text)
    out: Counter[str] = Counter()
    for line_no, line in enumerate(text.split("\n"), start=1):
        if line_no in table_lines:
            continue
        for m in re.findall(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)*\b", line):
            out[m] += 1
    return out


def orphan_equations(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for m in re.finditer(r"\$\$.*?\$\$", text, re.DOTALL):
        tail = text[m.end():m.end() + 200]
        non_math = re.sub(r"\$[^$]*\$", "", tail)
        non_math = re.sub(r"[^A-Za-z0-9\s.,;:?!()'-]", "", non_math)
        if len(non_math.strip()) < 60:
            line = text[: m.start()].count("\n") + 1
            out.append((line, m.group(0)[:80].replace("\n", " ")))
    return out


def long_sentences(text: str, threshold: int = 40) -> list[dict]:
    out: list[dict] = []
    t = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    t = re.sub(r"^\|.*$", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*[-*]\s.*$", "", t, flags=re.MULTILINE)
    for line_no, line in enumerate(t.split("\n"), start=1):
        for sent in re.split(r"(?<=[.!?])\s+", line):
            words = sent.split()
            if len(words) > threshold:
                out.append({"line": line_no, "n_words": len(words),
                            "snippet": sent[:100]})
    return out


def hand_constructed_paper_urls(text: str) -> list[dict]:
    pat = re.compile(
        r"\[([^\]]+)\]\((?:https?://[^/]*atlas\.user\.com)?/paper/([A-Za-z0-9_-]+)\)"
    )
    out: list[dict] = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        for m in pat.finditer(line):
            out.append({"line": line_no, "label": m.group(1), "key": m.group(2)})
    return out


# ── Audit driver ─────────────────────────────────────────────────────────

def _chapter_files(slug: str, book_dir: Path) -> list[Path]:
    """Return chapter .md paths in registry order. Skips PHASE-*-VERIFIER.md
    and other non-chapter files. Falls back to glob if registry is empty."""
    reg = _registry()
    entry = reg.get(slug, {})
    chapters = entry.get("chapters") or []
    if chapters:
        return [book_dir / f"{name}.md" for name in chapters
                if (book_dir / f"{name}.md").exists()]
    # Fallback: glob, excluding hidden files + verifier outputs
    return sorted(
        p for p in book_dir.glob("*.md")
        if not p.name.startswith(".")
        and not p.name.startswith("PHASE-")
    )


def audit_book(slug: str, paper_tex_path: str) -> dict:
    book_dir = BOOKS_ROOT / slug
    if not book_dir.is_dir():
        return {"slug": slug, "error": "book vault dir missing"}

    paper_tex_file = Path(paper_tex_path)
    paper_tex = _expand_tex_inputs(paper_tex_file) if paper_tex_file.exists() else ""
    paper_haystack = _normalise_numeric_haystack(paper_tex)
    cited_keys = _cited_keys_from_tex(paper_tex)
    book_bib_keys = _bib_keys(book_dir / "references.bib")

    atlas_meta = _atlas_topic(slug)
    out0 = (atlas_meta.get("outputs") or [{}])[0]
    atlas_status = out0.get("status") or atlas_meta.get("status") or "Drafting"
    atlas_overleaf = out0.get("overleaf_link") or atlas_meta.get("overleaf_link") or ""
    atlas_doi = (out0.get("doi") or atlas_meta.get("doi") or "").strip()
    atlas_pubdate = str(out0.get("publication_date") or "").strip()

    # 1. Bibliography drift — cited in paper, missing from book bib
    bib_drift_keys = sorted(cited_keys - book_bib_keys)

    # 2. Figure parity — check by basename without extension
    book_fig_files = sorted((book_dir / "figures").glob("*")) if (book_dir / "figures").is_dir() else []
    book_fig_stems = {p.stem for p in book_fig_files}
    # Strip TeX-commented lines (anything from unescaped `%` to end of line)
    # before scanning for \includegraphics{}. Doesn't touch `\%` (literal
    # percent in math/text).
    paper_tex_uncomm = re.sub(r"(?<!\\)%[^\n]*", "", paper_tex)
    paper_fig_refs = sorted(set(re.findall(
        r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", paper_tex_uncomm
    )))
    paper_fig_stems = {Path(r).stem for r in paper_fig_refs}
    figs_only_in_paper = sorted(paper_fig_stems - book_fig_stems)
    figs_only_in_book = sorted(book_fig_stems - paper_fig_stems)

    # 3. Numeric drift — results.md + method.md, normalised
    numeric_drift: list[dict] = []
    for ch_name in ("results.md", "method.md"):
        ch_path = book_dir / ch_name
        if not ch_path.exists():
            continue
        hits = numeric_drift_for_chapter(ch_path.read_text(errors="replace"),
                                         paper_haystack, limit=30)
        for h in hits:
            h["chapter"] = ch_name
            numeric_drift.append(h)

    # 4. Structural drift — §X.Y refs in book vs paper section numbering
    paper_sections = _paper_sections(paper_tex)
    book_section_refs_by_chapter: dict[str, list[tuple[int, str]]] = {}
    for ch_path in _chapter_files(slug, book_dir):
        if ch_path.name == "intro.md":
            continue  # intro is regen-only; no chapter cross-refs here
        refs = _book_section_refs(ch_path.read_text(errors="replace"))
        if refs:
            book_section_refs_by_chapter[ch_path.name] = refs
    structural_drift: list[dict] = []
    for ch_name, refs in book_section_refs_by_chapter.items():
        for line, ref in refs:
            if ref not in paper_sections:
                structural_drift.append({
                    "chapter": ch_name, "line": line, "ref": ref,
                    "note": f"paper has no §{ref}",
                })

    # 5. Overleaf-link drift
    intro = (book_dir / "intro.md").read_text(errors="replace") if (book_dir / "intro.md").exists() else ""
    has_overleaf = "overleaf.com" in intro.lower()
    terminal = {"Accepted", "In Press", "Camera-ready", "Published", "Withdrawn"}
    is_terminal = any(str(atlas_status).startswith(t) for t in terminal)
    overleaf_drift = None
    if is_terminal and has_overleaf:
        overleaf_drift = f"Status '{atlas_status}' is terminal but intro has Overleaf link — should drop."
    elif (not is_terminal) and atlas_overleaf and not has_overleaf:
        overleaf_drift = f"Status '{atlas_status}' is in-flight + atlas has overleaf_link but intro lacks Source field."

    # 6. Masthead format
    masthead_ok = (
        bool(re.search(r"^Authors\s*\n:", intro, re.MULTILINE))
        and bool(re.search(r"^Venue\s*\n:", intro, re.MULTILINE))
        and bool(re.search(r"^Topic\s*\n:", intro, re.MULTILINE))
    )
    has_blockquote_mast = bool(
        re.search(r"^>\s+\*\*(Paper|Authors|Venue)\.\*\*", intro, re.MULTILINE)
    )

    # 6b. Published-masthead drift. When atlas status is Published the intro
    # masthead should (a) carry a Source line pointing at the DOI rather than
    # Overleaf, and (b) have a Venue line that says "Published online" rather
    # than carrying a stale R&R / In Press / Accepted marker. Both fixes are
    # deterministic — re-run regenerate_intro.py --apply to apply.
    is_published = str(atlas_status).startswith("Published")
    published_masthead_notes: list[str] = []
    if is_published:
        if atlas_doi and atlas_doi not in intro:
            published_masthead_notes.append(
                f"Atlas DOI '{atlas_doi}' not referenced in intro — add Source line via regenerate_intro.py."
            )
        STALE_VENUE_MARKERS = (
            "R&R", "Major Revision", "In Press", "under revision",
            "under review", "In preparation", "Submitted", "Drafting",
            "Accepted",  # accepted-but-not-yet-published is now stale
        )
        venue_m = re.search(r"^Venue\s*\n:\s*([^\n]+)", intro, re.MULTILINE)
        venue_line = venue_m.group(1) if venue_m else ""
        if venue_line and "Published" not in venue_line and any(
            marker in venue_line for marker in STALE_VENUE_MARKERS
        ):
            published_masthead_notes.append(
                f"Venue line is stale ('{venue_line.strip()}') — should reference 'Published online'."
            )

    # 7. Citation-URL drift
    citation_url_hits: list[dict] = []
    for ch_path in _chapter_files(slug, book_dir):
        if ch_path.name == "intro.md":
            continue
        for h in hand_constructed_paper_urls(ch_path.read_text(errors="replace")):
            h["chapter"] = ch_path.name
            citation_url_hits.append(h)

    # Phase 2: Accessibility
    acc_block: list[dict] = []
    acc_warn: list[dict] = []
    for ch_path in _chapter_files(slug, book_dir):
        text = ch_path.read_text(errors="replace")
        acros = acronyms_in_prose(text)
        for acro, _ in acros.most_common():
            if acro in ACRONYM_ALLOW:
                continue
            if not acronym_expanded(text, acro):
                acc_block.append({"chapter": ch_path.name,
                                  "type": "missing_acronym_expansion",
                                  "acronym": acro})
        for line_no, snippet in orphan_equations(text):
            acc_block.append({"chapter": ch_path.name,
                              "type": "equation_no_prose",
                              "line": line_no, "snippet": snippet})
        for item in long_sentences(text):
            item["chapter"] = ch_path.name
            acc_warn.append(item)

    summary = {
        "slug": slug,
        "atlas_status": atlas_status,
        "bib_drift": len(bib_drift_keys),
        "figs_only_in_paper": len(figs_only_in_paper),
        "figs_only_in_book": len(figs_only_in_book),
        "structural_drift": len(structural_drift),
        "overleaf_drift": 1 if overleaf_drift else 0,
        "published_masthead_drift": len(published_masthead_notes),
        "blockquote_masthead": 1 if has_blockquote_mast else 0,
        "masthead_ok": masthead_ok,
        "citation_url_hand_constructed": len(citation_url_hits),
        "numeric_drift": len(numeric_drift),
        "accessibility_block": len(acc_block),
        "accessibility_warn": len(acc_warn),
        "paper_sections_total": len(paper_sections),
        "paper_cited_keys": len(cited_keys),
    }
    detail = {
        "bib_drift_keys": bib_drift_keys[:30],
        "figs_only_in_paper": figs_only_in_paper,
        "figs_only_in_book": figs_only_in_book,
        "structural_drift": structural_drift[:50],
        "overleaf_drift_note": overleaf_drift,
        "published_masthead_notes": published_masthead_notes,
        "citation_url_hits": citation_url_hits[:30],
        "numeric_drift_hits": numeric_drift[:30],
        "acc_block_sample": acc_block[:50],
        "acc_warn_sample": acc_warn[:20],
        "paper_sections": paper_sections,
    }
    return {"summary": summary, "detail": detail}


# ── Report rendering ─────────────────────────────────────────────────────

def render(slug: str, audit: dict) -> str:
    s = audit["summary"]
    d = audit["detail"]

    def section(title: str, items, fmt):
        if not items:
            return f"## {title}\n\n_(none)_\n"
        body = "\n".join(fmt(i) for i in items)
        return f"## {title}\n\n{body}\n"

    return "\n".join([
        f"# Audit report — {slug}",
        "",
        f"**Date:** {TODAY}",
        "**Mode:** report-only (v2: deterministic + bib-from-cite + numeric-normalised + structural-drift)",
        f"**Atlas status:** {s['atlas_status']}",
        f"**Paper structure:** {s['paper_sections_total']} sections / subsections; {s['paper_cited_keys']} distinct cited keys",
        "",
        "## Summary",
        "",
        "| Bucket | Count | Status |",
        "|---|---:|---|",
        f"| Bib drift (cited in paper, missing from book bib) | {s['bib_drift']} | {'pending — backfill' if s['bib_drift'] else 'clean'} |",
        f"| Figures missing from book | {s['figs_only_in_paper']} | {'pending' if s['figs_only_in_paper'] else 'clean'} |",
        f"| Figures only in book | {s['figs_only_in_book']} | {'informational' if s['figs_only_in_book'] else 'clean'} |",
        f"| **Structural drift** (book §X.Y refs to non-existent paper sections) | **{s['structural_drift']}** | {'pending — chapter prose edits' if s['structural_drift'] else 'clean'} |",
        f"| Overleaf-link | {s['overleaf_drift']} | {'pending' if s['overleaf_drift'] else 'clean'} |",
        f"| **Published-masthead** (DOI Source line + Venue freshness) | {s['published_masthead_drift']} | {'pending — regenerate' if s['published_masthead_drift'] else 'clean'} |",
        f"| Format — blockquote masthead | {s['blockquote_masthead']} | {'pending — regenerate' if s['blockquote_masthead'] else 'clean'} |",
        f"| Format — masthead fields complete | {'yes' if s['masthead_ok'] else 'NO'} | {'clean' if s['masthead_ok'] else 'pending'} |",
        f"| Citation-URL hand-constructed | {s['citation_url_hand_constructed']} | {'pending' if s['citation_url_hand_constructed'] else 'clean'} |",
        f"| Numeric drift (after ±/\\%/leading-zero normalisation) | {s['numeric_drift']} | {'pending — triage' if s['numeric_drift'] else 'clean'} |",
        f"| Accessibility — block tier | {s['accessibility_block']} | {'pending' if s['accessibility_block'] else 'clean'} |",
        f"| Accessibility — warn tier (long sentences) | {s['accessibility_warn']} | informational |",
        "",
        section("Bibliography drift — keys cited in paper, missing from book bib",
                d["bib_drift_keys"], lambda k: f"- `{k}`"),
        section("Figures missing from book",
                d["figs_only_in_paper"], lambda f: f"- `{f}`"),
        section("Figures only in book",
                d["figs_only_in_book"], lambda f: f"- `{f}`"),
        section("Structural drift — book references to paper sections that don't exist",
                d["structural_drift"],
                lambda h: f"- `{h['chapter']}:{h['line']}` — book says `§{h['ref']}` — {h['note']}"),
        f"## Overleaf-link drift\n\n{d['overleaf_drift_note'] or '_(clean)_'}\n",
        section(
            "Published-masthead drift (DOI Source line + Venue freshness)",
            d["published_masthead_notes"],
            lambda n: f"- {n}",
        ),
        section("Citation-URL drift — hand-constructed `/paper/<key>`",
                d["citation_url_hits"],
                lambda h: f"- `{h['chapter']}:{h['line']}` — `[{h['label']}](/paper/{h['key']})` → `` {{cite:t}}`{h['key']}` ``"),
        section("Numeric drift — tokens not found in paper tex (after normalisation)",
                d["numeric_drift_hits"],
                lambda h: f"- `{h['chapter']}:{h['line']}` — `{h['value']}` (searched for `{h['normalised']}`)"),
        section("Accessibility — block tier",
                d["acc_block_sample"],
                lambda i: f"- `{i['chapter']}` — {i['type']}" + (f": `{i.get('acronym') or i.get('snippet','')}`" if i.get('acronym') or i.get('snippet') else "")),
        section("Accessibility — long sentences (≥40 words)",
                d["acc_warn_sample"],
                lambda i: f"- `{i['chapter']}:{i['line']}` — {i['n_words']} words — \"{i['snippet']}\""),
        "## Paper section map (for reference when fixing structural drift)",
        "",
        "```",
        *[f"§{k:<8} {v}" for k, v in sorted(d["paper_sections"].items(), key=lambda kv: (len(kv[0]), kv[0]))],
        "```",
        "",
        "## Next actions",
        "",
        "1. If bib drift > 0: copy missing entries from paper bib to book bib OR re-run `paperpile` lookup.",
        "2. If structural drift > 0: update chapter prose to use current paper section numbers (see the section map above).",
        "3. Triage numeric drift (now post-normalised — remaining hits are more likely real).",
        "4. Convert any hand-constructed `[Key](/paper/...)` links to `{cite:t}` form.",
        "5. Address accessibility block-tier (acronym expansions, equation prose).",
        "",
    ])


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    reg = _registry()
    slugs = [target] if target else list(reg.keys())
    summaries = []
    for slug in slugs:
        if slug not in reg:
            print(f"  {slug}: not in registry — skipping", file=sys.stderr)
            continue
        tex_path = _resolve_paper_tex(slug)
        if not tex_path:
            msg = ("no paper tex found — add `paper_tex:` to the registry "
                   "entry pointing at the canonical .tex (path relative to "
                   "project root), or rename to paper-*/paper/main.tex.")
            print(f"  {slug}: {msg}", file=sys.stderr)
            # Surface in JSON so audits never silently drop a registered book.
            summaries.append({"slug": slug, "error": msg,
                              "atlas_status": "unknown"})
            continue
        audit = audit_book(slug, str(tex_path))
        if "error" in audit:
            print(f"  {slug}: {audit['error']}", file=sys.stderr)
            continue
        report = render(slug, audit)
        out_path = BOOKS_ROOT / slug / f".audit-report-{TODAY}.md"
        out_path.write_text(report)
        summaries.append(audit["summary"])
        print(f"  wrote {out_path}", file=sys.stderr)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
