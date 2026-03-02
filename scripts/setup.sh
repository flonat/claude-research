#!/usr/bin/env bash
# setup.sh — Set up Claude Code for Academic Research
#
# Creates symlinks so Claude Code can find skills, agents, hooks, and rules
# from any project directory.
#
# Usage:
#   ./scripts/setup.sh            # first-time setup
#   ./scripts/setup.sh --update   # re-link without overwriting settings

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"
VERSION="$(grep '"version"' "$REPO_DIR/package.json" 2>/dev/null | head -1 | sed 's/.*: *"\(.*\)".*/\1/' || echo "unknown")"
UPDATE_MODE=false

[[ "${1:-}" == "--update" ]] && UPDATE_MODE=true

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[setup]${NC} $*"; }
ok()    { echo -e "${GREEN}[setup]${NC} $*"; }
warn()  { echo -e "${YELLOW}[setup]${NC} $*"; }
err()   { echo -e "${RED}[setup]${NC} $*" >&2; }

echo ""
echo "========================================="
echo "  Claude Code for Academic Research"
if $UPDATE_MODE; then
  echo "  Update (v$VERSION)"
else
  echo "  Initial Setup (v$VERSION)"
fi
echo "========================================="
echo ""

# ---------- helper: create or verify symlink ----------
link_component() {
  local name="$1"
  local source="$2"
  local target="$3"

  if [[ -L "$target" ]]; then
    existing="$(readlink "$target")"
    if [[ "$existing" == "$source" ]]; then
      ok "$name symlink already correct"
    else
      if $UPDATE_MODE; then
        rm "$target"
        ln -s "$source" "$target"
        ok "$name symlink updated → $source"
      else
        warn "$name symlink exists but points to: $existing"
        warn "Remove it manually if you want to update: rm $target"
      fi
    fi
  elif [[ -e "$target" ]]; then
    warn "$target is a real directory/file (not a symlink)"
    warn "Back it up and remove it if you want to use this repo's $name"
  else
    ln -s "$source" "$target"
    ok "Linked $name → $source"
  fi
}

# ---------- 1. Create ~/.claude if needed ----------
if [[ ! -d "$CLAUDE_DIR" ]]; then
  info "Creating $CLAUDE_DIR..."
  mkdir -p "$CLAUDE_DIR"
  ok "Created $CLAUDE_DIR"
fi

# ---------- 2. Symlink components ----------
link_component "skills" "$REPO_DIR/skills" "$CLAUDE_DIR/skills"
link_component "agents" "$REPO_DIR/.claude/agents" "$CLAUDE_DIR/agents"
link_component "rules"  "$REPO_DIR/.claude/rules"  "$CLAUDE_DIR/rules"
link_component "hooks"  "$REPO_DIR/hooks"  "$CLAUDE_DIR/hooks"

# ---------- 3. Copy settings (skip in update mode) ----------
if $UPDATE_MODE; then
  info "Update mode — skipping settings.json (preserving your config)"
elif [[ -f "$CLAUDE_DIR/settings.json" ]]; then
  warn "~/.claude/settings.json already exists — not overwriting"
  warn "Compare with $REPO_DIR/.claude/settings.json and merge manually"
else
  cp "$REPO_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"
  ok "Copied settings.json → $CLAUDE_DIR/settings.json"
fi

# ---------- 4. Create log directory ----------
mkdir -p "$REPO_DIR/log/plans"
ok "Ensured log/ and log/plans/ directories exist"

# ---------- 5. Check Python dependencies ----------
info "Checking Python dependencies..."

if command -v uv &>/dev/null; then
  ok "uv found: $(uv --version)"
else
  warn "uv not found — required for Python hooks and MCP server"
  warn "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

if command -v python3 &>/dev/null; then
  ok "python3 found: $(python3 --version 2>&1)"
else
  warn "python3 not found — some hooks require Python 3.11+"
fi

if command -v latexmk &>/dev/null; then
  ok "latexmk found (LaTeX compilation available)"
else
  info "latexmk not found — install a TeX distribution for LaTeX skills"
fi

# ---------- 6. MCP bibliography server ----------
if [[ -d "$REPO_DIR/.mcp-server-biblio" ]]; then
  info "Bibliography MCP server found at .mcp-server-biblio/"
  info "To configure it, see docs/bibliography-setup.md"
else
  info "No .mcp-server-biblio/ directory — bibliography search not available"
fi

# ---------- Done ----------
echo ""
echo "========================================="
echo "  Setup complete! (v$VERSION)"
echo "========================================="
echo ""
if ! $UPDATE_MODE; then
  echo "Next steps:"
  echo "  1. Edit .context/profile.md with your details"
  echo "  2. Edit .context/current-focus.md with your current work"
  echo "  3. Edit .context/projects/_index.md with your projects"
  echo "  4. Edit CLAUDE.md to customise conventions"
  echo "  5. Review ~/.claude/settings.json for permissions and hooks"
  echo ""
  echo "Then open any project directory and run 'claude' to start!"
else
  echo "Symlinks updated. Your settings.json was preserved."
  echo ""
  echo "Check docs/getting-started.md if you need to merge new settings."
fi
