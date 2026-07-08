# Replication Package — Report Template

> Phase 12 report format for `/replication-package` Blind mode. Copy and fill in after completing anonymization. Also used as the basis for the Assemble mode Phase 7 report (omit the identity sections).

```
Replication Package — Complete (Blind)
========================================
Project:     <project-name>
Output:      <output-path>
Status:      Assembled + Anonymized

AI Traces Removed:
  Directories:  N removed
  Files:        N removed
  Text scrubs:  N lines across M files
  Gitignore:    N lines cleaned

Replication Assets:
  README:       Generated (AEA-style)
  Scripts:      N files, execution order documented
  Data:         N files (XX MB), provenance documented
  Dependencies: <manifest-file> present
  Outputs:      N files (XX MB)

Identity Anonymization:
  LaTeX author blocks:    N replaced
  Acknowledgments:        N redacted
  Self-citations flagged: N (K anonymized, J kept, I removed)
  Code headers:           N cleaned
  Package metadata:       N fields replaced
  Path references:        N cleaned
  Global replacements:    N across M files

Size comparison:
  Original:  XX MB
  Package:   XX MB

Git identity:
  Author:    Anonymous <anonymous@example.com>
  Committer: Anonymous <anonymous@example.com>
  Trailers:  None

Verification — identity leak check:
  "<full-name>":          0 matches
  "<email>":              0 matches
  "<institution-1>":      0 matches
  "<institution-2>":      0 matches
  ...
  "claude" (AI traces):   0 matches
  "anthropic":            0 matches

Manual checks recommended:
  - PDF files: check Document Properties for embedded author metadata
  - Image files: check EXIF data for camera/author info
  - Dataset files: check for identifying columns or headers
  - Supplementary materials: check any compiled outputs
  - Self-citations: verify venue policy on self-citation handling
```

Run the verification grep for **every identity item** plus AI traces. If any matches remain, list them with file and line number, and ask the user whether they are false positives or need manual fixing.
