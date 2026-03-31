# setup.ps1 — Set up Claude Code for Academic Research (Windows)
#
# Creates directory junctions so Claude Code can find skills, agents, hooks,
# and rules from any project directory.
#
# Usage:
#   .\scripts\setup.ps1            # first-time setup
#   .\scripts\setup.ps1 -Update    # re-link without overwriting settings

param(
    [switch]$Update
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"

# Try to read version from package.json
$Version = "unknown"
$PkgJson = Join-Path $RepoDir "package.json"
if (Test-Path $PkgJson) {
    $match = Select-String -Path $PkgJson -Pattern '"version"\s*:\s*"([^"]+)"' | Select-Object -First 1
    if ($match) { $Version = $match.Matches[0].Groups[1].Value }
}

function Write-Info  { param($msg) Write-Host "[setup] $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "[setup] $msg" -ForegroundColor Green }
function Write-Warn  { param($msg) Write-Host "[setup] $msg" -ForegroundColor Yellow }
function Write-Err   { param($msg) Write-Host "[setup] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "========================================="
Write-Host "  Claude Code for Academic Research"
if ($Update) {
    Write-Host "  Update (v$Version)"
} else {
    Write-Host "  Initial Setup (v$Version)"
}
Write-Host "========================================="
Write-Host ""

# ---------- helper: create or verify directory junction ----------
function Link-Component {
    param(
        [string]$Name,
        [string]$Source,
        [string]$Target
    )

    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            # It's a junction/symlink
            $existing = $item.Target
            if ($existing -eq $Source) {
                Write-Ok "$Name link already correct"
            } elseif ($Update) {
                Remove-Item $Target -Force -Recurse
                New-Item -ItemType Junction -Path $Target -Target $Source | Out-Null
                Write-Ok "$Name link updated -> $Source"
            } else {
                Write-Warn "$Name link exists but points to: $existing"
                Write-Warn "Remove it manually if you want to update: Remove-Item $Target"
            }
        } else {
            Write-Warn "$Target is a real directory/file (not a link)"
            Write-Warn "Back it up and remove it if you want to use this repo's $Name"
        }
    } else {
        New-Item -ItemType Junction -Path $Target -Target $Source | Out-Null
        Write-Ok "Linked $Name -> $Source"
    }
}

# ---------- 1. Create ~/.claude if needed ----------
if (-not (Test-Path $ClaudeDir)) {
    Write-Info "Creating $ClaudeDir..."
    New-Item -ItemType Directory -Path $ClaudeDir | Out-Null
    Write-Ok "Created $ClaudeDir"
}

# ---------- 2. Link components ----------
Link-Component "skills" (Join-Path $RepoDir "skills") (Join-Path $ClaudeDir "skills")
Link-Component "agents" (Join-Path $RepoDir ".claude\agents") (Join-Path $ClaudeDir "agents")
Link-Component "rules"  (Join-Path $RepoDir ".claude\rules")  (Join-Path $ClaudeDir "rules")
Link-Component "hooks"  (Join-Path $RepoDir "hooks")  (Join-Path $ClaudeDir "hooks")

# ---------- 3. Copy settings (skip in update mode) ----------
$SettingsSrc = Join-Path $RepoDir ".claude\settings.json"
$SettingsDst = Join-Path $ClaudeDir "settings.json"

if ($Update) {
    Write-Info "Update mode -- skipping settings.json (preserving your config)"
} elseif (Test-Path $SettingsDst) {
    Write-Warn "~/.claude/settings.json already exists -- not overwriting"
    Write-Warn "Compare with $SettingsSrc and merge manually"
} else {
    Copy-Item $SettingsSrc $SettingsDst
    Write-Ok "Copied settings.json -> $SettingsDst"
}

# ---------- 4. Create log directory ----------
$LogDir = Join-Path $RepoDir "log\plans"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
Write-Ok "Ensured log\ and log\plans\ directories exist"

# ---------- 5. Check dependencies ----------
Write-Info "Checking dependencies..."

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pyVer = & python --version 2>&1
    Write-Ok "python found: $pyVer"
} else {
    Write-Warn "python not found -- some hooks require Python 3.11+"
    Write-Warn "Install: winget install Python.Python.3.12"
}

# uv
$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($uv) {
    $uvVer = & uv --version 2>&1
    Write-Ok "uv found: $uvVer"
} else {
    Write-Warn "uv not found -- required for Python hooks and MCP server"
    Write-Warn "Install: winget install astral-sh.uv"
}

# latexmk
$latexmk = Get-Command latexmk -ErrorAction SilentlyContinue
if ($latexmk) {
    Write-Ok "latexmk found (LaTeX compilation available)"
} else {
    Write-Info "latexmk not found -- install a TeX distribution for LaTeX skills"
}

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    Write-Ok "git found: $(& git --version 2>&1)"
} else {
    Write-Warn "git not found -- required for version control"
    Write-Warn "Install: winget install Git.Git"
}

# ---------- 6. Windows-specific notes ----------
Write-Host ""
Write-Info "Windows notes:"
Write-Info "  - Hook scripts (.sh) require Git Bash or WSL to run"
Write-Info "  - If hooks fail, ensure Git Bash is in your PATH"
Write-Info "  - Python hooks (.py) run natively if Python is installed"

# ---------- Done ----------
Write-Host ""
Write-Host "========================================="
Write-Host "  Setup complete! (v$Version)"
Write-Host "========================================="
Write-Host ""

if (-not $Update) {
    Write-Host "Next steps:"
    Write-Host "  1. Edit .context\profile.md with your details"
    Write-Host "  2. Edit .context\current-focus.md with your current work"
    Write-Host "  3. Edit .context\projects\_index.md with your projects"
    Write-Host "  4. Edit CLAUDE.md to customise conventions"
    Write-Host "  5. Review ~\.claude\settings.json for permissions and hooks"
    Write-Host ""
    Write-Host "Then open any project directory and run 'claude' to start!"
} else {
    Write-Host "Links updated. Your settings.json was preserved."
    Write-Host ""
    Write-Host "Check docs\getting-started.md if you need to merge new settings."
}
