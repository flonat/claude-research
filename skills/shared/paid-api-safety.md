# Paid API Safety Patterns

> Defensive conventions for any skill or code that spends money on external APIs. Reference this document when generating scripts that call OpenAI, Anthropic, or other metered services.

## Mandatory Safeguards

Every script that makes paid API calls **must** include all four:

| Safeguard | What it does | When it runs |
|-----------|-------------|--------------|
| **Cost estimation** | Calculate estimated cost from token counts and rates, display before proceeding | Before any API call |
| **`--dry-run` mode** | Simulate the full pipeline (file prep, chunking, validation) without submitting | On `--dry-run` flag |
| **Explicit confirmation** | Require the user to type `yes` (not just press Enter) after seeing the estimate | After cost display, before submission |
| **Call logging** | Record every API call with timestamp, endpoint, token count, and cost to a log file | On every call |

### Cost Estimation Pattern

```python
def estimate_cost(records, model, input_tpm, output_tpm):
    """Estimate cost BEFORE spending money."""
    est_input_tokens = sum(len(r["content"]) // 4 for r in records)  # rough: 1 token ~ 4 chars
    est_output_tokens = len(records) * output_tpm  # expected output per record

    cost = (est_input_tokens / 1_000_000) * RATES[model]["input"] \
         + (est_output_tokens / 1_000_000) * RATES[model]["output"]

    print(f"Records:          {len(records):,}")
    print(f"Est. input tokens:  {est_input_tokens:,}")
    print(f"Est. output tokens: {est_output_tokens:,}")
    print(f"Model:            {model}")
    print(f"Estimated cost:   ${cost:.2f}")
    return cost
```

### Dry-Run Pattern

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true",
                    help="Show what would be submitted without calling the API")
args = parser.parse_args()

if args.dry_run:
    print(f"[DRY RUN] Would submit {len(batches)} batches ({total_records:,} records)")
    print(f"[DRY RUN] Estimated cost: ${estimated_cost:.2f}")
    sys.exit(0)
```

### Confirmation Pattern

```python
def confirm_spend(estimated_cost):
    """Require explicit 'yes' before spending money."""
    response = input(f"\nThis will cost approximately ${estimated_cost:.2f}. Type 'yes' to proceed: ")
    if response.strip().lower() != "yes":
        print("Aborted.")
        sys.exit(0)
```

## Recommended Safeguards (Batch/Bulk Operations)

For jobs processing 100+ records or costing more than $1:

| Safeguard | Details |
|-----------|---------|
| **Retry with backoff** | Start at 1s, double each retry, max 5 attempts. Respect `Retry-After` headers. |
| **Job ID tracking** | Write batch/job IDs to a tracking file (JSON or CSV) so status can be checked later. |
| **Chunking** | Split large jobs into chunks (e.g., 5,000-10,000 records per batch file). |
| **Resume capability** | Track completed chunks in a state file. On restart, skip already-completed work. |

### Retry Pattern

```python
import time

def call_with_backoff(fn, *args, max_retries=5, base_delay=1.0):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return fn(*args)
        except (RateLimitError, APIConnectionError, ssl.SSLError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"[RETRY] Attempt {attempt + 1}/{max_retries} failed: {e}. "
                  f"Retrying in {delay:.0f}s...")
            time.sleep(delay)
```

### Job Tracking Pattern

```python
import json
from datetime import datetime

TRACKING_FILE = "batch_tracking.json"

def save_batch_id(batch_id, record_count, status="submitted"):
    """Save batch ID for later status checks."""
    tracking = json.loads(Path(TRACKING_FILE).read_text()) if Path(TRACKING_FILE).exists() else []
    tracking.append({
        "batch_id": batch_id,
        "records": record_count,
        "status": status,
        "submitted_at": datetime.now().isoformat()
    })
    Path(TRACKING_FILE).write_text(json.dumps(tracking, indent=2))
```

### Resume Pattern

```python
STATE_FILE = "processing_state.json"

def get_completed_chunks():
    """Load set of already-completed chunk IDs."""
    if Path(STATE_FILE).exists():
        return set(json.loads(Path(STATE_FILE).read_text()).get("completed", []))
    return set()

def mark_chunk_complete(chunk_id):
    """Record a chunk as done so it won't be re-processed."""
    state = json.loads(Path(STATE_FILE).read_text()) if Path(STATE_FILE).exists() else {"completed": []}
    state["completed"].append(chunk_id)
    Path(STATE_FILE).write_text(json.dumps(state, indent=2))
```

## Cost Estimation Rates

Reference rates for common APIs. **Always verify current pricing before submitting large jobs.**

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) | Notes |
|----------|-------|----------------------|------------------------|-------|
| OpenAI | gpt-4o | $2.50 | $10.00 | Batch API is 50% off |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | Batch API is 50% off |
| OpenAI | gpt-4.1 | $2.00 | $8.00 | Batch API is 50% off |
| OpenAI | gpt-4.1-mini | $0.40 | $1.60 | Batch API is 50% off |
| OpenAI | gpt-4.1-nano | $0.10 | $0.40 | Batch API is 50% off |
| Anthropic | claude-sonnet-4 | $3.00 | $15.00 | Batches: 50% off, prompt caching available |
| Anthropic | claude-haiku-3.5 | $0.80 | $4.00 | Batches: 50% off |

**Formula:** Always show the user the calculation, not just the result:

```
Cost = (input_tokens / 1M) x input_rate + (output_tokens / 1M) x output_rate
     = (2,500,000 / 1M) x $2.50 + (500,000 / 1M) x $10.00
     = $6.25 + $5.00
     = $11.25
```

## Error Handling Checklist

| Failure mode | Required behaviour |
|-------------|-------------------|
| Network/SSL error | Retry with backoff (do not fail immediately) |
| Rate limit (429) | Respect `Retry-After` header, then retry |
| Partial batch failure | Log which batches succeeded vs. failed; save partial results |
| Auth error (401/403) | Fail immediately with clear message (do not retry) |
| Invalid input | Validate before submission, not after spending money |
| Interrupted run | State file enables resume from last completed chunk |

## When This Applies

- Any skill that generates code calling a metered API (OpenAI, Anthropic, Google, etc.)
- Batch processing scripts (Batch API, bulk embeddings, large-scale classification)
- One-off scripts that could accidentally run up a bill (e.g., processing an entire dataset)

## When to Skip

- Free-tier APIs or APIs with no per-call cost
- Local model inference (Ollama, vLLM, etc.)
- Single-call interactions where cost is negligible (< $0.01)
