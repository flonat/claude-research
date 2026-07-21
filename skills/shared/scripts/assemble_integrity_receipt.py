#!/usr/bin/env -S uv run --quiet python
"""Create, validate, and combine citation-integrity component receipts.

This utility is deliberately mechanical. It hashes declared artifacts,
validates component output from ``bib-validate`` and ``claim-verify``, and
combines compatible components. It never resolves a DOI, reads a cited paper,
judges a claim, or edits manuscript sources.

Usage:
  uv run python skills/shared/scripts/assemble_integrity_receipt.py manifest \
    --root PROJECT --scope full-manuscript --manuscript paper/main.tex \
    --bibliography paper/references.bib --output /tmp/citation-manifest.json
  uv run python skills/shared/scripts/assemble_integrity_receipt.py validate COMPONENT.json
  uv run python skills/shared/scripts/assemble_integrity_receipt.py assemble \
    --bib-fragment BIB.json --claim-fragment CLAIM.json \
    --output-json RECEIPT.json --output-md /tmp/receipt.md

Exit codes:
  0  requested operation completed
  2  invalid input, incompatible fragments, or an existing output target
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1
RULESET_VERSION = "citation-integrity-v1"
COMPONENTS = {"bibliography", "claims"}
PRODUCERS = {"bibliography": "bib-validate", "claims": "claim-verify"}
RULE_IDS = {
    "bibliography": {
        "BIB-CITATION-INVENTORY",
        "BIB-IDENTITY",
        "BIB-RETRACTION",
        "BIB-VERSION",
    },
    "claims": {
        "CLAIM-ATTACHMENT",
        "CLAIM-STRENGTH",
        "CLAIM-ACCESS",
        "QUOTE-INTEGRITY",
    },
}
FINDING_STATUSES = {"PASS", "FLAG", "UNVERIFIABLE", "NOT_APPLICABLE"}
SEVERITIES = {"blocker", "warning", "info"}
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class ReceiptError(ValueError):
    """Raised when a component or receipt violates the shared contract."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise ReceiptError(message)


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReceiptError(f"cannot read JSON object {path}: {error}") from error
    _expect(isinstance(value, dict), f"{path}: top-level JSON value must be an object")
    return value


def _portable_path(value: Any, label: str) -> str:
    _expect(isinstance(value, str) and value.strip(), f"{label} must be a non-empty path")
    path = PurePosixPath(value)
    _expect(not path.is_absolute(), f"{label} must be project-relative: {value}")
    _expect(".." not in path.parts, f"{label} cannot traverse outside the project: {value}")
    return path.as_posix()


def _validate_artifact_list(value: Any, label: str, *, allow_empty: bool) -> list[dict[str, str]]:
    _expect(isinstance(value, list), f"artifacts.{label} must be a list")
    _expect(allow_empty or bool(value), f"artifacts.{label} cannot be empty")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        _expect(isinstance(item, dict), f"artifacts.{label}[{index}] must be an object")
        path = _portable_path(item.get("path"), f"artifacts.{label}[{index}].path")
        digest = item.get("sha256")
        _expect(
            isinstance(digest, str) and HASH_RE.fullmatch(digest) is not None,
            f"artifacts.{label}[{index}].sha256 must be a lowercase SHA-256 digest",
        )
        _expect(path not in seen, f"artifacts.{label} contains duplicate path: {path}")
        seen.add(path)
        normalized.append({"path": path, "sha256": digest})
    return sorted(normalized, key=lambda row: row["path"])


def validate_manifest(value: Any) -> dict[str, Any]:
    _expect(isinstance(value, dict), "artifact_manifest must be an object")
    scope = value.get("scope")
    _expect(isinstance(scope, str) and scope.strip(), "artifact_manifest.scope must be non-empty")
    artifacts = value.get("artifacts")
    _expect(isinstance(artifacts, dict), "artifact_manifest.artifacts must be an object")
    return {
        "scope": scope,
        "artifacts": {
            "manuscript": _validate_artifact_list(
                artifacts.get("manuscript"), "manuscript", allow_empty=False
            ),
            "bibliography": _validate_artifact_list(
                artifacts.get("bibliography"), "bibliography", allow_empty=True
            ),
        },
    }


