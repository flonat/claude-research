---
name: voice-analyzer
version: 1.0.0
description: "Use when you need to analyze writing samples to create a portable voice profile."
  Analyze writing samples to create a portable voice profile and style guide.
  Use when setting up voice-matched AI writing, onboarding to a new project,
  or refreshing an outdated style guide.
user-invocable: true
allowed-tools: 
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# Voice Analyzer: Create a Voice Profile from Writing Samples

Extract voice patterns from writing samples and generate a comprehensive, portable style guide (VOICE.md). The output becomes infrastructure — a reference document used every time you work with AI to maintain your authentic voice instead of producing generic content.

## Quick Start

Provide 3-5 writing samples where your voice feels strongest (500-2000 words each). The skill will:

1. Analyze patterns across all samples
2. Identify your distinctive voice markers
3. Generate a VOICE.md style guide
4. Create a forbidden phrases list specific to your anti-patterns
5. Provide testing prompts to validate the guide

**Ideal samples:** Published papers, proposals, emails you're proud of, blog posts, referee responses, teaching materials

**Avoid:** Heavily edited collaborative pieces, boilerplate text, anything that felt forced

---

## Sample Gathering Guidance

### What Makes Good Samples

**Include samples that:**
- You wrote when feeling confident and natural
- Received feedback like "this sounds just like you"
- You'd be happy to write again
- Show your voice across different contexts (casual, professional, explanatory)
- Are at least 500 words (longer is better for pattern detection)

**Avoid samples that:**
- Were heavily edited by others
- Feel generic or corporate even to you
- Were written under heavy constraints
- Don't represent how you want to sound going forward

### Minimum Requirements

- **Minimum:** 3 samples, 500+ words each
- **Ideal:** 5-7 samples, 1000+ words each
- **Advanced:** 10+ samples including different formats (email, long-form, paper sections)

More samples = more accurate pattern detection, but diminishing returns after 10.

### Academic Sample Sources

If you're building an academic voice profile:

- **Paper drafts** — introduction and discussion sections show the most voice
- **Referee responses** — often reveal how you argue and handle criticism
- **Proposals and abstracts** — show how you frame contributions
- **Teaching materials** — lecture notes, assignment descriptions
- **Emails to collaborators** — longer substantive emails, not one-liners
- **Blog posts or public writing** — if you have any

**Avoid for academic profiles:**
- Methods sections (too formulaic to show voice)
- Literature review sections (mostly paraphrasing others)
- Co-authored sections where your voice was diluted

---

## Analysis Framework

When analyzing samples, examine these six dimensions:

### 1. Sentence Patterns

- Average sentence length (short/punchy vs. long/flowing)
- Length variation (uniform vs. high variance)
- Sentence starters (do you vary, or repeat patterns?)
- Use of fragments for emphasis
- Complex vs. simple sentence construction

### 2. Vocabulary Fingerprint

- Formality level (casual/conversational vs. professional/technical)
- Jargon usage (field-specific terms, insider language)
- Characteristic phrases you repeat
- Filler words ("actually", "basically", "honestly")
- Intensifiers you favor ("really", "quite", "particularly")
- Academic-specific: hedging vocabulary, contribution framing

### 3. Rhythm and Flow

- Typical paragraph length
- How you transition between ideas
- Use of one-sentence paragraphs for emphasis
- Section structure and pacing
- How you open and close pieces

### 4. Tone Markers

- Humor style (dry, self-deprecating, none)
- Level of directness
- How you handle uncertainty (hedge vs. commit)
- Personal disclosure level
- Relationship with reader (peer, teacher, mentor, collaborator)

### 5. Structural Habits

- How you use lists vs. prose
- Header/subheader patterns
- Use of examples and analogies
- How you introduce and conclude topics
- Formatting preferences (bold, italics, em-dashes, parentheticals)

### 6. Opinion Expression

- How strongly you state opinions
- How you qualify claims
- Use of "I" vs. "we" vs. "you" vs. passive
- How you handle disagreement or controversy
- Confidence level in assertions

---

## Output Format

Generate a VOICE.md file with this structure:

