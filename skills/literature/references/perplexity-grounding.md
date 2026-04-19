# Literature — Phase 1.25: Perplexity Real-Time Grounding

> Optional. Advisory only — feeds the search plan (Phase 1.5) but never enters the `.bib`.

**Purpose:** Before constructing the search plan, get a real-time pulse on the topic from Perplexity Sonar Pro. Perplexity's web-grounded answers surface the most recent terminology, named actors, and flashpoint debates — signals that OpenAlex/Scopus/WoS cannot provide because they lag.

**Hard gate:** Skip silently if `OPENROUTER_API_KEY` is not set in `/Volumes/Secrets/credentials.env`. Do not prompt, do not warn — just continue to Phase 1.5. This keeps the pipeline portable.

## Check the gate

```bash
if grep -q "^OPENROUTER_API_KEY=" /Volumes/Secrets/credentials.env 2>/dev/null; then
    source /Volumes/Secrets/credentials.env
    HAS_PERPLEXITY=1
else
    HAS_PERPLEXITY=0
fi
```

If `HAS_PERPLEXITY=0`, skip this phase and go to Phase 1.5. If `HAS_PERPLEXITY=1`, continue.

## Call Sonar Pro via OpenRouter

```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "model": "perplexity/sonar-pro",
  "messages": [
    {"role": "system", "content": "You are a research assistant. Given a topic, return: (1) the 3-5 most-cited or most-discussed papers from the last 24 months, (2) current terminology and named actors, (3) active debates or flashpoints, (4) adjacent subfields worth searching. Be terse. Flag anything contested or still unresolved. Do not fabricate — if uncertain, say so."},
    {"role": "user", "content": "Topic: <topic query>. What does the current landscape look like?"}
  ]
}
EOF
)" > /tmp/lit-search/perplexity-grounding.json
```

## Use the output to inform Phase 1.5

1. **Extract named papers** from Perplexity's response — add DOIs/titles to the Phase 2 verification queue (they must still pass the DOI gate — Perplexity is a lead, not a source of truth).
2. **Extract current terminology** — adjust Phase 1.5 Track A queries to use the vocabulary the field is actually using today (e.g., "gut microbiome" vs "gut flora").
3. **Extract flashpoints** — add these as Track A queries if not already covered.
4. **Extract adjacent subfields** — consider as Track B/C expansion candidates.

## Constraint — never cite Perplexity directly

Every paper Perplexity names must be independently verified via `scholarly scholarly-verify-dois` in Phase 4. Perplexity's role is to prevent the search plan from being stale, not to bypass the DOI gate. Treat any paper surfaced here exactly as you would a paper from Google Scholar: as a candidate, not a confirmed source.

## Cost note

Sonar Pro via OpenRouter is ~$0.003-0.015 per query depending on context. Budget one call per `/literature` invocation unless the deep loop runs (Phase 4.5 may trigger additional calls for gap-specific grounding).