def finding_blocks(finding: dict[str, Any]) -> bool:
    status = finding["status"]
    return status in {"FLAG", "UNVERIFIABLE"} and (
        finding["severity"] == "blocker"
        or (status == "UNVERIFIABLE" and finding.get("load_bearing") is True)
    )


def component_verdict(findings: list[dict[str, Any]]) -> str:
    if any(finding_blocks(finding) for finding in findings):
        return "FAIL"
    if any(finding["status"] in {"FLAG", "UNVERIFIABLE"} for finding in findings):
        return "WARN"
    return "PASS"


def _validate_finding(value: Any, component: str, index: int) -> dict[str, Any]:
    label = f"findings[{index}]"
    _expect(isinstance(value, dict), f"{label} must be an object")
    rule_id = value.get("rule_id")
    _expect(rule_id in RULE_IDS[component], f"{label}.rule_id is not owned by {component}: {rule_id}")
    status = value.get("status")
    _expect(status in FINDING_STATUSES, f"{label}.status must be one of {sorted(FINDING_STATUSES)}")
    severity = value.get("severity")
    _expect(severity in SEVERITIES, f"{label}.severity must be one of {sorted(SEVERITIES)}")
    message = value.get("message")
    _expect(isinstance(message, str) and message.strip(), f"{label}.message must be non-empty")
    if "load_bearing" in value:
        _expect(isinstance(value["load_bearing"], bool), f"{label}.load_bearing must be boolean")
    if "evidence" in value:
        _expect(isinstance(value["evidence"], dict), f"{label}.evidence must be an object")
    return value


def validate_fragment(value: Any) -> dict[str, Any]:
    _expect(isinstance(value, dict), "fragment must be an object")
    _expect(value.get("kind") == "citation-integrity-component", "kind must be citation-integrity-component")
    _expect(value.get("schema_version") == SCHEMA_VERSION, f"schema_version must be {SCHEMA_VERSION}")
    _expect(value.get("ruleset_version") == RULESET_VERSION, f"ruleset_version must be {RULESET_VERSION}")
    component = value.get("component")
    _expect(component in COMPONENTS, f"component must be one of {sorted(COMPONENTS)}")
    producer = value.get("producer")
    _expect(producer == PRODUCERS[component], f"producer for {component} must be {PRODUCERS[component]}")
    report_path = _portable_path(value.get("report_path"), "report_path")
    _expect(report_path.endswith(".md"), "report_path must identify the paired Markdown report")
    generated_at = value.get("generated_at")
    _expect(isinstance(generated_at, str) and generated_at.strip(), "generated_at must be non-empty")
    try:
        datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ReceiptError("generated_at must be an ISO-8601 timestamp") from error
    manifest = validate_manifest(
        {"scope": value.get("scope"), "artifacts": value.get("artifacts")}
    )

    coverage = value.get("coverage")
    _expect(isinstance(coverage, dict), "coverage must be an object")
    population = coverage.get("population")
    _expect(isinstance(population, str) and population.strip(), "coverage.population must be non-empty")
    for field in ("total", "checked", "unverifiable"):
        number = coverage.get(field)
        _expect(isinstance(number, int) and not isinstance(number, bool) and number >= 0, f"coverage.{field} must be a non-negative integer")
    _expect(coverage["checked"] <= coverage["total"], "coverage.checked cannot exceed coverage.total")
    _expect(coverage["unverifiable"] <= coverage["total"], "coverage.unverifiable cannot exceed coverage.total")

    raw_findings = value.get("findings")
    _expect(isinstance(raw_findings, list), "findings must be a list")
    findings = [_validate_finding(item, component, index) for index, item in enumerate(raw_findings)]
    observed_rules = {item["rule_id"] for item in findings}
    missing_rules = RULE_IDS[component] - observed_rules
    _expect(not missing_rules, f"fragment omits required rule outcomes: {', '.join(sorted(missing_rules))}")

    derived = component_verdict(findings)
    _expect(value.get("component_verdict") == derived, f"component_verdict must be {derived}")
    other = sorted(COMPONENTS - {component})
    _expect(value.get("composite_status") == "INCOMPLETE", "component composite_status must be INCOMPLETE")
    _expect(value.get("missing_components") == other, f"missing_components must be {other}")

    normalized = dict(value)
    normalized["report_path"] = report_path
    normalized["scope"] = manifest["scope"]
    normalized["artifacts"] = manifest["artifacts"]
    normalized["findings"] = findings
    return normalized


