# AEA-Style Data and Code Availability README Template

> Template for generating replication READMs in `/replication-package` Phase 4. Follows the American Economic Association's Data and Code Availability Policy structure, widely adopted across social sciences.

---

## Overview

| Field | Value |
|-------|-------|
| **Title** | [Paper title] |
| **Authors** | [Author names] |
| **Date** | [YYYY-MM-DD] |
| **JEL Codes** | [If applicable] |

**Summary:** [1-2 sentence description of what the replication package contains and what it reproduces.]

---

## Data Availability

### Included Data

| File | Source | License | Notes |
|------|--------|---------|-------|
| `data/raw/dataset1.csv` | [Original source with URL] | [CC-BY 4.0 / Public domain / etc.] | [Downloaded YYYY-MM-DD] |
| `data/raw/dataset2.dta` | [Source] | [License] | [Notes] |

### Data Not Included

| Data | Source | Access | Reason |
|------|--------|--------|--------|
| [Dataset name] | [Provider] | [How to obtain: URL, application process, DUA] | [Restricted use / too large / proprietary] |

### Data Citations

> List formal citations for all datasets, following the dataset's preferred citation format.

1. [Author(s)]. [Year]. "[Dataset Title]." [Repository/Publisher]. [DOI/URL].

---

## Computational Requirements

### Software

| Software | Version | Required |
|----------|---------|----------|
| Python | 3.x | Yes |
| R | 4.x | Yes |
| LaTeX (TeX Live / MiKTeX) | [Year] | For paper compilation |

### Packages

#### Python

```
# Install from requirements.txt or pyproject.toml
pip install -r requirements.txt
```

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | x.x.x | [Purpose] |
| pandas | x.x.x | [Purpose] |

#### R

```r
# Install from renv.lock
renv::restore()
```

| Package | Version | Purpose |
|---------|---------|---------|
| tidyverse | x.x.x | [Purpose] |
| fixest | x.x.x | [Purpose] |

### Hardware

- **Approximate runtime:** [e.g., "30 minutes on a standard laptop", "8 hours on a 32-core server"]
- **Memory requirements:** [e.g., "4 GB RAM minimum"]
- **Storage requirements:** [e.g., "2 GB free disk space"]
- **Special hardware:** [e.g., "GPU required for training" or "None"]

---

## Description of Programs

### Directory Structure

```
project/
  code/           # Analysis scripts
  data/raw/       # Source data (read-only)
  data/processed/ # Intermediate data (generated)
  output/         # Results: tables, figures
  paper/          # LaTeX source
```

### Scripts

Scripts should be run in the order listed below. Each script's inputs and outputs are documented.

| # | Script | Description | Inputs | Outputs | Runtime |
|---|--------|-------------|--------|---------|---------|
| 1 | `code/01_clean_data.py` | Clean and merge raw data | `data/raw/*.csv` | `data/processed/clean.csv` | ~2 min |
| 2 | `code/02_analysis.R` | Main regression analysis | `data/processed/clean.csv` | `output/tables/table1.tex` | ~5 min |
| 3 | `code/03_figures.py` | Generate all figures | `data/processed/clean.csv` | `output/figures/*.pdf` | ~3 min |
| 4 | `code/04_robustness.R` | Robustness checks | `data/processed/clean.csv` | `output/tables/table_A*.tex` | ~10 min |

### Master Script

If a master script exists:

```bash
# Run all analyses in sequence
bash run_all.sh
```

Or with Make:

```bash
make all
```

---

## Instructions to Replicators

### Step-by-step

1. **Clone/download** this repository
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt  # Python
   Rscript -e "renv::restore()"     # R
   ```
3. **Obtain restricted data** (if applicable):
   - [Instructions for obtaining data not included in the package]
   - Place files in `data/raw/` matching the filenames listed above
4. **Run scripts in order:**
   ```bash
   python code/01_clean_data.py
   Rscript code/02_analysis.R
   python code/03_figures.py
   Rscript code/04_robustness.R
   ```
   Or use the master script: `bash run_all.sh`
5. **Compile the paper** (optional):
   ```bash
   cd paper && latexmk -pdf main.tex
   ```
6. **Verify outputs** match the tables and figures in the paper.

### Expected Outputs

After successful replication, the following files should be produced:

| Output | Location | Corresponds to |
|--------|----------|---------------|
| `output/tables/table1.tex` | Table 1 in paper | Main results |
| `output/figures/figure1.pdf` | Figure 1 in paper | [Description] |

---

## List of Tables and Figures

> Map every table and figure in the paper to the script and data that produce it.

### Tables

| Table | Script | Data | Notes |
|-------|--------|------|-------|
| Table 1: [Title] | `code/02_analysis.R` | `data/processed/clean.csv` | |
| Table 2: [Title] | `code/02_analysis.R` | `data/processed/clean.csv` | |
| Table A1: [Title] | `code/04_robustness.R` | `data/processed/clean.csv` | Appendix |

### Figures

| Figure | Script | Data | Notes |
|--------|--------|------|-------|
| Figure 1: [Title] | `code/03_figures.py` | `data/processed/clean.csv` | |
| Figure 2: [Title] | `code/03_figures.py` | `data/processed/clean.csv` | |

---

## References

> Cite all data sources, software, and methodological references used in the replication package.

1. [Data citation 1]
2. [Data citation 2]
3. [Software citation, if applicable]

---

## Notes

- [Any additional information replicators should know]
- [Known issues or platform-specific quirks]
- [Contact information for questions — omit if double-blind]