```markdown
# Voice Profile: [Name]
Generated: [Date]
Based on: [X] writing samples ([total word count] words)

## Voice Summary
[2-3 sentence description of overall voice character]

## Core Voice Characteristics

### Sentence Patterns
- Average length: [X] words
- Variation: [Low/Medium/High]
- Notable patterns: [specific observations]

### Vocabulary Fingerprint
- Formality: [Casual/Conversational/Professional/Formal]
- Characteristic phrases: [list]
- Words to use freely: [list]

### Rhythm and Flow
- Paragraph style: [description]
- Transition patterns: [description]
- Pacing notes: [description]

### Tone Markers
- Primary tone: [description]
- Humor style: [description]
- Reader relationship: [description]

### Structural Habits
- List vs. prose preference: [description]
- Formatting patterns: [description]

### Opinion Expression
- Directness level: [1-10]
- Qualification style: [description]
- Authority stance: [description]

## The Forbidden List

### Never Use (These kill your voice)
- [phrase 1]
- [phrase 2]
- [etc.]

### Use Sparingly (Context-dependent)
- [phrase 1] - only when [context]
- [etc.]

### Watch for Clusters (OK alone, problematic together)
- [pattern description]

## Academic Mode Notes
[If academic samples were analyzed]
- Paper voice vs. email voice differences
- Hedging conventions to preserve
- Contribution framing patterns
- How formality shifts by audience (journal vs. collaborator vs. student)

## Voice Maintenance

### Monthly Check
- Read 3 recent pieces aloud
- Do they still sound like you?
- Update this guide if voice has evolved

### Quarterly Refresh
- Gather new strong samples
- Re-run analysis
- Compare to this guide
- Update patterns that have changed

## Testing Prompts

Use these to validate the guide works:

**Test 1 - Short form:**
"Using my voice profile, write a 3-sentence response to [common scenario in your field]"

**Test 2 - Long form:**
"Using my voice profile, write the opening 2 paragraphs for a piece about [topic you know well]"

**Test 3 - Edge case:**
"Using my voice profile, write about [topic outside your usual content]"

Compare outputs to your natural writing. If they feel off, update the guide.
```

---

## Analysis Process

### Step 1: Initial Read
Read all samples without analyzing. Get a feel for the overall voice impression. Note your gut reaction: what makes this writing distinctive?

### Step 2: Pattern Extraction
Go through each dimension in the analysis framework. Pull specific examples from the samples. Look for patterns that appear across multiple samples (not one-offs).

### Step 3: Contrast Analysis
Compare to generic AI output patterns. What does this writer do that AI typically doesn't? What AI patterns are absent from these samples?

### Step 4: Forbidden List Generation
Based on the contrast analysis, identify phrases and patterns that would destroy this voice. These become the "never use" list.

### Step 5: Guide Assembly
Compile findings into the VOICE.md format. Include specific examples from the samples to illustrate each pattern.

### Step 6: Validation Prompts
Generate 3 test prompts tailored to this person's typical writing contexts. These will be used to verify the guide works.

---

## Where to Save VOICE.md

- **Default:** `.context/voice/florian-voice.md` (follows the `.context/` pattern)
- **Project-specific:** `<project>/.context/voice/voice.md` (for project-specific voice)
- **Multiple profiles:** `.context/voice/[context]-voice.md` (academic, casual, teaching)

Add a pointer in the project's CLAUDE.md so it auto-loads:
```markdown
## Voice Profile
See [`.context/voice/florian-voice.md`](.context/voice/florian-voice.md)
```

---

## Integration

- `/voice-editor` uses VOICE.md to guide rewrites

---

## Success Criteria

The voice analysis is complete when:
- [ ] All provided samples have been analyzed
- [ ] Each dimension in the analysis framework has findings
- [ ] VOICE.md file is generated with all sections
- [ ] Forbidden list contains at least 10 specific items
- [ ] 3 validation prompts are tailored to the user's context
- [ ] User has been shown where to save the file
- [ ] Testing process has been explained

**Quality check:** The generated guide should allow someone unfamiliar with the writer to produce content that readers would recognize as authentic.

---

## Core Principle

You're not trying to achieve perfection on attempt one. You're building infrastructure that improves with use. The first guide will be good but not perfect — that's normal. Each piece written with this guide makes it more precise.

Voice doesn't live in first drafts. It lives in editing choices. The guide gives AI direction; your editing gives the work your actual voice.
