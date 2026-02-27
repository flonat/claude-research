# Web of Science API Guide

## Overview

WoS offers two API tiers with different endpoints, pagination, and response formats. Set via `WOS_API_TIER` env var (default: `starter`).

| Feature | Starter API | Expanded API |
|---------|-------------|--------------|
| Base URL | `https://api.clarivate.com/apis/wos-starter/v1` | `https://wos-api.clarivate.com/api/wos` |
| Search endpoint | `/documents` | Root (`/`) |
| Results per page | Max 50 | Max 100 |
| Pagination | Page-based (`page=N`) | Record-based (`firstRecord=N`) |
| Abstracts | Not included | Included |
| Response format | Flat JSON | Deeply nested XML-like JSON |

**Authentication:** `X-ApiKey` header for both tiers.

## Query Syntax

### Topic Search

```
TS=(machine learning)
TS=("algorithmic collusion" OR "tacit collusion")
```

`TS=()` searches title, abstract, author keywords, and Keywords Plus.

### Year Filter

```
PY=(2020-2024)          -- range (inclusive)
PY=(2023)               -- single year
```

### Combining

```
TS=("platform governance") AND PY=(2020-2025)
```

### Other Field Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `TS=()` | Topic (title + abstract + keywords) | `TS=("deep learning")` |
| `TI=()` | Title only | `TI=("neural network")` |
| `AU=()` | Author | `AU=(Smith J)` |
| `SO=()` | Source (journal name) | `SO=("Management Science")` |
| `OG=()` | Organisation | `OG=("University of Example")` |
| `DO=()` | DOI | `DO=(10.1000/example)` |
| `PY=()` | Publication year | `PY=(2020-2024)` |

## Starter API

### Request Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | WoS query string | `TS=("AI") AND PY=(2023)` |
| `limit` | Results per page (max 50) | `50` |
| `page` | Page number (1-indexed) | `1` |
| `sortField` | Sort order | `relevance`, `TC.D`, `PY.D` |
| `db` | Database | `WOS` |

### Sort Options (Starter)

| Value | Description |
|-------|-------------|
| `relevance` | Relevance (default) |
| `TC.D` | Times Cited descending |
| `PY.D` | Publication Year descending |
| `PY.A` | Publication Year ascending |

### Response Structure

```json
{
  "metadata": {
    "total": 1234,
    "page": 1,
    "limit": 50
  },
  "hits": [
    {
      "uid": "WOS:000123456789",
      "title": "Paper Title",
      "names": {
        "authors": [
          {"displayName": "Smith, John", "wosStandard": "Smith, J"}
        ]
      },
      "source": {
        "sourceTitle": "Journal Name",
        "publishYear": 2024
      },
      "identifiers": {
        "doi": "10.1000/example"
      },
      "keywords": {
        "authorKeywords": ["keyword1", "keyword2"]
      },
      "citations": [
        {"db": "wos", "count": 42}
      ]
    }
  ]
}
```

### Key Response Fields (Starter)

| Path | Description |
|------|-------------|
| `uid` | WoS accession number (e.g., `WOS:000123456789`) |
| `title` | Paper title |
| `names.authors[].displayName` | Author display name |
| `source.sourceTitle` | Journal/conference name |
| `source.publishYear` | Publication year |
| `identifiers.doi` | DOI (without prefix) |
| `keywords.authorKeywords` | Author keywords (array) |
| `citations[].count` | Citation count (filter by `db: "wos"`) |

**Note:** Starter API does **not** return abstracts.

### Pagination (Starter)

```
Page 1: page=1, limit=50
Page 2: page=2, limit=50
```

Stop when `page * limit >= metadata.total`.

## Expanded API

### Request Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `databaseId` | Database | `WOS` |
| `usrQuery` | WoS query string | `TS=("AI") AND PY=(2023)` |
| `count` | Results per page (max 100) | `100` |
| `firstRecord` | Starting record (1-indexed) | `1` |
| `sortField` | Sort order | `RS+D`, `TC+D`, `PY+D` |
| `optionView` | Response detail level | `FR` (full record) |

### Sort Options (Expanded)

| Value | Description |
|-------|-------------|
| `RS+D` | Relevance Score descending (default) |
| `TC+D` | Times Cited descending |
| `PY+D` | Publication Year descending |
| `PY+A` | Publication Year ascending |

### Response Structure

The Expanded API returns deeply nested JSON. Records are at:
```
data.Data.Records.records.REC
```