def _artifact_identity(fragment: dict[str, Any]) -> str:
    return json.dumps(
        {"scope": fragment["scope"], "artifacts": fragment["artifacts"]},
        sort_keys=True,
        separators=(",", ":"),
    )


def assemble_fragments(fragments: list[dict[str, Any]]) -> dict[str, Any]:
    _expect(bool(fragments), "at least one component fragment is required")
    validated = [validate_fragment(fragment) for fragment in fragments]
    names = [fragment["component"] for fragment in validated]
    _expect(len(names) == len(set(names)), "each component may appear at most once")
    identity = _artifact_identity(validated[0])
    for fragment in validated[1:]:
        _expect(
            _artifact_identity(fragment) == identity,
            "component artifact hashes or scope do not match; rerun both components on one frozen artifact manifest",
        )

    by_component = {fragment["component"]: fragment for fragment in validated}
    missing = sorted(COMPONENTS - set(by_component))
    if missing:
        overall = "INCOMPLETE"
    elif any(fragment["component_verdict"] == "FAIL" for fragment in validated):
        overall = "FAIL"
    elif any(fragment["component_verdict"] == "WARN" for fragment in validated):
        overall = "WARN"
    else:
        overall = "PASS"

    findings = [
        {"component": fragment["component"], **finding}
        for fragment in sorted(validated, key=lambda item: item["component"])
        for finding in fragment["findings"]
    ]
    counts = Counter(finding["status"] for finding in findings)
    return {
        "kind": "citation-integrity-receipt",
        "schema_version": SCHEMA_VERSION,
        "ruleset_version": RULESET_VERSION,
        "generated_at": utc_now(),
        "scope": validated[0]["scope"],
        "artifacts": validated[0]["artifacts"],
        "overall_status": overall,
        "missing_components": missing,
        "components": {
            name: {
                "producer": fragment["producer"],
                "report_path": fragment["report_path"],
                "verdict": fragment["component_verdict"],
                "coverage": fragment["coverage"],
                "generated_at": fragment["generated_at"],
            }
            for name, fragment in sorted(by_component.items())
        },
        "summary": {status.lower(): counts.get(status, 0) for status in sorted(FINDING_STATUSES)},
        "findings": findings,
    }


