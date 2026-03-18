# Validation Tiers

> Shared reference for research projects. Declare the validation tier before proceeding with analysis. This determines claim strength, required sample sizes, and quality thresholds. Adapted from CommDAAF AgentAcademy protocol (Xu 2026).

## Principle

**Declare the tier before examining results.** This prevents scope creep (exploratory work masquerading as publication-ready) and under-investment (publication claims with pilot-level validation). The tier is locked at project initialisation and can only be upgraded through explicit re-declaration.

---

## The Three Tiers

| Tier | Label | Validation Required | Claim Strength | Time Investment |
|------|-------|-------------------|----------------|-----------------|
| 🟢 | **Exploratory** | Basic checks, robustness to obvious alternatives | Hypothesis-generating, suggestive | Hours to 1 day |
| 🟡 | **Pilot** | Sensitivity analysis, multiple specifications, spot-checks | Tentative conclusions, "warrants further investigation" | 1-3 days |
| 🔴 | **Publication** | Full robustness battery, pre-registration, replication, external validation | "Robust evidence", causal claims (if design supports) | 3+ days |

---

## What Each Tier Requires

### 🟢 Exploratory

**Purpose:** Quick investigation, feasibility check, pattern discovery.

| Requirement | Standard |
|-------------|----------|
| Sample size | No minimum (but state N) |
| Robustness | At least 1 alternative specification |
| Standard errors | Correct level (clustered if panel) |
| Sensitivity | Not required |
| Pre-registration | Not required |
| Replication | Not required |
| Claim language | "suggests", "preliminary evidence", "initial exploration" |

**Escalation trigger:** If the user makes causal claims or says "we find that X causes Y" at exploratory tier → escalate to Level 2.

### 🟡 Pilot

**Purpose:** Serious investigation with enough rigour to guide next steps.

| Requirement | Standard |
|-------------|----------|
| Sample size | Justify based on method (power analysis encouraged) |
| Robustness | 3+ alternative specifications |
| Standard errors | Correct and justified |
| Sensitivity | Key parameter sensitivity (at minimum: functional form, sample restrictions) |
| Pre-registration | Encouraged |
| Replication | Internal (split-sample or bootstrap) |
| Claim language | "evidence consistent with", "findings warrant further investigation" |

**Escalation trigger:** If the user submits pilot-tier work to a top journal without upgrading → escalate to Level 3.

### 🔴 Publication

**Purpose:** Results intended for peer-reviewed publication.

| Requirement | Standard |
|-------------|----------|
| Sample size | Power analysis required (justify effect size assumption) |
| Robustness | Full battery: alternative DVs, specifications, samples, estimators |
| Standard errors | Multiple approaches compared (e.g., robust, clustered, wild bootstrap) |
| Sensitivity | Formal sensitivity analysis (Oster bounds, Rosenbaum bounds, or equivalent) |
| Pre-registration | Required for experiments; strongly encouraged for observational |
| Replication | Cross-language (if code-based) or cross-method |
| External validation | Where possible (out-of-sample, different dataset, different context) |
| Claim language | Must match identification strategy — no "effects" without causal design |

**Escalation trigger:** If any publication requirement is missing → escalate per the full [escalation protocol](escalation-protocol.md).

---

## How to Declare

### At project initialisation (`/init-project-research`)

The tier is recorded in `.planning/state.md`:

```markdown
## Validation Tier
🟡 PILOT — sensitivity analysis + multiple specifications required
Declared: 2026-03-15
Rationale: Conference paper for CORE A venue, not yet targeting journal
```

### Mid-project upgrade

To upgrade tier (e.g., exploratory → publication):

1. State the new tier and why
2. Review existing work against the new tier's requirements
3. List what additional validation is needed
4. Update `.planning/state.md`

Downgrades are also legitimate: "We're cutting scope to exploratory for this conference deadline."

---

## Integration with Existing Systems

| System | How tiers interact |
|--------|-------------------|
| **Severity gradient** (`severity-gradient` rule) | Tier maps to phase: Exploratory ≈ Discovery, Pilot ≈ Drafting, Publication ≈ Pre-submission |
| **Escalation protocol** (`escalation-protocol.md`) | Tiers define what triggers escalation — exploratory has a longer leash |
| **Design-before-results** rule | Applies at all tiers, but strictness scales: exploratory allows iteration, publication requires pre-commitment |
| **Method probing** (`method-probing-questions.md`) | All tiers require answering probing questions; the depth of acceptable answers varies |
| **Review agents** | `referee2-reviewer` calibrates expectations to declared tier |
| **Quality scoring** | Thresholds from severity-gradient: 60 (exploratory), 70 (pilot), 90 (publication) |

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Correct Approach |
|-------------|----------------|------------------|
| No tier declared | Defaults create confusion — exploratory work gets judged as publication | Always declare at start |
| "Exploratory" with causal claims | Claim strength exceeds validation level | Either upgrade tier or soften claims |
| "Publication" with no sensitivity analysis | Missing a core requirement | Add sensitivity before submitting |
| Upgrading tier after seeing results | Post-hoc rationalisation | Tier must be declared before results |
| Same tier for all projects | One size doesn't fit all | Match tier to actual goals |
