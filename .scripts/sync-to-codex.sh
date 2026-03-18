#!/bin/bash
# Sync Claude Code infrastructure to Codex CLI
# Usage: bash .scripts/sync-to-codex.sh [--dry-run]
#
# Phases:
#   1. Backup existing ~/.codex/ state
#   2. Symlink skills from ~/.claude/skills/ → ~/.codex/skills/
#   3. Generate ~/.codex/AGENTS.md from agents + rules
#   4. Update ~/.codex/config.toml (model, sandbox, MCP servers)
#   5. Validate

set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

CLAUDE_HOME="$HOME/.claude"
CODEX_HOME="$HOME/.codex"
SKILLS_SRC="$CLAUDE_HOME/skills"
SKILLS_DST="$CODEX_HOME/skills"
AGENTS_SRC="$CLAUDE_HOME/agents"
RULES_SRC="$CLAUDE_HOME/rules"

# Resolve Task Management root
_CONFIG="$HOME/.config/task-mgmt/path"
if [[ ! -f "$_CONFIG" ]]; then echo "Missing $_CONFIG" >&2; exit 1; fi
TM="$(head -1 "$_CONFIG" | tr -d '\n')"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
error() { echo -e "${RED}✗${NC} $*" >&2; }

# ── Phase 0: Pre-flight checks ──────────────────────────────────────────

if [[ ! -d "$CODEX_HOME" ]]; then
    error "Codex home directory not found at $CODEX_HOME"
    exit 1
fi

if ! command -v codex &>/dev/null; then
    error "Codex CLI not found in PATH"
    exit 1
fi

if [[ ! -d "$SKILLS_SRC" ]]; then
    error "Claude skills directory not found at $SKILLS_SRC"
    exit 1
fi

echo "Syncing Claude Code → Codex CLI"
echo "  Claude home: $CLAUDE_HOME"
echo "  Codex home:  $CODEX_HOME"
echo "  Dry run:     $DRY_RUN"
echo ""

# ── Phase 1: Backup ─────────────────────────────────────────────────────

BACKUP_DIR="$CODEX_HOME/backups/$(date +%Y%m%d-%H%M%S)"
if [[ "$DRY_RUN" == "false" ]]; then
    mkdir -p "$BACKUP_DIR"
    # Back up AGENTS.md and config.toml if they exist
    [[ -f "$CODEX_HOME/AGENTS.md" ]] && cp "$CODEX_HOME/AGENTS.md" "$BACKUP_DIR/"
    [[ -f "$CODEX_HOME/config.toml" ]] && cp "$CODEX_HOME/config.toml" "$BACKUP_DIR/"
    info "Backup saved to $BACKUP_DIR"
else
    info "[dry-run] Would backup AGENTS.md and config.toml to $BACKUP_DIR"
fi

# ── Phase 2: Symlink skills ─────────────────────────────────────────────

echo ""
echo "Phase 2: Skills"

mkdir -p "$SKILLS_DST"

# Track counts
LINKED=0
SKIPPED=0
REMOVED=0

# Remove stale symlinks (point to skills that no longer exist in Claude)
for link in "$SKILLS_DST"/*/; do
    [[ ! -L "${link%/}" ]] && continue  # skip non-symlinks
    link_name="$(basename "${link%/}")"
    # Skip system skills
    [[ "$link_name" == ".system" ]] && continue
    # Check if symlink target still exists
    if [[ ! -e "${link%/}" ]]; then
        if [[ "$DRY_RUN" == "false" ]]; then
            rm "$SKILLS_DST/$link_name"
            ((REMOVED++))
        else
            warn "[dry-run] Would remove stale symlink: $link_name"
            ((REMOVED++))
        fi
    fi
done

# Create symlinks for each Claude skill
for skill_dir in "$SKILLS_SRC"/*/; do
    [[ ! -d "$skill_dir" ]] && continue
    skill_name="$(basename "$skill_dir")"

    # Skip hidden directories
    [[ "$skill_name" == .* ]] && continue

    # Check for SKILL.md (required)
    if [[ ! -f "$skill_dir/SKILL.md" ]]; then
        warn "Skipping $skill_name (no SKILL.md)"
        ((SKIPPED++))
        continue
    fi

    # Check for collision with system skills
    if [[ -d "$SKILLS_DST/.system/$skill_name" ]]; then
        warn "Skipping $skill_name (conflicts with Codex system skill)"
        ((SKIPPED++))
        continue
    fi

    # Create or update symlink
    if [[ "$DRY_RUN" == "false" ]]; then
        ln -sfn "$skill_dir" "$SKILLS_DST/$skill_name"
        ((LINKED++))
    else
        if [[ -L "$SKILLS_DST/$skill_name" ]]; then
            ((LINKED++))
        else
            info "[dry-run] Would link: $skill_name"
            ((LINKED++))
        fi
    fi
