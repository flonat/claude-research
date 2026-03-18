#!/usr/bin/env python3
"""
AI Pattern Density Scanner

Scans text or LaTeX files for AI-generated writing patterns and reports density scores.
Based on Weiai Wayne Xu's CommScribe anti-AI pattern catalogue (286 patterns, 10 categories).

Usage:
    uv run python .scripts/ai_pattern_density.py <file>              # Scan a file
    uv run python .scripts/ai_pattern_density.py <file> --sections   # Per-section breakdown (LaTeX)
    uv run python .scripts/ai_pattern_density.py <file> --json       # Machine-readable output
    uv run python .scripts/ai_pattern_density.py --stdin              # Read from stdin

Density thresholds (patterns per 100 words):
    < 0.5  Excellent   Indistinguishable from human
    0.5-1.0  Good      Minor patterns, likely passes detection
    1.0-2.0  Caution   Some patterns, may flag detectors
    2.0-3.0  Poor      Noticeable AI patterns
    > 3.0  Bad         Clearly AI-generated

Attribution: Pattern catalogue from github.com/weiaiwayne/commscribe
"""

import re
import sys
import json
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Pattern catalogue (10 categories, 286 patterns)
# ---------------------------------------------------------------------------

@dataclass
class PatternCategory:
    name: str
    patterns: list[str]
    # Patterns that need word-boundary matching (short words that would false-positive)
    word_boundary: bool = False


CATEGORIES: list[PatternCategory] = [
    PatternCategory(
        name="Generic Openers",
        patterns=[
            "in today's", "in recent years", "in the realm of", "in the world of",
            "in the context of", "in the field of", "in this day and age",
            "throughout history", "since the dawn of time", "as we navigate",
            "as we delve into", "as technology continues to evolve",
            "with the rise of", "with the advent of",
            "with the increasing importance of", "given the importance of",
            "when it comes to", "when we think about",
            "it is no secret that", "it goes without saying that",
            "it is widely acknowledged that", "it is commonly known that",
            "it is well established that",
        ],
    ),
    PatternCategory(
        name="Importance/Noting Phrases",
        patterns=[
            "it is important to note that", "it is worth noting that",
            "it should be noted that", "it is crucial to understand that",
            "it is essential to recognize that", "it is vital to consider that",
            "it bears mentioning that", "it must be emphasized that",
            "it cannot be overstated that",
            "what's important here is", "the key point is that",
            "the crucial aspect is", "one important thing to consider is",
        ],
    ),
    PatternCategory(
        name="Overused Transitions",
        patterns=[
            "furthermore,", "moreover,", "additionally,", "in addition,",
            "consequently,", "subsequently,", "accordingly,",
            "as a result,", "in conclusion,", "to summarize,", "in summary,",
            "to sum up,", "all in all,", "on the other hand,", "conversely,",
            "nevertheless,", "nonetheless,", "that being said,",
            "with that said,", "having said that,", "that said,",
            "be that as it may,", "first and foremost,", "last but not least,",
        ],
    ),
    PatternCategory(
        name="Excessive Hedging",
        patterns=[
            "may or may not", "could potentially", "might possibly",
            "to some extent", "in some ways", "in certain respects",
            "to a certain degree", "it seems that", "it appears that",
            "it would seem that", "one could argue that",
            "some might say that", "there is a possibility that",
            "it is possible that", "it is likely that", "has the potential to",
        ],
    ),
    PatternCategory(
        name="Filler/Padding Phrases",
        patterns=[
            "a wide range of", "a variety of", "a plethora of", "a myriad of",
            "a multitude of", "an array of", "a vast array of",
            "many different", "several key",
            "plays a role in", "plays a crucial role in",
            "plays a vital role in", "plays an important role in",
            "is considered to be", "can be seen as", "is known to be",
            "is said to be", "in terms of", "with regard to",
            "with respect to", "in relation to", "pertaining to",
            "the fact that", "due to the fact that", "owing to the fact that",
            "despite the fact that", "in light of the fact that",
            "given the fact that",
        ],
    ),
    PatternCategory(
        name="Structural Patterns",
        patterns=[
            "let's dive in", "let's explore", "let's delve into",
            "let's take a closer look", "let's examine", "let's unpack",
            "let me explain", "allow me to", "i'd be happy to",
            "great question", "that's a great question",
            "here's the thing", "here's what you need to know",
            "the bottom line is", "at the end of the day",
            "when all is said and done", "moving forward", "going forward",
            "looking ahead", "consider the following",
            "the following points illustrate",
        ],
    ),
    PatternCategory(
        name="Inflated Adjectives",
        word_boundary=True,
        patterns=[
            "groundbreaking", "revolutionary", "transformative",
            "game-changing", "cutting-edge", "state-of-the-art",
            "world-class", "best-in-class", "holistic", "synergistic",
            "seamlessly", "effortlessly",
        ],
    ),
    PatternCategory(
        name="Academic AI Patterns",
        patterns=[
            "this paper explores", "this study aims to",
            "this research investigates", "the purpose of this study is to",
            "the aim of this paper is to", "we aim to contribute to",
            "this work contributes to", "fills a gap in the literature",
            "addresses a gap in", "contributes to our understanding of",
            "sheds light on", "provides insights into",
            "offers a nuanced understanding of",
            "provides a comprehensive overview of",
            "presents a systematic analysis of",
            "in line with previous research", "consistent with prior studies",
            "the findings suggest that", "the results indicate that",
            "the data reveal that", "our analysis shows that",
            "future research should", "further research is needed",
            "more research is warranted", "limitations notwithstanding",
            "despite these limitations",
        ],
    ),
    PatternCategory(
        name="Conclusion Clichés",
        patterns=[
            "in conclusion,", "to conclude,", "in closing,",
            "all in all,", "taken together,", "in the final analysis,",
            "at the end of the day,", "when all is said and done,",
            "the bottom line is", "the takeaway is", "the key takeaway is",
            "what we can learn from this is", "this goes to show that",
            "this highlights the importance of",
            "this underscores the need for", "as we move forward,",
            "only time will tell", "remains to be seen",
            "the jury is still out",
        ],
    ),
    PatternCategory(
        name="AI Vocabulary (high-frequency)",
        word_boundary=True,
        patterns=[
            "delve", "delving", "delved",
            "landscape", "tapestry", "beacon",
            "pivotal", "commendable", "meticulous",
            "intricate", "nuanced", "multifaceted",
            "underscores", "underscored", "underscoring",
            "foster", "fostering", "fostered",
            "leverage", "leveraging", "leveraged",
            "navigate", "navigating", "navigated",
            "embark", "embarking", "embarked",
            "realm", "endeavor", "endeavors",
            "aligns", "crucial",
            "robust", "comprehensive",
            "innovative", "novel",
        ],
    ),
]


