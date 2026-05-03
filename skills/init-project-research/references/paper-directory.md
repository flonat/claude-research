# Init Project Research — Paper Directory Convention

> Detailed reference extracted from `SKILL.md` Phase 5.

## Paper Directory Convention (Nested Pattern)

Each paper submission gets its own **real directory** at project root (e.g., `paper/`, `paper-ccs/`, `paper-rg/`). Inside that directory, a `paper/` **symlink** points to the Overleaf folder. This nesting allows venue-specific files (submission checklists, cover letters, response documents, reviewer correspondence) to live alongside the Overleaf content without being synced to Overleaf.

**Structure:**

```
paper-ccs/                    # Real directory (venue wrapper)
├── paper/                    # Symlink → Overleaf directory
├── submission-checklist.md   # Venue-specific (not in Overleaf)
├── cover-letter.tex          # Venue-specific
└── response-to-reviewers.tex # Added after R&R
```

**Single-paper projects** use the same pattern:

```
paper/                        # Real directory (venue wrapper)
└── paper/                    # Symlink → Overleaf directory
```

## Overleaf Folder Naming Convention

**Naming convention:** `Paper {THEME_PREFIX} {Title Cased Slug} ({VENUE})` — venue suffix is **required**, even for single-venue papers. Examples: `Paper ASG Privacy Compliance Gaming (CCS)`, `Paper BDS Identity Belief Alignment (JBDM)`, `Paper MechDes Strategic Compliance (NeurIPS 26)`.

Use the venue's standard abbreviation (CCS, NeurIPS, EAAMO, FAccT, ICSE, JBDM, [Journal], …). Append a 2-digit year if it disambiguates multiple submission cycles for the same venue (`(NeurIPS 26)` vs `(NeurIPS 27)`).

| Theme | Prefix |
|-------|--------|
| Category A | ASG |
| Category B | BDS |
| Category C | EnvEcon |
| Category D | HAI |
| Industrial Organisation | IO |
| Mechanism Design | MechDes |
| NLP & Computational AI | NLP |
| Category E | OR |
| Category F | OrgStrat |
| Category G | PolSci |

For multi-venue submissions, create one Overleaf folder per venue, each with its own venue suffix: `Paper ASG Privacy Compliance Gaming (CCS)`, `Paper ASG Privacy Compliance Gaming (RegGov)`.

## Commands

```bash
# Create the Overleaf project folder if it doesn't exist yet
# (creating a folder in the Overleaf root automatically creates an Overleaf project)
overleaf_root="$(cat ~/.config/task-mgmt/overleaf-root 2>/dev/null || echo ~/Apps/Overleaf)"
mkdir -p "$overleaf_root/Paper ASG Privacy Compliance Gaming (CCS)"

# For each venue:
mkdir -p paper-ccs
ln -s "$overleaf_root/Paper ASG Privacy Compliance Gaming (CCS)" paper-ccs/paper

# Single paper (still uses venue suffix):
mkdir -p paper-jbdm
ln -s "$overleaf_root/Paper BDS Identity Belief Alignment (JBDM)" paper-jbdm/paper
```

**Important:** Never rename or delete Overleaf folders — see `.claude/rules/overleaf-separation.md` (Overleaf Folder Lifecycle).

Ensure `.latexmkrc` exists inside the Overleaf target (the symlink destination), not in the wrapper directory. Drop the canonical config:

```bash
TM=$(cat ~/.config/task-mgmt/path)
cp "$TM/templates/latexmkrc/.latexmkrc" paper-<venue>/paper/
```

The canonical file (`templates/latexmkrc/.latexmkrc`) auto-detects pdflatex/xelatex/lualatex, builds to `out/`, and copies the PDF back to the source dir. It lives inside the Overleaf-synced folder so both local and Overleaf web compiles see it.

## Backup Directory

After creating paper directories, create a `backup/` directory with one subdirectory per paper:

```bash
mkdir -p backup/
for d in paper*/; do
  mkdir -p "backup/$(basename "$d")"
done
```

**Convention:** One `backup/` directory at project root, with subdirectories matching each `paper*` directory name. The daily `backup-overleaf-papers.sh` script copies `.tex`/`.bib`/style files from the Overleaf symlink targets into these subdirectories.

**Examples:**
- Single paper: `backup/paper/`
- Multi-paper: `backup/paper-ccs/`, `backup/paper-rg/`

## Permissions Sync (Phase 4)

After writing `.claude/settings.local.json` (with hook config), merge global permissions into it so the new project starts with full permissions from day one:

1. Read `~/.claude/settings.json` → extract `permissions.allow` array
2. Read the newly created `.claude/settings.local.json`
3. Compute the union: `local_permissions ∪ global_permissions`
4. Write the merged `permissions.allow` back to `.claude/settings.local.json` (preserving the `hooks` key)

```bash
# Merge global permissions into the new project's settings
jq -s '.[0].permissions.allow as $global |
  .[1] | .permissions.allow = ((.permissions.allow // []) + $global | unique | sort)' \
  ~/.claude/settings.json .claude/settings.local.json > .claude/settings.local.json.tmp \
  && mv .claude/settings.local.json.tmp .claude/settings.local.json
```

Also merge the `permissions.deny` array using the same logic.
