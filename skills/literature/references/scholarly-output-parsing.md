# Parsing `scholarly` CLI JSON Output

The `scholarly` CLI writes initialization log lines to stderr but they often interleave with stdout when redirected via `> file.json` or `2>&1`. Naive `json.load(open(path))` fails on the leading non-JSON noise.

## Symptom

```
[mcp-scholarly] Loading source adapters...
[mcp-scholarly] OpenAlex: ready
{
  "tool": "scholarly-paper-detail",
  "arguments": {...},
  "data": {...}
}
```

`json.load` raises `JSONDecodeError: Expecting value: line 1 column 1`.

## Helper

```python
import json
from pathlib import Path

def parse_scholarly_json(filepath: str | Path) -> dict | None:
    """Parse scholarly CLI output that may have leading log noise.

    Locates the first JSON object opening (`{"tool":` or `{\\n  "tool":`)
    and uses raw_decode to extract just the JSON payload.

    Returns the decoded dict, or None if no JSON object is found.
    """
    content = Path(filepath).read_text()
    # Find the first JSON object — try pretty-printed then compact
    idx = content.find('{\n  "tool":')
    if idx == -1:
        idx = content.find('{"tool":')
    if idx == -1:
        return None
    obj, _ = json.JSONDecoder().raw_decode(content[idx:])
    return obj


def get_paper_data(filepath: str | Path) -> dict | None:
    """Convenience: return the `data` field directly (the actual paper payload)."""
    parsed = parse_scholarly_json(filepath)
    return parsed.get("data") if parsed else None
```

## Usage in sub-agents

```bash
# Sub-agent shells out:
scholarly arxiv-get-paper --arxiv-id 1904.02868 > /tmp/lit/ghorbani-zou.json 2>&1

# Parsing step:
uv run python -c "
from pathlib import Path
import sys
sys.path.insert(0, '$HOME/.claude/skills/literature/references')
exec(Path('$HOME/.claude/skills/literature/references/scholarly-output-parsing.md').read_text().split('\`\`\`python')[1].split('\`\`\`')[0])
data = get_paper_data('/tmp/lit/ghorbani-zou.json')
print(data['title'], '|', data['doi'])
"
```

For repeated use, copy the helper into a project-local `code/scholarly_helper.py` rather than exec-from-markdown.

## Why this matters

- `mcp-scholarly` adapter banner (`[mcp-scholarly] Loading...`) is printed unconditionally on init even when calling the CLI binary directly.
- Pre-existing pattern of `json.load(open(path))` in Phase 2/3 helpers fails silently on noisy output, then returns no candidates — producing zero-result Phase 2 searches that look like "no papers exist on this topic" rather than "parsing broke".
- Documented after the 2026-05-04 false-name-proof-data-attribution literature pull where this exact failure mode wasted ~15 minutes of debugging.

## Alternatives considered

- **Pipe through `jq`**: works but requires `jq` available everywhere; adds shell complexity to sub-agent prompts.
- **Force CLI to silence banner**: `mcp-scholarly` has no `--quiet` flag as of 2026-05-04. Filed as enhancement candidate.
- **Use Python MCP client directly**: defeats the point of CLI-fronted access from sub-agents (per `subagent-prompt-discipline` rule).