# ---------------------------------------------------------------------------
# LaTeX stripping
# ---------------------------------------------------------------------------

def strip_latex(text: str) -> str:
    """Remove LaTeX commands, environments, and math to get prose-only text."""
    # Remove comments
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    # Remove \begin{...} and \end{...}
    text = re.sub(r'\\(begin|end)\{[^}]*\}', '', text)
    # Remove display math
    text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
    text = re.sub(r'\\\[.*?\\\]', '', text, flags=re.DOTALL)
    # Remove inline math
    text = re.sub(r'\$[^$]+\$', '', text)
    # Remove common commands with arguments: \cmd{arg}
    text = re.sub(r'\\(?:cite|ref|label|eqref|cref|Cref|autoref|pageref|nameref|footnote|texttt|textbf|textit|emph|url|href|includegraphics|input|bibliography|bibliographystyle)\{[^}]*\}', '', text)
    # Remove \cmd[opt]{arg}
    text = re.sub(r'\\[a-zA-Z]+\[[^\]]*\]\{[^}]*\}', '', text)
    # Remove remaining \cmd{arg} but keep the arg text for structural commands
    text = re.sub(r'\\(?:section|subsection|subsubsection|paragraph|title|author|caption)\*?\{([^}]*)\}', r'\1', text)
    # Remove other \commands
    text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
    # Remove braces
    text = re.sub(r'[{}]', '', text)
    # Remove figure/table floats content (captions already extracted)
    text = re.sub(r'\\begin\{(?:figure|table)\}.*?\\end\{(?:figure|table)\}', '', text, flags=re.DOTALL)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_sections(text: str) -> dict[str, str]:
    """Split LaTeX text into sections by \\section headings."""
    pattern = r'\\section\*?\{([^}]+)\}'
    splits = re.split(pattern, text)

    sections: dict[str, str] = {}
    if len(splits) < 2:
        return {"Full Document": text}

    # Content before first section
    preamble = splits[0].strip()
    if preamble and len(preamble.split()) > 20:
        sections["(Preamble)"] = preamble

    for i in range(1, len(splits), 2):
        name = splits[i].strip()
        body = splits[i + 1] if i + 1 < len(splits) else ""
        sections[name] = body.strip()

    return sections


# ---------------------------------------------------------------------------
# Pattern matching
# ---------------------------------------------------------------------------

@dataclass
class Match:
    category: str
    pattern: str
    count: int


@dataclass
class ScanResult:
    text_name: str
    word_count: int
    total_matches: int
    density: float
    rating: str
    matches_by_category: dict[str, list[Match]] = field(default_factory=dict)


def classify_density(density: float) -> str:
    if density < 0.5:
        return "Excellent"
    elif density < 1.0:
        return "Good"
    elif density < 2.0:
        return "Caution"
    elif density < 3.0:
        return "Poor"
    else:
        return "Bad"


