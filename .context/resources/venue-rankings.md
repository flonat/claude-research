# Venue Rankings Reference

> Global reference for targeting publications — journals and conferences.
> Journals: aim for **CABS AJG 4 or 4***. Conferences: aim for **CORE A* or A**.

## Ranking Systems

| System | Venue type | Source | Scale | Notes |
|--------|-----------|--------|-------|-------|
| **CABS AJG** | Journals | Chartered Association of Business Schools | 1–4* | Most comprehensive UK business journal list |
| **SJR** | Journals | Scimago / Elsevier | Score + Q1–Q4 | Broad coverage across all disciplines |
| **FT 50** | Journals | Financial Times | Named list | 50 journals; global MBA ranking input |
| **CORE** | Conferences | Computing Research and Education (Australasia) | A*, A, B, C | Most widely used for CS/IS conferences |

## Data Files

Static CSV data for programmatic lookups:

| File | Contents | Records |
|------|----------|---------|
| `.context/resources/venue-rankings/abs_ajg_2024.csv` | CABS AJG 2024 journal rankings | 1,822 journals |
| `.context/resources/venue-rankings/core_2026.csv` | CORE ICORE 2026 conference rankings (A*–C) | ~800 conferences |
| `.context/resources/venue-rankings/CABS-AJG-2024.xlsx` | Original CABS spreadsheet (reference only) | — |

**SJR has no static file** — use the Elsevier Serial Title API for live lookups (requires `SCOPUS_API_KEY`).

### SJR Live Lookup

Query the Elsevier Serial Title API to get SJR score and CiteScore quartile for any journal:

```python
import httpx, json

async def lookup_sjr(title: str, api_key: str) -> dict | None:
    """Returns {"sjr": float, "quartile": "Q1"|"Q2"|"Q3"|"Q4"} or None."""
    r = await httpx.AsyncClient(headers={
        "X-ELS-APIKey": api_key, "Accept": "application/json",
    }).get("https://api.elsevier.com/content/serial/title",
           params={"title": title, "view": "CITESCORE"})
    if r.status_code != 200:
        return None
    entries = r.json().get("serial-metadata-response", {}).get("entry", [])
    # Match exact title (Elsevier does substring search)
    norm = lambda s: s.lower().strip().replace(".", "").replace(",", "").replace(":", "").replace("&", "and")
    entry = next((e for e in entries if norm(e.get("dc:title", "")) == norm(title)), None)
    if not entry:
        return None
    sjr_list = entry.get("SJRList", {}).get("SJR", [])
    return {"sjr": float(sjr_list[0]["$"]), "quartile": "..."} if sjr_list else None
```

The Topic Finder app (`ZZ Topic Finder/src/claude_topic_finder/services/rankings.py`) has a full implementation with quartile extraction.

---

## CORE Conference Tiers

| Tier | CORE | Meaning |
|------|------|---------|
| Tier 1 | A* | Flagship venue — top of field, highly selective (<20% acceptance) |
| Tier 2 | A | Excellent venue — strong reputation, competitive (<25% acceptance) |
| Tier 3 | B | Good venue — solid but less competitive |
| Tier 4 | C | Acceptable venue — regional or niche |

CORE Portal: https://portal.core.edu.au/conf-ranks/

---

## FT 50 List

> Source: Financial Times (https://www.ft.com/content/3405a512-5cbb-11e1-8f1f-00144feabdc0)
> Journals marked * were added in recent revisions.

1. Academy of Management Journal
2. Academy of Management Review
3. Accounting, Organizations and Society
4. Administrative Science Quarterly
5. American Economic Review
6. Contemporary Accounting Research
7. Econometrica
8. Entrepreneurship Theory and Practice
9. Harvard Business Review
10. Human Relations*
11. Human Resource Management
12. Information Systems Research
13. Journal of Accounting and Economics
14. Journal of Accounting Research
15. Journal of Applied Psychology
16. Journal of Business Ethics
17. Journal of Business Venturing
18. Journal of Consumer Psychology
19. Journal of Consumer Research
20. Journal of Finance
21. Journal of Financial and Quantitative Analysis
22. Journal of Financial Economics
23. Journal of International Business Studies
24. Journal of Management*
25. Journal of Management Information Systems*
26. Journal of Management Studies
27. Journal of Marketing
28. Journal of Marketing Research
29. Journal of Operations Management
30. Journal of Political Economy
31. Journal of the Academy of Marketing Science*
32. Management Science
33. Manufacturing and Service Operations Management*
34. Marketing Science
35. MIS Quarterly
36. Operations Research
37. Organization Science
38. Organization Studies
39. Organizational Behavior and Human Decision Processes
40. Production and Operations Management
41. Quarterly Journal of Economics
42. Research Policy*
43. Review of Accounting Studies
44. Review of Economic Studies*
45. Review of Finance*
46. Review of Financial Studies
47. Sloan Management Review
48. Strategic Entrepreneurship Journal*
49. Strategic Management Journal
50. The Accounting Review

---

---

## Conference Metadata Template

When targeting a conference in `/init-project-research`, capture:

```markdown
## Conference Target
- **Conference:** <full name> (<acronym>)
- **CORE ranking:** <A*/A/B/C>
- **Submission deadline:** <date>
- **Notification date:** <date>
- **Camera-ready date:** <date>
- **Conference dates:** <dates>
- **Location:** <city, country>
- **Page limit:** <N pages + refs>
- **Format:** <LaTeX template / style file>
- **Review type:** <double-blind / single-blind / open>
- **Anonymisation required:** <yes/no>
- **CfP link:** <URL>
```
