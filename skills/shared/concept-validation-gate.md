# Concept Validation Gate

> Shared reference for writing and literature skills. Validates that a research concept is sufficiently developed before investing time in synthesis, drafting, or review. Adapted from CommScribe (Xu 2026).

## Principle

**A weak concept produces a weak paper.** Validate the concept before proceeding to literature synthesis or drafting. This prevents wasted effort on poorly defined research questions, missing theoretical framing, or generic AI-sounding proposals.

---

## Validation Requirements

| Requirement | Minimum | Why It Matters |
|-------------|---------|----------------|
| **Word count** | 300 words | Demonstrates sufficient engagement with the idea |
| **Citations** | 3 references | Shows grounded knowledge, not speculation |
| **Research question** | Explicit, specific | Defines scope and testable contribution |
| **Theoretical framing** | Named framework or lens | Provides analytical structure |
| **Original voice** | Detected (not generic AI) | Ensures authentic intellectual engagement |

---

## What a Concept Plan Must Address

### 1. Research Question

Specific, answerable, and falsifiable.

| Quality | Example |
|---------|---------|
| ❌ Too vague | "How does AI affect organisations?" |
| ❌ Too broad | "What is the impact of technology on decision-making?" |
| ✅ Specific | "How does the introduction of AI decision support change the weighting behaviour of expert panels in multi-criteria evaluation?" |

### 2. Theoretical Framing

Name the theory, cite the source, explain how it applies.

| Quality | Example |
|---------|---------|
| ❌ Missing | "I'll look at decision-making." |
| ❌ Name-dropped | "This uses prospect theory." |
| ✅ Engaged | "Drawing on Kahneman and Tversky's (1979) prospect theory, I examine whether AI recommendations shift reference points in expert judgement, potentially amplifying loss aversion in high-stakes MCDM contexts." |

### 3. Literature Context

What existing work does this build on or challenge?

| Quality | Example |
|---------|---------|
| ❌ Generic | "Many scholars have studied this." |
| ✅ Specific | "While Bansal et al. (2021) examined AI advice-taking in individual decisions, and Sunstein (2019) analysed group polarisation, neither addresses how AI interacts with structured multi-criteria processes where criteria weights are elicited." |

### 4. Contribution Claim

What is genuinely new?

| Quality | Example |
|---------|---------|
| ❌ Vague | "This fills a gap in the literature." |
| ✅ Specific | "By embedding AI recommendations within a live AHP process, I isolate the mechanism through which AI shifts weight allocations — something prior work has theorised but not tested experimentally." |

### 5. Scope Boundaries

What are you explicitly NOT covering?

**Example:** "Focus: expert panels in public sector procurement. Excluded: consumer-facing AI recommendations, autonomous systems without human oversight, non-MCDM decision frameworks."

---

## Depth Score

Beyond the checklist, assess intellectual depth (0.0–1.0):

### Depth Indicators (presence increases score)

| Category | Markers |
|----------|---------|
| **Nuance** | "however", "although", "yet", "while", "despite", "conversely" |
| **Critical thinking** | "gap", "limitation", "critique", "overlooked", "underexplored", "tension" |
| **Engagement** | "argues", "suggests", "contends", "demonstrates", "challenges", "extends" |
| **Theory** | "framework", "lens", "perspective", "mechanism", "construct", "typology" |
| **Methodology** | "method", "approach", "design", "identification", "estimation", "measure" |

### Scoring

- Count markers per category
- Normalise by word count (per 100 words)
- Weight: Nuance (0.25), Critical thinking (0.25), Engagement (0.20), Theory (0.15), Methodology (0.15)
- **Target:** depth_score ≥ 0.4

### Interpretation

| Score | Assessment |
|-------|-----------|
| < 0.2 | Generic — likely AI-generated or insufficiently developed |
| 0.2–0.4 | Surface-level — needs more critical engagement |
| 0.4–0.6 | Adequate — meets minimum for proceeding |
| 0.6–0.8 | Strong — shows genuine intellectual engagement |
| > 0.8 | Excellent — deep, nuanced, ready for synthesis |

---

## Red Flags

Flag these phrases — they signal generic or AI-generated concepts:

| Red Flag | Problem |
|----------|---------|
| "This paper will explore..." | Generic opener |
| "In recent years..." | Filler, not specific |
| "With the rise of..." | Cliché |
| "The purpose of this research is to..." | Formulaic |
| "fills a gap in the literature" | Overused claim without specificity |
| "This is an important topic because..." | Assertion without evidence |
| "Much has been written about..." | Vague attribution |

**Response when detected:** "Your concept sounds generic. Use specific details from your reading to establish your voice and demonstrate genuine engagement with the literature."

---

## Validation Outcomes

### ✅ PASS

All requirements met, depth_score ≥ 0.4, no red flags (or red flags are minor).

→ Proceed to literature synthesis or drafting.

### ⚠️ REVISE

1-2 requirements unmet or depth_score 0.2–0.4.

→ Provide specific feedback on what to strengthen. Ask for revision before proceeding.

### ❌ FAIL

3+ requirements unmet or depth_score < 0.2.

→ Concept is not ready. Suggest the user read more in the area, narrow the question, or identify a theoretical framework before returning.

---

## How Skills Use This

### In `/literature` (before synthesis)

1. Request concept plan from user
2. Run validation checks
3. If PASS → proceed to search and synthesis
4. If REVISE/FAIL → return feedback, wait for revision


1. Check if a validated concept exists (in project's `.planning/` or `CONCEPT.md`)
2. If not → run validation gate before drafting
3. If yes → use the concept to guide section structure

### In review agents

1. Check whether the paper's introduction meets concept validation standards
2. A paper that would FAIL the concept gate has fundamental framing issues → flag as Critical
