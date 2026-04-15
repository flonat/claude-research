# Bibliography MCP — Known Issues & Learnings

## Known Issues

### S2 `scholarly_paper_detail` returns wrong journal names

Semantic Scholar maps journal abbreviations incorrectly for some management journals:

| S2 returns | Actual journal |
|-----------|---------------|
| Southern Medical Journal | Strategic Management Journal |
| Quality Engineering | Journal of Management Studies |

**Impact:** BibTeX from `citationStyles` field and `venue` metadata are wrong.
**Mitigation:** Always cross-check journal names against CrossRef DOI lookup or `scholarly_verify_dois` results.

### `scholarly_search` unreliable for specific known papers

Returns noisy, irrelevant results when searching for a specific paper by author + title + year (e.g., management papers return medical/biology results).

**Impact:** Cannot reliably find seminal papers in management/org theory.
**Mitigation:** Use CrossRef API directly for targeted lookups:
```bash
curl -sL "https://api.crossref.org/works?query.bibliographic=URL-encoded+title+author&rows=3"
```
Reserve `scholarly_search` for broad topic discovery only.

## Citations

[LEARN:citation] S2 "Southern Medical Journal" → Strategic Management Journal (SMJ abbreviation collision)
[LEARN:citation] S2 "Quality Engineering" → Journal of Management Studies (JMS abbreviation collision)
