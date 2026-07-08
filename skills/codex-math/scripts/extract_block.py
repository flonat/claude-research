#!/usr/bin/env python3
"""extract_block.py — pull a theorem/proof block (+ referenced equations) from a .tex file.

Part of the `codex-math` skill (Theorist Toolbox, Moran Koren — adapted for the user's
system: the original shipped as `extract_block.sh`; reimplemented in stdlib Python for
robust LaTeX-environment parsing).

Usage:
    python3 extract_block.py <file.tex> <pattern>

<pattern> matches either a label (`\\label{<pattern>}`) or literal text appearing on the
line that opens the block (e.g. "Theorem 1", "prop:concavity"). The script prints, to
stdout:
  1. the enclosing theorem-like environment (theorem/lemma/proposition/corollary/
     definition/claim/remark), extended through an immediately following proof env;
  2. any displayed equations (equation/align/gather/multline, starred or not) whose
     \\label is \\ref/\\eqref/\\cref'd inside that block.

This gives Codex (via the `codex-research` agent) a clean, self-contained block to verify
or extend, without the caller pasting context by hand. It does NOT call Codex itself.

Exit codes: 0 ok · 1 bad usage / missing file · 2 pattern not found.
"""
from __future__ import annotations

import re
import sys

THM_ENVS = ("theorem", "lemma", "proposition", "corollary", "definition", "claim", "remark")
EQ_ENVS = ("equation", "align", "gather", "multline", "eqnarray")


def _envs_alt(envs: tuple[str, ...]) -> str:
    # match `name` and `name*`
    return "|".join(re.escape(e) for e in envs)


def find_anchor(lines: list[str], pattern: str) -> int:
    """Return the 0-based index of the first line matching the pattern (label or text)."""
    label_re = re.compile(r"\\label\{" + re.escape(pattern) + r"\}")
    for i, line in enumerate(lines):
        if label_re.search(line) or pattern in line:
            return i
    raise LookupError(pattern)


def enclosing_block(lines: list[str], anchor: int) -> tuple[int, int]:
    """Find the theorem-like environment enclosing/closest-above the anchor, extend through
    a following proof env. Returns (start, end) inclusive 0-based line indices."""
    begin_re = re.compile(r"\\begin\{(" + _envs_alt(THM_ENVS) + r")\*?\}")
    # Walk backward for the nearest \begin of a theorem-like env.
    start = None
    env = None
    for i in range(anchor, -1, -1):
        m = begin_re.search(lines[i])
        if m:
            start = i
            env = m.group(1)
            break
    if start is None:
        # No enclosing env: fall back to a small window around the anchor.
        return (max(0, anchor - 2), min(len(lines) - 1, anchor + 8))

    end_re = re.compile(r"\\end\{" + re.escape(env) + r"\*?\}")
    end = None
    for i in range(start, len(lines)):
        if end_re.search(lines[i]):
            end = i
            break
    if end is None:
        end = min(len(lines) - 1, start + 40)

    # Extend through an immediately-following proof environment (allow blank lines between).
    proof_begin = re.compile(r"\\begin\{proof\}")
    proof_end = re.compile(r"\\end\{proof\}")
    j = end + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines) and proof_begin.search(lines[j]):
        for k in range(j, len(lines)):
            if proof_end.search(lines[k]):
                end = k
                break
    return (start, end)


def referenced_labels(block: str) -> list[str]:
    refs = re.findall(r"\\(?:eqref|ref|cref|Cref)\{([^}]*)\}", block)
    out: list[str] = []
    for r in refs:
        for part in r.split(","):
            part = part.strip()
            if part and part not in out:
                out.append(part)
    return out


def equation_blocks_for(lines: list[str], labels: list[str]) -> list[str]:
    """Return the source of any displayed-equation environment carrying one of `labels`."""
    if not labels:
        return []
    begin_re = re.compile(r"\\begin\{(" + _envs_alt(EQ_ENVS) + r")\*?\}")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        m = begin_re.search(lines[i])
        if not m:
            i += 1
            continue
        env = m.group(1)
        end_re = re.compile(r"\\end\{" + re.escape(env) + r"\*?\}")
        j = i
        while j < n and not end_re.search(lines[j]):
            j += 1
        chunk = "\n".join(lines[i : j + 1])
        if any(re.search(r"\\label\{" + re.escape(lbl) + r"\}", chunk) for lbl in labels):
            out.append(chunk)
        i = j + 1
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        sys.stderr.write("usage: extract_block.py <file.tex> <pattern>\n")
        return 1
    path, pattern = argv[1], argv[2]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        sys.stderr.write(f"extract_block: cannot read {path}: {exc}\n")
        return 1

    try:
        anchor = find_anchor(lines, pattern)
    except LookupError:
        sys.stderr.write(f"extract_block: pattern not found: {pattern}\n")
        return 2

    start, end = enclosing_block(lines, anchor)
    block_lines = lines[start : end + 1]
    block = "\n".join(block_lines)

    sys.stdout.write(f"% --- block: {pattern}  (lines {start + 1}-{end + 1} of {path}) ---\n")
    sys.stdout.write(block + "\n")

    eqs = equation_blocks_for(lines, referenced_labels(block))
    if eqs:
        sys.stdout.write("\n% --- referenced equations ---\n")
        sys.stdout.write("\n\n".join(eqs) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
