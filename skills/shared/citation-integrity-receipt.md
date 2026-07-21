# Citation Integrity Receipt Contract

This contract composes two existing checks into one auditable outcome. It does
not define a new research judgment and does not transfer ownership between the
producers.

## Ownership boundary

| Component | Canonical producer | Owns | Must not do |
|---|---|---|---|
| `bibliography` | `bib-validate` | Citation inventory, record identity/DOI, retraction and update notices, preprint/version status | Read source papers to judge prose claims |
| `claims` | `claim-verify` | Claim-to-source attachment, strength/scope fidelity, source access, exact quotation fidelity | Re-resolve bibliography metadata or re-run retraction/version checks |
| Assembly | `shared/scripts/assemble_integrity_receipt.py` | Hash artifacts, validate fragments, derive verdicts, reject incompatible inputs, render a receipt | Fetch metadata or papers, assess claims, or edit manuscript/bibliography files |

`pre-submission-report --citation-integrity-only` orchestrates the two
producers and the assembler. It performs no citation checks of its own.

## Files and frozen scope

Each producer writes its normal timestamped Markdown report plus a typed
companion with the same stem:

```
reviews/<scope>/<producer>/<timestamp>.md
reviews/<scope>/<producer>/<timestamp>.citation-integrity.json
```

The orchestrator writes the full receipt beside its normal report:

```
reviews/<scope>/pre-submission-report/<timestamp>.md
reviews/<scope>/pre-submission-report/<timestamp>.citation-integrity.json
```

Before either component runs, create one artifact manifest containing every
in-scope `.tex` file and every loaded external `.bib` file. Paths are
project-relative and each file carries a lowercase SHA-256 digest. Both
components copy the same `scope` and `artifacts` values into their companions.
The assembler rejects any path, scope, or digest mismatch; it never combines
merely "recent" reports.

For an individual run, the producer may create the manifest itself. Use a
stable scope such as `full-manuscript`; for a bounded audit use a descriptive
scope such as `section-3` and list only the manuscript files that define it.

## Component JSON

Every component companion has this shape:

```json
{
  "kind": "citation-integrity-component",
  "schema_version": 1,
  "ruleset_version": "citation-integrity-v1",
  "generated_at": "2026-07-21T12:00:00Z",
  "component": "bibliography",
  "producer": "bib-validate",
  "report_path": "reviews/paper-example/bib-validate/2026-07-21-1200.md",
  "scope": "full-manuscript",
  "artifacts": {
    "manuscript": [{"path": "paper/main.tex", "sha256": "<64 lowercase hex>"}],
    "bibliography": [{"path": "paper/references.bib", "sha256": "<64 lowercase hex>"}]
  },
  "coverage": {
    "population": "cited bibliography entries",
    "total": 20,
    "checked": 20,
    "unverifiable": 0
  },
  "component_verdict": "PASS",
  "composite_status": "INCOMPLETE",
  "missing_components": ["claims"],
  "findings": [
    {"rule_id": "BIB-CITATION-INVENTORY", "status": "PASS", "severity": "info", "message": "All cited keys resolve."},
    {"rule_id": "BIB-IDENTITY", "status": "PASS", "severity": "info", "message": "All in-scope identities resolve."},
    {"rule_id": "BIB-RETRACTION", "status": "PASS", "severity": "info", "message": "No serious update notice found."},
    {"rule_id": "BIB-VERSION", "status": "PASS", "severity": "info", "message": "No stale preprint found."}
  ]
}
```

`component` is exactly `bibliography` or `claims`. Each component always says
`composite_status: INCOMPLETE` and lists the other component as missing: an
individual tool reports its own outcome but cannot claim the combined result.
`producer` is fixed by component (`bib-validate` or `claim-verify`), and
`report_path` identifies the paired project-relative Markdown report.

Each finding requires:

- `rule_id`: one of the owned rule IDs below;
- `status`: `PASS`, `FLAG`, `UNVERIFIABLE`, or `NOT_APPLICABLE`;
- `severity`: `blocker`, `warning`, or `info`;
- `message`: a concise outcome grounded in the producer's report.

Optional fields include `citation_key`, `source_id`, `claim_id`,
`manuscript_location`, `load_bearing` (boolean), `evidence` (object), and
`required_action`. Emit at least one finding for every owned rule ID, including
explicit PASS/NOT_APPLICABLE outcomes; never encode an omitted check as PASS.
For claim findings, `evidence` should retain the source locator/version, access
status, page/section, and exact passage, plus a SHA-256 digest for a local PDF.

## Stable rule IDs

| Component | Rule ID | Meaning |
|---|---|---|
| bibliography | `BIB-CITATION-INVENTORY` | Every in-scope citation key maps to a bibliography record |
| bibliography | `BIB-IDENTITY` | Record identity and DOI/metadata are verified |
| bibliography | `BIB-RETRACTION` | Retraction, withdrawal, concern, and correction status is checked |
| bibliography | `BIB-VERSION` | Preprint/publication version status is checked |
| claims | `CLAIM-ATTACHMENT` | The cited source actually supports the attributed proposition |
| claims | `CLAIM-STRENGTH` | Direction, magnitude, population, conditions, and caveats are preserved |
| claims | `CLAIM-ACCESS` | The evidence needed for verification was available |
| claims | `QUOTE-INTEGRITY` | Direct quotations are exact and context-faithful |

## Deterministic verdicts

The assembler recomputes every component verdict:

- `FAIL`: any `FLAG` or `UNVERIFIABLE` finding with `severity: blocker`, or
  any `UNVERIFIABLE` finding marked `load_bearing: true`;
- `WARN`: no blocker, but at least one `FLAG` or `UNVERIFIABLE` finding;
- `PASS`: all findings are `PASS` or `NOT_APPLICABLE`.

A one-component assembly always yields overall `INCOMPLETE`. With both exact-
matching components, the overall result is `FAIL` if either fails, otherwise
`WARN` if either warns, otherwise `PASS`. Artifact, scope, schema, or ruleset
mismatches are input errors, not review verdicts.

## Required commands

Resolve `<skills-root>` as the directory containing this installed `shared/`
folder. In a source checkout, use the repository-local `skills/` directory.
This keeps the commands independent of any client or machine-specific home
path:

```bash
uv run python "<skills-root>/shared/scripts/assemble_integrity_receipt.py" manifest \
  --root "$PROJECT_ROOT" --scope full-manuscript \
  --manuscript paper/main.tex --bibliography paper/references.bib \
  --output /tmp/citation-integrity-manifest.json

uv run python "<skills-root>/shared/scripts/assemble_integrity_receipt.py" validate \
  reviews/<scope>/<producer>/<timestamp>.citation-integrity.json

uv run python "<skills-root>/shared/scripts/assemble_integrity_receipt.py" assemble \
  --bib-fragment reviews/<scope>/bib-validate/<timestamp>.citation-integrity.json \
  --claim-fragment reviews/<scope>/claim-verify/<timestamp>.citation-integrity.json \
  --output-json reviews/<scope>/pre-submission-report/<timestamp>.citation-integrity.json \
  --output-md /tmp/<timestamp>-citation-integrity.md
```

Choose fresh output paths. The utility refuses to overwrite any existing
manifest, receipt, or Markdown rendering.
