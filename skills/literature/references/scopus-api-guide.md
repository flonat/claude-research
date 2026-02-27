# Scopus API Guide (Elsevier REST API)

## Base Information

**Base URL:** `https://api.elsevier.com/content/search/scopus`
**Authentication:** Two headers required:
- `X-ELS-APIKey` — Scopus API key
- `X-ELS-Insttoken` — Institutional token (enables access from any IP; omit for campus-only access)

**Rate Limits:** Varies by subscription. Typically 2-9 requests/second, throttled per API key.

## Query Syntax

Scopus uses a field-qualified boolean query language.

### Topic Search

```
TITLE-ABS-KEY("machine learning" OR "deep learning")
```

Searches title, abstract, and keywords. Space-separated terms within `TITLE-ABS-KEY()` are implicit AND. Use `OR` between quoted phrases for broader queries.

### Subject Area Filter

```
SUBJAREA(COMP)
```

Filter by Scopus subject area codes. Common codes:
- `COMP` — Computer Science
- `BUSI` — Business, Management and Accounting
- `ECON` — Economics, Econometrics and Finance
- `DECI` — Decision Sciences
- `SOCI` — Social Sciences
- `PSYC` — Psychology
- `MATH` — Mathematics
- `ENGI` — Engineering

### Year Filters

```
PUBYEAR > 2019          -- published after 2019 (i.e. 2020+)
PUBYEAR < 2024          -- published before 2024
PUBYEAR = 2023          -- published in exactly 2023
```

Note: these are strict inequalities. To get 2020-2023, use `PUBYEAR > 2019 AND PUBYEAR < 2024`.

### Combining Filters

```
TITLE-ABS-KEY("algorithmic collusion") AND PUBYEAR > 2019 AND PUBYEAR < 2026
```

### Author and Affiliation Queries

```
AU-ID(12345678)         -- author by Scopus ID
AFFIL("University of Example")  -- affiliation search
AUTH("Smith J.")        -- author name search
```

## Request Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Full Scopus query string | `TITLE-ABS-KEY("AI")` |
| `start` | Offset for pagination (0-indexed) | `0`, `25`, `50` |
| `count` | Results per page (max 25) | `25` |
| `sort` | Sort order | `relevancy`, `-citedby-count`, `-coverDate` |
| `view` | Response detail level | `STANDARD`, `COMPLETE` |
| `field` | Limit returned fields | `dc:title,dc:creator,prism:doi` |

### Sort Options

| Value | Description |
|-------|-------------|
| `relevancy` | Relevance (default) |
| `-citedby-count` | Most cited first |
| `-coverDate` | Most recent first |
| `+coverDate` | Oldest first |
| `-pagecount` | Longest papers first |

### View Options

| View | Fields included |
|------|----------------|
| `STANDARD` | Title, authors (first only), source, DOI |
| `COMPLETE` | All of STANDARD + abstract, all authors, keywords, citation count, EID |

**Always use `COMPLETE` view** to get abstracts, full author lists, and keywords.

## Response Structure

```json
{
  "search-results": {
    "opensearch:totalResults": "1234",
    "opensearch:startIndex": "0",
    "opensearch:itemsPerPage": "25",
    "entry": [
      {
        "dc:title": "Paper Title",
        "dc:creator": "First Author",
        "author": [
          {"authname": "Smith J.", "given-name": "John", "surname": "Smith"}
        ],
        "prism:publicationName": "Journal Name",
        "prism:coverDate": "2024-01-15",
        "prism:doi": "10.1000/example",
        "citedby-count": "42",
        "dc:description": "Abstract text...",
        "authkeywords": "keyword1 | keyword2 | keyword3",
        "eid": "2-s2.0-85012345678"
      }
    ]
  }
}
```

### Key Response Fields

| Field | Description |
|-------|-------------|
| `dc:title` | Paper title |
| `dc:creator` | First author only |
| `author` | Full author list (array of objects with `authname`, `given-name`, `surname`) |
| `prism:publicationName` | Journal/conference name |
| `prism:coverDate` | Publication date (YYYY-MM-DD) |
| `prism:doi` | DOI (without `https://doi.org/` prefix) |
| `citedby-count` | Citation count (string) |
| `dc:description` | Abstract (COMPLETE view only) |
| `authkeywords` | Author keywords, pipe-separated |
| `eid` | Scopus Electronic ID (e.g., `2-s2.0-85012345678`) |

## Pagination

Scopus uses offset-based pagination:

```
Page 1: start=0,  count=25
Page 2: start=25, count=25
Page 3: start=50, count=25
```

Check `opensearch:totalResults` to know when to stop. Maximum 25 results per page.

### Detecting Empty Results

An entry with an `error` key means no results:
```json
{"entry": [{"error": "Result set was empty"}]}
```

## Common Query Patterns

### Highly Cited Papers on a Topic

```
query: TITLE-ABS-KEY("platform governance") AND PUBYEAR > 2019
sort: -citedby-count
count: 25
view: COMPLETE
```

### Recent Papers in a Subject Area

```
query: SUBJAREA(BUSI) AND TITLE-ABS-KEY("artificial intelligence") AND PUBYEAR > 2022
sort: -coverDate
count: 25
view: COMPLETE
```

### Year-by-Year Trend Counts

Run one query per year with `count=1` and read `opensearch:totalResults`:
```
query: TITLE-ABS-KEY("algorithmic collusion") AND PUBYEAR = 2023
count: 1
```

## Error Handling

### HTTP Status Codes

- `200` — Success
- `400` — Bad query syntax (check parentheses, field names)
- `401` — Invalid API key
- `403` — Rate limit exceeded or insufficient permissions
- `404` — Resource not found
- `429` — Too many requests (back off)

### Common Pitfalls

1. **Max 25 results per page** — unlike OpenAlex (200), Scopus pagination is slow
2. **Year filters are strict inequalities** — `PUBYEAR > 2019` means 2020+, not 2019+
3. **`dc:creator` is first author only** — use the `author` array for full author list
4. **Keywords are pipe-separated** — split on `|`, not comma
5. **DOI field lacks prefix** — `prism:doi` returns `10.1000/example`, not `https://doi.org/10.1000/example`
6. **InstToken is required for off-campus access** — without it, requests from non-institutional IPs will fail

## Additional Resources

- Scopus Search API docs: https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
- Query syntax guide: https://dev.elsevier.com/sc_search_tips.html
- Subject area codes: https://service.elsevier.com/app/answers/detail/a_id/15181
