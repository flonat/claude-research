"""Markdown formatters for multi-source scholarly results."""

from __future__ import annotations

from sources.models import Paper


def format_papers_table(papers: list[Paper], title: str = "Results") -> str:
    """Format a list of Papers as a markdown table."""
    if not papers:
        return f"## {title}\n\nNo results found."

    lines = [f"## {title}\n"]
    lines.append("| # | Title | Authors | Year | Cited | Source | DOI |")
    lines.append("|---|-------|---------|------|-------|--------|-----|")

    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.authors[:3])
        if len(p.authors) > 3:
            authors += " et al."
        title_short = p.title[:80] + "..." if len(p.title) > 80 else p.title
        doi_link = f"[link]({p.doi})" if p.doi else "—"
        source = p.source_name or "—"
        if len(source) > 30:
            source = source[:27] + "..."

        lines.append(
            f"| {i} | {title_short} | {authors} | {p.publication_year} | "
            f"{p.cited_by_count:,} | {source} | {doi_link} |"
        )

    return "\n".join(lines)


def format_verification_table(results: dict[str, Paper | None]) -> str:
    """Format DOI verification results as a markdown table."""
    lines = ["## DOI Verification Results\n"]
    lines.append("| # | DOI | Title | Year | Cited By | Verified By | Status |")
    lines.append("|---|-----|-------|------|----------|-------------|--------|")

    verified_count = 0
    single_count = 0
    not_found_count = 0

    for i, (doi, paper) in enumerate(results.items(), 1):
        if paper is None:
            status = "NOT FOUND"
            not_found_count += 1
            lines.append(f"| {i} | `{doi}` | — | — | — | — | ❌ {status} |")
        else:
            sources = ", ".join(paper.verified_by)
            if len(paper.verified_by) >= 2:
                status = "VERIFIED"
                verified_count += 1
            else:
                status = "SINGLE SOURCE"
                single_count += 1
            title_short = paper.title[:60] + "..." if len(paper.title) > 60 else paper.title
            lines.append(
                f"| {i} | `{doi}` | {title_short} | {paper.publication_year} | "
                f"{paper.cited_by_count:,} | {sources} | "
                f"{'✅' if status == 'VERIFIED' else '⚠️'} {status} |"
            )

    lines.append("")
    lines.append(f"**Summary:** {verified_count} verified (2+ sources), "
                 f"{single_count} single-source, {not_found_count} not found")

    return "\n".join(lines)


def format_source_status(sources: list[dict]) -> str:
    """Format source status as a markdown table."""
    lines = ["## Scholarly Source Status\n"]
    lines.append("| Source | Status | Key |")
    lines.append("|--------|--------|-----|")

    for s in sources:
        status = "✅ Active" if s["active"] else "❌ Not configured"
        key = s.get("key", "—")
        lines.append(f"| {s['name']} | {status} | `{key}` |")

    return "\n".join(lines)
