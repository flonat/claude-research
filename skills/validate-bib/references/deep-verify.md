# Deep Verification Mode

> Triggered by: `--deep-verify` flag, or when the .bib has 40+ entries, or when the user says "deep verify" / "verify all references".

This mode spawns parallel sub-agents that each verify a batch of entries and write structured results to disk -- bypassing context window limits entirely.

## Architecture

```
You (orchestrator)
+-- Read .bib file, extract all entries
+-- Create verification_results/ directory in project root
+-- Batch entries into groups of 5
+-- Spawn parallel agents (max 5 concurrent), each:
|   +-- For each entry in batch:
|   |   +-- Verify DOI resolves (via biblio MCP scholarly_verify_dois)
|   |   +-- Check title matches DOI metadata
|   |   +-- Check author consistency
|   |   +-- Check year correctness
|   |   +-- Check for published version if preprint
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
- Instructions to use biblio MCP tools for verification
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
