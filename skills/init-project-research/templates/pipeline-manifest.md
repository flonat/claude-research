# Pipeline Manifest

**Project:** <!-- Project title -->
**Last Updated:** <!-- Date -->

---

## Script Status

| Step | Script | Language | Status | Notes |
|------|--------|----------|--------|-------|
<!-- | 01 | code/python/01_import.py | Python | Done | Imports raw data, cleans IDs | -->
<!-- | 05 | code/R/05_merge.R | R | Done | Merges datasets | -->
<!-- | 10 | code/R/10_summary_stats.R | R | Done | Summary statistics table | -->
<!-- | 20 | code/python/20_estimate.py | Python | In progress | Main estimation | -->

**Naming convention:** Step numbers use gaps (01, 05, 10, 20...) to allow insertion. Letter suffixes (10a, 10b) for variants of the same step.

---

## Data Files

| File | Purpose | Created by | Used by |
|------|---------|------------|---------|
<!-- | data/processed/clean_data.csv | Cleaned import | Step 01 | Step 05 | -->
<!-- | data/processed/analysis_file.parquet | Analysis-ready | Step 05 | Steps 10, 20 | -->

**Rule:** `data/raw/` is READ-ONLY. All processed data goes to `data/processed/`.

---

## Manuscript Figure Manifest

This table maps every figure and table in the manuscript back to its source script and input data. Use it to trace any output upstream to its code, or to identify which outputs need regeneration when a script or dataset changes.

| Manuscript ref | Filename | Source script | Step | Input data |
|---------------|----------|---------------|------|------------|
<!-- | Figure 1 | descriptive_plot.pdf | code/R/10_summary_stats.R | 10 | analysis_file.parquet | -->
<!-- | Figure 2 | event_study.pdf | code/python/20_estimate.py | 20 | analysis_file.parquet | -->
<!-- | Table 1 | summary_stats.tex | code/R/10_summary_stats.R | 10 | analysis_file.parquet | -->
<!-- | Table 2 | main_results.tex | code/python/20_estimate.py | 20 | analysis_file.parquet | -->

### Tracing Workflow

**Figure → Source (downstream to upstream):**
1. Find the `\includegraphics{filename}` or `\input{filename}` in your paper
2. Look up the filename in the manifest above to find the source script and step
3. Read the source script to find its input data file
4. Check the Script Status table to find what upstream step creates that data

**Script change → Affected figures (upstream to downstream):**
1. Identify which step's script was changed
2. Look up that step in the manifest to find all figures/tables it produces
3. Rerun the script (via `./run_all.sh "script_name"` if available)
4. Output goes to `output/figures/` or `output/tables/`, which the paper picks up

---

## Notes

- All outputs go to `output/` — figures in `output/figures/`, tables in `output/tables/`
- The Script Status table must stay in sync with actual scripts in `code/`
- Uncomment and fill in rows as you add scripts and outputs to the project