Each `REC` is a single record:

```json
{
  "UID": "WOS:000123456789",
  "static_data": {
    "summary": {
      "titles": {
        "title": [
          {"type": "item", "content": "Paper Title"},
          {"type": "source", "content": "Journal Name"}
        ]
      },
      "names": {
        "name": [
          {"role": "author", "display_name": "Smith, John", "full_name": "Smith, John"}
        ]
      },
      "pub_info": {
        "pubyear": "2024"
      }
    },
    "fullrecord_metadata": {
      "keywords": {
        "keyword": ["keyword1", "keyword2"]
      },
      "abstracts": {
        "abstract": {
          "abstract_text": {
            "p": "Abstract text here..."
          }
        }
      }
    }
  },
  "dynamic_data": {
    "citation_related": {
      "tc_list": {
        "silo_tc": [
          {"coll_id": "WOS", "local_count": "42"}
        ]
      }
    },
    "cluster_related": {
      "identifiers": {
        "identifier": [
          {"type": "doi", "value": "10.1000/example"}
        ]
      }
    }
  }
}
```

### Key Paths (Expanded)

| Path | Description |
|------|-------------|
| `UID` | WoS accession number |
| `static_data.summary.titles.title` | Array; `type: "item"` = title, `type: "source"` = journal |
| `static_data.summary.names.name` | Author list; filter by `role: "author"` |
| `static_data.summary.pub_info.pubyear` | Publication year |
| `static_data.fullrecord_metadata.keywords.keyword` | Keywords |
| `static_data.fullrecord_metadata.abstracts.abstract.abstract_text.p` | Abstract (string or array of paragraphs) |
| `dynamic_data.citation_related.tc_list.silo_tc` | Citation counts; filter by `coll_id: "WOS"` |
| `dynamic_data.cluster_related.identifiers.identifier` | DOI; filter by `type: "doi"` |

**Warning:** Many of these fields can be either a single object or an array. Always normalise to array before iterating.

### QueryID for Subsequent Pages

The first request returns a `QueryID` in `QueryResult`:
```json
{"QueryResult": {"QueryID": 12345, "RecordsFound": 500}}
```

Use it for subsequent pages:
```
GET /query/12345?count=100&firstRecord=101&sortField=RS+D&optionView=FR
```

### Pagination (Expanded)

```
Request 1: firstRecord=1,   count=100
Request 2: firstRecord=101, count=100  (use QueryID)
Request 3: firstRecord=201, count=100  (use QueryID)
```

Stop when `firstRecord > RecordsFound`.

## Common Query Patterns

### Highly Cited Papers on a Topic

```
q: TS=("platform governance") AND PY=(2020-2025)
sortField: TC.D          (Starter) / TC+D (Expanded)
limit: 50
```

### Year-by-Year Trend Counts

Run one query per year with `limit=1` (Starter) or `count=0` (Expanded) and read the total:

**Starter:**
```
q: TS=("algorithmic collusion") AND PY=(2023)
limit: 1
→ metadata.total
```

**Expanded:**
```
usrQuery: TS=("algorithmic collusion") AND PY=(2023)
count: 0
firstRecord: 1
→ QueryResult.RecordsFound
```

## Error Handling

### HTTP Status Codes

- `200` — Success
- `400` — Bad query syntax
- `401` — Invalid API key
- `403` — Forbidden (check subscription tier)
- `404` — Not found
- `429` — Rate limit exceeded

### Common Pitfalls

1. **Starter has no abstracts** — switch to Expanded tier if abstracts are needed
2. **Expanded response is deeply nested** — `Data.Records.records.REC` can be a single object or array
3. **Single-element arrays collapse** — `names.name` may be `{}` instead of `[{}]` when only one author
4. **DOI can be in multiple locations** — check `dynamic_data.cluster_related.identifiers`, then `static_data.summary.identifiers`, then `static_data.item.ids`
5. **Sort field syntax differs** — Starter uses `.` separator (`TC.D`), Expanded uses `+` (`TC+D`)
6. **QueryID is only for Expanded** — Starter uses standard page-based pagination

## Additional Resources

- WoS Starter API docs: https://developer.clarivate.com/apis/wos-starter
- WoS Expanded API docs: https://developer.clarivate.com/apis/wos
- Query language reference: https://images.webofknowledge.com/images/help/WOS/hs_search_rules.html