done

info "Skills: $LINKED linked, $SKIPPED skipped, $REMOVED stale removed"

# ── Phase 3: Generate AGENTS.md ─────────────────────────────────────────

echo ""
echo "Phase 3: AGENTS.md"

if [[ "$DRY_RUN" == "false" ]]; then
    uv run python "$TM/.scripts/generate-codex-agents-md.py" \
        --agents-dir "$AGENTS_SRC" \
        --rules-dir "$RULES_SRC" \
        --output "$CODEX_HOME/AGENTS.md"
    info "Generated $CODEX_HOME/AGENTS.md"
else
    info "[dry-run] Would generate AGENTS.md from $AGENTS_SRC + $RULES_SRC"
fi

# ── Phase 4: Update config.toml ─────────────────────────────────────────

echo ""
echo "Phase 4: config.toml"

CONFIG_FILE="$CODEX_HOME/config.toml"

# Read existing config to preserve user settings (model, trust, migrations)
# We only add/update the sections we manage; we don't overwrite the whole file.

# Check if our managed sections already exist
if grep -q "# --- Managed by sync-to-codex ---" "$CONFIG_FILE" 2>/dev/null; then
    # Remove our managed block and re-append
    if [[ "$DRY_RUN" == "false" ]]; then
        sed -i '' '/^# --- Managed by sync-to-codex ---$/,/^# --- End managed ---$/d' "$CONFIG_FILE"
    fi
fi

MANAGED_BLOCK=$(cat <<'TOML'
# --- Managed by sync-to-codex ---
# Do not edit this section manually; it is regenerated by sync-to-codex.sh

[sandbox]
# Default to workspace-write for interactive use
permissions = ["disk-full-read-access"]

[history]
# Persist conversation history
persistence = "save"

# --- End managed ---
TOML
)

if [[ "$DRY_RUN" == "false" ]]; then
    echo "" >> "$CONFIG_FILE"
    echo "$MANAGED_BLOCK" >> "$CONFIG_FILE"
    info "Updated config.toml (managed block appended)"
else
    info "[dry-run] Would append managed block to config.toml"
fi

# ── Phase 5: Validation ─────────────────────────────────────────────────

echo ""
echo "Phase 5: Validation"

ERRORS=0

# Check skills count
SKILL_COUNT=$(find "$SKILLS_DST" -maxdepth 1 -type l | wc -l | tr -d ' ')
if [[ "$SKILL_COUNT" -gt 0 ]]; then
    info "Skills directory: $SKILL_COUNT symlinks"
else
    error "No skill symlinks found"
    ((ERRORS++))
fi

# Check AGENTS.md exists and is non-empty
if [[ -f "$CODEX_HOME/AGENTS.md" && -s "$CODEX_HOME/AGENTS.md" ]]; then
    AGENTS_LINES=$(wc -l < "$CODEX_HOME/AGENTS.md" | tr -d ' ')
    info "AGENTS.md: $AGENTS_LINES lines"
else
    if [[ "$DRY_RUN" == "false" ]]; then
        error "AGENTS.md missing or empty"
        ((ERRORS++))
    fi
fi

# Check config.toml is parseable (basic check)
if [[ -f "$CONFIG_FILE" ]]; then
    if python3 -c "
import tomllib, sys
with open('$CONFIG_FILE', 'rb') as f:
    tomllib.load(f)
" 2>/dev/null; then
        info "config.toml: valid TOML"
    else
        error "config.toml: invalid TOML"
        ((ERRORS++))
    fi
fi

# Check Codex CLI version
CODEX_VERSION=$(codex --version 2>/dev/null || echo "unknown")
info "Codex CLI: $CODEX_VERSION"

# Summary
echo ""
if [[ "$ERRORS" -eq 0 ]]; then
    echo -e "${GREEN}Sync complete — no errors.${NC}"
else
    echo -e "${RED}Sync completed with $ERRORS error(s).${NC}"
    exit 1
fi
