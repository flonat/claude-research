#!/bin/bash
# run_all.sh — Multi-language pipeline executor
# Usage:
#   ./run_all.sh "script_name"    Run a single script (auto-detects language)
#   ./run_all.sh --all            Run all pipeline steps in order
#
# Supported languages: Python (via uv), R, Stata
# Logs saved to: output/logs/<script>_<timestamp>.log

set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_ROOT/output/logs"
mkdir -p "$LOG_DIR"

# --- Language runners ---

run_python() {
    local script="$1"
    local logfile="$2"
    echo "Running Python: $script"
    uv run python "$script" 2>&1 | tee "$logfile"
    return "${PIPESTATUS[0]}"
}

run_r() {
    local script="$1"
    local logfile="$2"
    echo "Running R: $script"
    Rscript "$script" 2>&1 | tee "$logfile"
    return "${PIPESTATUS[0]}"
}

run_stata() {
    local script="$1"
    local logfile="$2"
    echo "Running Stata: $script"
    local script_name
    script_name=$(basename "$script" .do)
    stata-mp -b do "$script" 2>&1 | tee "$logfile"
    # Stata writes its own log; append it
    if [ -f "${script_name}.log" ]; then
        cat "${script_name}.log" >> "$logfile"
        rm "${script_name}.log"
    fi
    return "${PIPESTATUS[0]}"
}

# --- Dispatcher ---

run_script() {
    local script="$1"
    local script_name
    script_name=$(basename "$script")
    local timestamp
    timestamp=$(date +"%Y-%m-%d_%H%M%S")
    local logfile="$LOG_DIR/${script_name}_${timestamp}.log"

    echo "========================================"
    echo "  Script: $script_name"
    echo "  Log:    $logfile"
    echo "  Time:   $(date)"
    echo "========================================"

    local exit_code=0

    case "$script" in
        *.py)   run_python "$script" "$logfile" || exit_code=$? ;;
        *.R)    run_r "$script" "$logfile" || exit_code=$? ;;
        *.do)   run_stata "$script" "$logfile" || exit_code=$? ;;
        *)
            echo "ERROR: Unknown file type: $script"
            echo "Supported: .py, .R, .do"
            return 1
            ;;
    esac

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo "SUCCESS: $script_name completed (exit code 0)"
    else
        echo "FAILED: $script_name (exit code $exit_code)"
    fi
    echo "Log saved: $logfile"

    # Open log on macOS
    if command -v open &> /dev/null; then
        open "$logfile"
    fi

    return $exit_code
}

# --- Main ---

if [ $# -eq 0 ]; then
    echo "Usage:"
    echo "  ./run_all.sh \"script_name\"    Run a single script"
    echo "  ./run_all.sh --all            Run all pipeline steps"
    exit 1
fi

if [ "$1" = "--all" ]; then
    echo "Running full pipeline..."
    echo ""
    # Add pipeline steps here in order, e.g.:
    # run_script "code/python/01_import.py"
    # run_script "code/R/05_merge.R"
    # run_script "code/R/10_summary_stats.R"
    # run_script "code/python/20_estimate.py"
    echo "No pipeline steps configured yet. Add them to run_all.sh."
    exit 0
else
    run_script "$1"
fi
