# Per-Script Logging Skeletons + Master-Script Pattern

> When the source project's scripts don't already write per-script logs, offer these skeletons so the
> assembled package has one log file per script + a `session_info.log`. Adapted from Yusaku Horiuchi's
> replication-package-guide (R original); the Python/Julia/Stata forms mirror it. The invariant:
> **every public script logs to `logs/<script>.log`; the master script records session info + elapsed time.**

## The contract
- One log file per public script: `logs/<script-stem>.log` (console output + messages, tee'd to screen).
- Each log records: script name, start/end timestamp, and warnings at end.
- The **master script** runs all scripts in order, then writes `session_info.log` (language version, platform, OS, loaded packages, run start/end/elapsed).
- After a successful run, the master script refreshes the README's "Computing Environment" block.

## R

`functions/logging.R`:
```r
start_script_log <- function(script_name, log_dir = "logs") {
  dir.create(log_dir, recursive = TRUE, showWarnings = FALSE)
  log_file <- file.path(log_dir, paste0(script_name, ".log"))
  sink(log_file, split = TRUE)
  cat("########################################\n")
  cat("Script:", paste0(script_name, ".R"), "\n")
  cat("Started:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"), "\n")
  cat("########################################\n\n")
  invisible(log_file)
}

end_script_log <- function() {
  cat("\n--- warnings() at end of script ---\n")
  w <- warnings(); if (is.null(w) || length(w) == 0) cat("None\n") else print(w)
  cat("Ended:", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"), "\n")
  while (sink.number() > 0) sink()
}
```
Master (`master.R`) essentials: `safe_source()` (stop if file missing, banner per script), run scripts in order, then `sink("session_info.log"); cat(elapsed); print(sessionInfo()); sink()`. Full worked example: `resources/academics/yusaku-horiuchi/replication-package-guide/templates/compact/master.R`.

## Python

`code/logging_util.py`:
```python
import sys, datetime, contextlib
from pathlib import Path

@contextlib.contextmanager
def script_log(script_name, log_dir="logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    f = open(Path(log_dir) / f"{script_name}.log", "w")
    class Tee:
        def write(s, d): f.write(d); sys.__stdout__.write(d)
        def flush(s): f.flush()
    old = sys.stdout; sys.stdout = Tee()
    print("#" * 40); print(f"Script: {script_name}.py")
    print(f"Started: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"); print("#" * 40, "\n")
    try:
        yield
    finally:
        print(f"\nEnded: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
        sys.stdout = old; f.close()
```
Master (`master.py`): run each script via `runpy`/`subprocess` in order; write `session_info.log` from `platform`, `sys.version`, and `pip freeze` (or `uv pip freeze`), plus start/end/elapsed. Use **`uv`** (never bare `pip`) per `python-uv`.

## Julia
`logging.jl`: open `logs/<name>.log`, use a `TeeStream` (or `Logging.SimpleLogger` + `Base.CoreLogging`), banner start/end. Master: run in order, then dump `versioninfo()` + `Pkg.status()` + elapsed to `session_info.log`.

## Stata
Per script: `capture log close _all` then `log using "logs/<name>.log", replace text`; end with `log close`. Master `.do`: `timer on 1`, `do` each script in order, `timer off 1`; write `session_info.log` via `creturn list` (Stata version, OS) + `timer list`.

## Notes
- Adapt the log dir to the package structure (`logs/` for compact; `build/logs/` + `analyze/logs/` for build-analyze — see `figure-table-crosswalk.md` and the AEA template's directory section).
- These are *offered*, not forced — if the source project already logs cleanly, keep its scheme and only ensure `session_info.log` exists.
