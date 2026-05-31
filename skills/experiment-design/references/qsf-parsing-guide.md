# QSF Parsing Guide

> How to parse Qualtrics `.qsf` files and extract design elements.
> Read during Survey mode (Entry Point A) of `/experiment-design`.

## QSF File Structure

A `.qsf` file is JSON with this top-level structure:

```json
{
  "SurveyEntry": { ... },           // Survey metadata
  "SurveyElements": [               // Array of elements
    { "Element": "BL", ... },       // Block definitions
    { "Element": "FL", ... },       // Flow definitions
    { "Element": "SQ", ... },       // Survey questions
    { "Element": "RS", ... },       // Response sets
    ...
  ]
}
```

## Question Type Mapping

### Standard Types (`SQ` elements)

| Qualtrics `Selector` | Human name | How to parse |
|----------------------|-----------|-------------|
| `Likert` | Likert scale | `Choices` for scale points, `Answers` for items |
| `Matrix` | Matrix table | `Answers` = rows (items), `Choices` = columns (scale) |
| `SAVR` | Single answer | `Choices` = response options |
| `MAVR` | Multiple answer | `Choices` = response options (multi-select) |
| `Slider` | Slider | `Choices` with min/max/step |
| `TE` / `SL` | Text entry (single line) | Free text |
| `TE` / `ML` | Text entry (multi-line) | Free text |
| `TE` / `ESTB` | Text entry (essay) | Free text |
| `CS` | Constant sum | `Choices` = items to allocate across |
| `RO` | Rank order | `Choices` = items to rank |
| `MaxDiff` | Best-worst scaling | `Choices` = items, shown in subsets |
| `NPS` | Net Promoter Score | 0-10 scale |

### Numeric Entry
Look for `Validation.Settings.ForceResponse` and `Validation.Settings.Type = "ValidNumber"`.

### Timing Questions
`QuestionType = "Timing"` — records page submit time, first click, last click, click count.

## Detecting Design Elements

### Factorial Conditions

Look for **Randomizer** elements in the survey flow (`FL` element):

```json
{
  "Type": "Randomizer",
  "FlowID": "FL_2",
  "SubSet": 1,
  "EvenPresentation": true,
  "Flow": [
    { "Type": "Block", "ID": "BL_condition1" },
    { "Type": "Block", "ID": "BL_condition2" },
    { "Type": "Block", "ID": "BL_condition3" }
  ]
}
```

**Parsing rules:**
- Each `Randomizer` = one factor
- Each `Block` inside = one level of that factor
- `SubSet` = how many levels each participant sees (1 = between-subjects)
- `EvenPresentation` = balanced assignment
- Multiple nested Randomizers = factorial design (count them to infer N×M)

### Embedded Data

Look for `EmbeddedData` elements in the flow:

```json
{
  "Type": "EmbeddedData",
  "FlowID": "FL_3",
  "EmbeddedData": [
    { "Description": "condition", "Type": "Recipient", "Field": "condition" }
  ]
}
```

These often encode condition assignments, participant IDs, or Prolific/MTurk metadata.

### Skip/Display Logic

Found in question `DisplayLogic` or `SkipLogic` fields:

```json
{
  "DisplayLogic": {
    "Type": "BooleanExpression",
    "inPage": false,
    "Conditions": [{
      "LeftOperand": "q://QID1/SelectableChoice/1",
      "Operator": "Selected"
    }]
  }
}
```

Parse to reconstruct branching paths. Report as a flow diagram.

### Attention Checks

**Heuristic detection** (not always reliable):
- Questions with `ForceResponse` and exactly one "correct" answer
- Questions containing keywords: "attention", "carefully", "select", "please choose"
- Very short questions embedded in long scale batteries
- Questions with a `Validation` block that checks specific responses

Flag potential attention checks but ask the user to confirm.

## Scale Detection

### Recognizing Known Scales

Match question text and item count against `references/known-scales-registry.md`. Detection signals:

1. **Exact match:** Item text matches a known scale verbatim
2. **Partial match:** 3+ items from a known scale appear in sequence
3. **Structural match:** Same number of items + same scale points as a known scale

### Semantic Type Detection

Classify scales by their anchor text:

| Anchor pattern | Semantic type |
|---------------|---------------|
| Strongly disagree → Strongly agree | Agreement |
| Very dissatisfied → Very satisfied | Satisfaction |
| Not at all → Extremely | Intensity |
| Never → Always | Frequency |
| Very unlikely → Very likely | Likelihood/intention |
| Not at all trustworthy → Very trustworthy | Trust |
| No risk → High risk | Risk perception |

### Reverse-Coded Items

Flag items where the valence is opposite to the scale direction:
- Negative wording in a positive-anchored scale (e.g., "I rarely feel happy" in a well-being scale)
- Keywords: "not", "rarely", "never", "difficult", "unable", "lack"

## Output Format

After parsing, produce a structured summary:

```markdown
## QSF Summary: [Survey Title]

### Design
- **Type:** [between/within/factorial/mixed]
- **Conditions:** [list with N per cell]
- **Randomization:** [balanced/unbalanced, even presentation]

### Questions ([N] total)
| # | Block | Type | Label | Scale | Items | Logic |
|---|-------|------|-------|-------|-------|-------|
| Q1 | Consent | MC-SA | Consent | Binary | 1 | — |
| Q2 | Demographics | MC-SA | Age | Categorical | 1 | — |
| ... | | | | | | |

### Detected Scales
| Scale | Items | Type | Known match |
|-------|-------|------|-------------|
| Trust | 5 | Likert-7 | Mayer & Davis (1999) |
| ... | | | |

### Attention Checks
[List with positions and types]

### Warnings
- [Any issues found: missing attention checks, unbalanced conditions, etc.]
```