def render_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# Citation Integrity Receipt",
        "",
        f"**Overall status:** {receipt['overall_status']}",
        f"**Ruleset:** {receipt['ruleset_version']}",
        f"**Scope:** {receipt['scope']}",
        "",
        "## Components",
        "",
        "| Component | Verdict | Checked | Total | Unverifiable | Report |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for component in sorted(COMPONENTS):
        row = receipt["components"].get(component)
        if row is None:
            lines.append(f"| {component} | NOT RUN | — | — | — | — |")
            continue
        coverage = row["coverage"]
        lines.append(
            f"| {component} | {row['verdict']} | {coverage['checked']} | "
            f"{coverage['total']} | {coverage['unverifiable']} | `{row['report_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Component | Rule | Status | Severity | Message |",
            "|---|---|---|---|---|",
        ]
    )
    for finding in receipt["findings"]:
        message = str(finding["message"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {finding['component']} | {finding['rule_id']} | {finding['status']} | "
            f"{finding['severity']} | {message} |"
        )
    if receipt["missing_components"]:
        lines.extend(
            [
                "",
                "## Incomplete receipt",
                "",
                "Missing component(s): " + ", ".join(receipt["missing_components"]) + ".",
                "This is a component outcome, not a full citation-integrity verdict.",
            ]
        )
    return "\n".join(lines) + "\n"


def _write_new(path: Path, content: str) -> None:
    _expect(not path.exists(), f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    root: Path,
    scope: str,
    manuscript: list[str],
    bibliography: list[str],
) -> dict[str, Any]:
    root = root.absolute()

    def artifact(raw: str, label: str) -> dict[str, str]:
        supplied = Path(raw)
        candidate = supplied if supplied.is_absolute() else root / supplied
        absolute = candidate.absolute()
        try:
            relative = absolute.relative_to(root)
        except ValueError as error:
            raise ReceiptError(f"{label} is outside project root: {raw}") from error
        _expect(absolute.is_file(), f"{label} is not a file: {raw}")
        return {"path": relative.as_posix(), "sha256": sha256(absolute)}

    value = {
        "scope": scope,
        "artifacts": {
            "manuscript": [artifact(path, "manuscript") for path in manuscript],
            "bibliography": [artifact(path, "bibliography") for path in bibliography],
        },
    }
    return validate_manifest(value)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    manifest = subparsers.add_parser("manifest", help="hash a frozen manuscript/bibliography scope")
    manifest.add_argument("--root", type=Path, required=True, help="project root used for portable paths")
    manifest.add_argument("--scope", required=True, help="stable scope identifier shared by both components")
    manifest.add_argument("--manuscript", action="append", required=True, help="manuscript file; repeat as needed")
    manifest.add_argument("--bibliography", action="append", default=[], help="bibliography file; repeat as needed")
    manifest.add_argument("--output", type=Path, help="new JSON path; stdout when omitted")

    validate = subparsers.add_parser("validate", help="validate one component fragment")
    validate.add_argument("fragment", type=Path)

    assemble = subparsers.add_parser("assemble", help="combine one or two compatible component fragments")
    assemble.add_argument("--bib-fragment", type=Path)
    assemble.add_argument("--claim-fragment", type=Path)
    assemble.add_argument("--output-json", type=Path, help="new receipt JSON path; stdout when omitted")
    assemble.add_argument("--output-md", type=Path, help="optional new Markdown rendering path")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "manifest":
            value = build_manifest(args.root, args.scope, args.manuscript, args.bibliography)
            rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
            if args.output:
                _write_new(args.output, rendered)
            else:
                sys.stdout.write(rendered)
            return 0

        if args.command == "validate":
            fragment = validate_fragment(_load_object(args.fragment))
            result = {
                "component": fragment["component"],
                "component_verdict": fragment["component_verdict"],
                "composite_status": "INCOMPLETE",
                "missing_components": fragment["missing_components"],
            }
            sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
            return 0

        paths = [path for path in (args.bib_fragment, args.claim_fragment) if path]
        _expect(bool(paths), "assemble requires --bib-fragment and/or --claim-fragment")
        fragments = [_load_object(path) for path in paths]
        for expected, fragment in zip(
            [name for name, path in (("bibliography", args.bib_fragment), ("claims", args.claim_fragment)) if path],
            fragments,
            strict=True,
        ):
            _expect(fragment.get("component") == expected, f"{expected} option received {fragment.get('component')} fragment")
        receipt = assemble_fragments(fragments)
        rendered_json = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if args.output_json:
            _expect(not args.output_json.exists(), f"refusing to overwrite existing output: {args.output_json}")
        if args.output_md:
            _expect(not args.output_md.exists(), f"refusing to overwrite existing output: {args.output_md}")
        if args.output_json:
            _write_new(args.output_json, rendered_json)
        else:
            sys.stdout.write(rendered_json)
        if args.output_md:
            _write_new(args.output_md, render_markdown(receipt))
        return 0
    except ReceiptError as error:
        print(f"citation-integrity: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
