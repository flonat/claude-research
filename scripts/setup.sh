#!/usr/bin/env bash
# setup.sh — Set up Claude Code for Academic Research
#
# Creates symlinks so Claude Code can find skills, agents, hooks, and rules
# from any project directory. Run this once after cloning.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[setup]${NC} $*"; }
ok()    { echo -e "${GREEN}[setup]${NC} $*"; }
warn()  { echo -e "${YELLOW}[setup]${NC} $*"; }
err()   { echo -e "${RED}[setup]${NC} $*" >&2; }

echo ""
echo "========================================="
echo "  Claude Code for Academic Research"
echo "  Initial Setup"
echo "========================================="
echo ""

# ---------- 1. Create ~/.claude if needed ----------
if [[ ! -d "$CLAUDE_DIR" ]]; then
  info "Creating $CLAUDE_DIR..."
  mkdir -p "$CLAUDE_DIR"
  ok "Created $CLAUDE_DIR"
fi

# ---------- 2. Symlink skills ----------
if [[ -L "$CLAUDE_DIR/skills" ]]; then
  existing="$(readlink "$CLAUDE_DIR/skills")"
  if [[ "$existing" == "$REPO_DIR/skills" ]]; then
    ok "Skills symlink already correct"
  else
    warn "Skills symlink exists but points to: $existing"
    warn "Remove it manually if you want to update: rm $CLAUDE_DIR/skills"
  fi
elif [[ -d "$CLAUDE_DIR/skills" ]]; then
  warn "~/.claude/skills/ is a real directory (not a symlink)"
  warn "Back it up and remove it if you want to use this repo's skills"
else
  ln -s "$REPO_DIR/skills" "$CLAUDE_DIR/skills"
  ok "Linked skills → $REPO_DIR/skills"
fi

# ---------- 3. Symlink agents ----------
if [[ -L "$CLAUDE_DIR/agents" ]]; then
  existing="$(readlink "$CLAUDE_DIR/agents")"
  if [[ "$existing" == "$REPO_DIR/.claude/agents" ]]; then
    ok "Agents symlink already correct"
  else
    warn "Agents symlink exists but points to: $existing"
    warn "Remove it manually if you want to update: rm $CLAUDE_DIR/agents"
  fi
elif [[ -d "$CLAUDE_DIR/agents" ]]; then
  warn "~/.claude/agents/ is a real directory (not a symlink)"
  warn "Back it up and remove it if you want to use this repo's agents"
else
  ln -s "$REPO_DIR/.claude/agents" "$CLAUDE_DIR/agents"
  ok "Linked agents → $REPO_DIR/.claude/agents"
fi

# ---------- 4. Symlink rules ----------
if [[ -L "$CLAUDE_DIR/rules" ]]; then
  existing="$(readlink "$CLAUDE_DIR/rules")"
  if [[ "$existing" == "$REPO_DIR/.claude/rules" ]]; then
    ok "Rules symlink already correct"
  else
    warn "Rules symlink exists but points to: $existing"
    warn "Remove it manually if you want to update: rm $CLAUDE_DIR/rules"
  fi
elif [[ -d "$CLAUDE_DIR/rules" ]]; then
  warn "~/.claude/rules/ is a real directory (not a symlink)"
  warn "Back it up and remove it if you want to use this repo's rules"
else
  ln -s "$REPO_DIR/.claude/rules" "$CLAUDE_DIR/rules"
  ok "Linked rules → $REPO_DIR/.claude/rules"
fi

# ---------- 5. Symlink hooks ----------
if [[ -L "$CLAUDE_DIR/hooks" ]]; then
  existing="$(readlink "$CLAUDE_DIR/hooks")"
  if [[ "$existing" == "$REPO_DIR/hooks" ]]; then
    ok "Hooks symlink already correct"
  else
    warn "Hooks symlink exists but points to: $existing"
    warn "Remove it manually if you want to update: rm $CLAUDE_DIR/hooks"
  fi
elif [[ -d "$CLAUDE_DIR/hooks" ]]; then
  warn "~/.claude/hooks/ is a real directory (not a symlink)"
  warn "Back it up and remove it if you want to use this repo's hooks"
else
  ln -s "$REPO_DIR/hooks" "$CLAUDE_DIR/hooks"
  ok "Linked hooks → $REPO_DIR/hooks"
fi

# ---------- 6. Copy settings (if none exist) ----------
if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
  warn "~/.claude/settings.json already exists — not overwriting"
  warn "Compare with $REPO_DIR/.claude/settings.json and merge manually"
else
  cp "$REPO_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json"
  ok "Copied settings.json → $CLAUDE_DIR/settings.json"
fi

# ---------- 7. Create log directory ----------
mkdir -p "$REPO_DIR/log/plans"
ok "Ensured log/ and log/plans/ directories exist"

# ---------- Done ----------
echo ""
echo "========================================="
echo "  Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .context/profile.md with your details"
echo "  2. Edit .context/current-focus.md with your current work"
echo "  3. Edit .context/projects/_index.md with your projects"
echo "  4. Edit CLAUDE.md to customise conventions"
echo "  5. Review ~/.claude/settings.json for permissions and hooks"
echo ""
echo "Then open any project directory and run 'claude' to start!"