def scan_text(text: str, name: str = "text") -> ScanResult:
    """Scan text for AI patterns and return results."""
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        return ScanResult(name, 0, 0, 0.0, "Excellent")

    text_lower = text.lower()
    total = 0
    by_category: dict[str, list[Match]] = {}

    for cat in CATEGORIES:
        cat_matches: list[Match] = []
        for pattern in cat.patterns:
            p = pattern.lower().rstrip(',').rstrip('.')
            if cat.word_boundary:
                count = len(re.findall(rf'\b{re.escape(p)}\b', text_lower))
            else:
                count = text_lower.count(p)
            if count > 0:
                cat_matches.append(Match(cat.name, pattern, count))
                total += count
        if cat_matches:
            by_category[cat.name] = cat_matches

    density = (total / word_count) * 100
    return ScanResult(name, word_count, total, density, classify_density(density), by_category)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

RATING_SYMBOLS = {
    "Excellent": "✅",
    "Good": "🟢",
    "Caution": "🟡",
    "Poor": "🟠",
    "Bad": "🔴",
}


def format_result(result: ScanResult, verbose: bool = True) -> str:
    lines: list[str] = []
    sym = RATING_SYMBOLS.get(result.rating, "")
    lines.append(f"\n{'='*60}")
    lines.append(f"  {result.text_name}")
    lines.append(f"{'='*60}")
    lines.append(f"  Words:     {result.word_count:,}")
    lines.append(f"  Matches:   {result.total_matches}")
    lines.append(f"  Density:   {result.density:.2f} per 100 words")
    lines.append(f"  Rating:    {sym} {result.rating}")
    lines.append(f"{'='*60}")

    if verbose and result.matches_by_category:
        lines.append("")
        for cat_name, matches in sorted(
            result.matches_by_category.items(),
            key=lambda x: sum(m.count for m in x[1]),
            reverse=True,
        ):
            cat_total = sum(m.count for m in matches)
            lines.append(f"  {cat_name} ({cat_total} hits)")
            for m in sorted(matches, key=lambda x: x.count, reverse=True):
                marker = f"x{m.count}" if m.count > 1 else ""
                lines.append(f"    - \"{m.pattern}\" {marker}".rstrip())
            lines.append("")

    return "\n".join(lines)


def format_summary_table(results: list[ScanResult]) -> str:
    """Format multiple results as a compact table."""
    lines: list[str] = []
    lines.append("")
    lines.append(f"  {'Section':<30} {'Words':>6} {'Hits':>5} {'Density':>8} {'Rating':<10}")
    lines.append(f"  {'-'*30} {'-'*6} {'-'*5} {'-'*8} {'-'*10}")
    for r in results:
        sym = RATING_SYMBOLS.get(r.rating, "")
        lines.append(
            f"  {r.text_name:<30} {r.word_count:>6,} {r.total_matches:>5} "
            f"{r.density:>7.2f} {sym} {r.rating:<10}"
        )
    return "\n".join(lines)


def result_to_dict(result: ScanResult) -> dict:
    return {
        "name": result.text_name,
        "word_count": result.word_count,
        "total_matches": result.total_matches,
        "density": round(result.density, 3),
        "rating": result.rating,
        "categories": {
            cat: [{"pattern": m.pattern, "count": m.count} for m in matches]
            for cat, matches in result.matches_by_category.items()
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scan text for AI-generated writing patterns and report density.",
        epilog="Thresholds: <0.5 Excellent, 0.5-1.0 Good, 1.0-2.0 Caution, 2.0-3.0 Poor, >3.0 Bad",
    )
    parser.add_argument("file", nargs="?", help="File to scan (.tex or plain text)")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--sections", action="store_true", help="Per-section breakdown (LaTeX only)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Summary only, no per-pattern detail")
    args = parser.parse_args()

    if args.stdin:
        raw = sys.stdin.read()
        fname = "stdin"
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)
        raw = path.read_text(encoding="utf-8", errors="replace")
        fname = path.name
    else:
        parser.print_help()
        sys.exit(1)

    is_latex = fname.endswith(".tex") or "\\documentclass" in raw[:500]

    if is_latex and args.sections:
        sections = extract_sections(raw)
        results: list[ScanResult] = []
        for sec_name, sec_text in sections.items():
            prose = strip_latex(sec_text)
            results.append(scan_text(prose, sec_name))

        # Overall
        full_prose = strip_latex(raw)
        overall = scan_text(full_prose, f"OVERALL ({fname})")
        results.append(overall)

        if args.json:
            print(json.dumps([result_to_dict(r) for r in results], indent=2))
        else:
            print(format_summary_table(results))
            if not args.quiet:
                # Show detail for overall only
                print(format_result(overall, verbose=True))
    else:
        prose = strip_latex(raw) if is_latex else raw
        result = scan_text(prose, fname)

        if args.json:
            print(json.dumps(result_to_dict(result), indent=2))
        else:
            print(format_result(result, verbose=not args.quiet))

    # Exit code: 0 if Good or better, 1 if Caution or worse
    final = overall if (is_latex and args.sections) else result  # noqa: F821
    sys.exit(0 if final.density < 1.0 else 1)


if __name__ == "__main__":
    main()
