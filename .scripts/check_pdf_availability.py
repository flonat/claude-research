#!/usr/bin/env python3
"""Pre-flight: check which DOIs from a paper-book bibliography have PDFs.

Runs on Mac Mini, SSHes into the VPS, execs a one-shot Python inside the
deploy-refpile-1 container against citations.db + the storage backend, and
returns a JSON dict {doi: bool}.

Used by paper-book's private build to gate the [PDF↗] link in references.md
so we only render links that will actually deliver a PDF (not 404).

Usage:
    check_pdf_availability.py <doi-list-file>

The input file is one DOI per line. Output is JSON on stdout.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


PROBE_SCRIPT = r"""
import json, os, sys
sys.path.insert(0, '/app')
from refpile.services.citation_enricher import get_db
from refpile.services.pdf_storage import is_stored
from refpile.services.pdf_extract import _find_pdf_attachment

email = os.environ.get('ADMIN_EMAIL', '')
db = get_db()
out = {}
for doi in sys.stdin.read().splitlines():
    doi = doi.strip()
    if not doi:
        continue
    row = db.get_by_doi(doi, user_email=email)
    if not row or not row.get('zotero_key'):
        out[doi] = False
        continue
    key = row['zotero_key']
    if is_stored(key, user_email=email):
        out[doi] = True
        continue
    try:
        out[doi] = bool(_find_pdf_attachment(key))
    except Exception:
        out[doi] = False
print(json.dumps(out))
"""


def check(dois: list[str]) -> dict[str, bool]:
    if not dois:
        return {}
    payload = "\n".join(dois) + "\n"
    cmd = [
        "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "vps",
        "docker", "exec", "-i", "deploy-refpile-1", "python", "-c", shlex.quote(PROBE_SCRIPT),
    ]
    # Replace the quoted token: ssh+docker exec needs the script as a literal arg
    # without shell-quote munging. Use a different invocation that pipes via stdin.
    ssh_cmd = (
        "docker exec -i -e ADMIN_EMAIL deploy-refpile-1 python -c "
        + shlex.quote(PROBE_SCRIPT)
    )
    res = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", "vps", ssh_cmd],
        input=payload, capture_output=True, text=True, timeout=30,
    )
    if res.returncode != 0:
        sys.stderr.write(f"[pdf-check] ssh failed (rc={res.returncode}):\n{res.stderr}\n")
        return {d: False for d in dois}
    try:
        return json.loads(res.stdout.strip())
    except Exception as e:
        sys.stderr.write(f"[pdf-check] non-json output: {e}\n{res.stdout[:500]}\n")
        return {d: False for d in dois}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dois", type=Path, help="path to file with one DOI per line")
    args = ap.parse_args()
    dois = [
        line.strip()
        for line in args.dois.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    result = check(dois)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
