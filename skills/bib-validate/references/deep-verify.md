# Deep Verification Mode

> Triggered by: `--deep-verify` flag, or when the .bib has 40+ entries, or when the user says "deep verify" / "verify all references".

This mode spawns parallel sub-agents that each verify a batch of entries and write structured results to disk -- bypassing context window limits entirely.

## Architecture

**MCP constraint:** MCP tools (`scholarly_verify_dois`, `scholarly_search`, etc.) are NOT available inside sub-agents — they are permission-scoped to the main conversation context only. The orchestrator must handle all MCP calls, and sub-agents must use Crossref REST API and WebFetch for DOI verification.

```
You (orchestrator)
+-- Read .bib file, extract all entries
+-- **Pre-verify all DOIs via MCP (main context):**
|   +-- Call `scholarly_verify_dois` with all DOIs (max 50 per call)
|   +-- Write results to verification_results/mcp_preverify.json
+-- Create verification_results/ directory in project root
+-- Batch entries into groups of 5
+-- Spawn parallel agents (max 5 concurrent), each:
|   +-- Read mcp_preverify.json for pre-verified DOI status
|   +-- For each entry in batch:
|   |   +-- If DOI pre-verified as VERIFIED: check title match only
|   |   +-- If DOI NOT_FOUND or SINGLE_SOURCE: verify via Crossref API (curl)
|   |   +-- Check title matches DOI metadata
|   |   +-- Check author consistency
|   |   +-- Check year correctness
|   |   +-- Check for published version if preprint (via WebSearch, NOT MCP)
|   +-- Write results to verification_results/batch_N.json
+-- Wait for all agents to complete
+-- Read all batch JSON files
+-- Merge into verification_results/full_report.json
+-- Generate markdown summary highlighting entries needing attention
```

## Batch JSON Format

Each agent writes a file `verification_results/batch_N.json`:

```json
[
  {
    "cite_key": "Author2020-ab",
    "doi_valid": true,
    "title_match": true,
    "author_match": true,
    "year_correct": true,
    "preprint_status": "published_version_exists",
    "published_doi": "10.1234/...",
    "issues": [],
    "suggested_fixes": {}
  }
]
```

## Agent Prompt Template

Each sub-agent receives:
- The batch of .bib entries (raw text)
- The batch number
- The output path: `verification_results/batch_N.json`
- The path to `verification_results/mcp_preverify.json` (pre-verified DOI results from orchestrator)
- Instructions to use **Crossref REST API** (`curl -sL "https://api.crossref.org/works?query.bibliographic=..."`) and **WebFetch** for DOI verification — **NOT** MCP tools (MCP is unavailable in sub-agents)
- Instruction to write results to disk only -- never return large payloads

## Assembly & Report

After all agents complete:
1. Read all `verification_results/batch_*.json` files
2. Merge into `verification_results/full_report.json`
3. Generate `verification_results/summary.md` with:
   - Total entries verified
   - Entries with issues (grouped by issue type)
   - Suggested fixes
   - Entries needing manual attention
4. Print the summary to the user

## Cleanup

After the report is delivered, offer to delete `verification_results/` or keep it for reference.
