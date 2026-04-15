# Sources Cache Protocol

> Cache bibliometric and literature search results to avoid redundant API calls across sessions. Two tiers: project-level (shared with collaborators) and central (personal, cross-project).

## Why Cache

1. **API rate limits** — OpenAlex, Scopus, and WoS have daily/monthly quotas
2. **Reproducibility** — cached results document what was found at a specific point in time
3. **Speed** — skip redundant searches when revisiting a topic within days
4. **Cost** — Exa and some other services charge per query

## Cache Locations

| Tier | Location | Scope | Committed? |
|------|----------|-------|-----------|
| **Project** | `<project>/.cache/literature/` | One research project | No (gitignored) |
| **Central** | `~/.cache/claude-literature/` | All projects | No |

The project cache takes precedence over the central cache (more specific context).

## Cache Format

Each cached result is a JSON file named by query hash:

```
<cache-dir>/<source>/<sha256-of-query>.json
```

```json
{
  "query": "human-AI collaboration MCDM",
  "source": "scholarly_search",
  "timestamp": "2026-04-10T14:30:00Z",
  "expires": "2026-05-10T14:30:00Z",
  "params": {"limit": 20, "year_from": 2020},
  "result_count": 15,
  "results": [...]
}
```

## Expiry Rules

| Content type | Default TTL | Rationale |
|-------------|-------------|-----------|
| Search results | 30 days | New papers appear regularly |
| DOI metadata | 90 days | Metadata rarely changes |
| Citation counts | 14 days | Counts update frequently |
| Author profiles | 60 days | Affiliations change slowly |
| Verified DOIs | Never expires | A DOI is permanent |

## How Skills Use the Cache

### Before any search

```python
# Pseudocode — the skill checks cache before calling MCP
cache_key = sha256(f"{source}:{query}:{json.dumps(params, sort_keys=True)}")
cached = read_cache(project_cache, source, cache_key) or read_cache(central_cache, source, cache_key)
if cached and not expired(cached):
    use cached["results"]
else:
    results = call_mcp_tool(source, query, params)
    write_cache(project_cache, source, cache_key, results)
    write_cache(central_cache, source, cache_key, results)  # also populate central
```

### In practice (skill-level implementation)

Since skills run as markdown instructions (not code), the caching is implemented as a **convention**:

1. **Before searching:** Check if `<project>/.cache/literature/<source>/` exists and has recent files matching the query
2. **After searching:** Save results to cache using the Bash tool:
   ```bash
   mkdir -p .cache/literature/scholarly_search
   echo '<json>' > .cache/literature/scholarly_search/<hash>.json
   ```
3. **On cache hit:** Read the cached file instead of calling the MCP tool
4. **On cache miss or expired:** Call the MCP tool, then write to cache

### Simplified flow for most skills

For skills that don't want to implement full caching logic, use the **session dedup** pattern instead:

1. At the start of a literature search, write found papers to a temp file (`/tmp/lit-session-<topic>.json`)
2. Before each new search, check the temp file for already-found papers
3. Skip papers already in the session file

This is lighter than full caching but prevents redundant within-session searches.

## Cache Invalidation

| Trigger | Action |
|---------|--------|
| Manual: user says "fresh search" or "ignore cache" | Skip cache, overwrite with new results |
| TTL expired | Treat as cache miss |
| MCP server updated (new sources, schema changes) | Clear central cache: `rm -rf ~/.cache/claude-literature/` |
| Project `.bib` updated significantly | Clear project cache for that topic |

## Gitignore Setup

Add to project `.gitignore`:
```
.cache/
```

The central cache is outside any repo, so no gitignore needed.

## Which Skills Should Cache

| Skill | Cache tier | What to cache |
|-------|-----------|---------------|
| `/literature` | Project + Central | Search results, paper metadata |
| `/bib-validate` | Central | DOI verification results |
| `/scout` | Central | Novelty search results, venue data |
| `/gather-readings` | Project | PDF availability checks |
| `/radar` | Central | Topic monitoring searches |

## Relationship to Paperpile

Paperpile IS the permanent cache for papers you've decided to keep. The sources cache is for **search results** — the step before a paper enters Paperpile. Don't duplicate Paperpile's role; cache the search, not the paper.
