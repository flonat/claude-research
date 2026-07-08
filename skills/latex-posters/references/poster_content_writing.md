# Research Poster Content: Writing Style & Quality

> Writing style, visual-text integration, content adaptation, and quality checklists.
> See also: [poster_content_sections.md](poster_content_sections.md) for principles & sections.

## Writing Style for Posters

### Active vs. Passive Voice

**Prefer Active Voice** (more engaging, clearer):
- ✅ "We developed a model..."
- ✅ "The treatment reduced symptoms..."

**Passive Voice** (when appropriate):
- ✅ "Samples were collected from..."
- ✅ "Data were analyzed using..."

### Sentence Length

**Keep Sentences Short**:
- **Ideal**: 10-15 words per sentence
- **Maximum**: 20-25 words
- **Avoid**: >30 words (hard to follow)

**Example Revision**:
- ❌ Long: "We performed a comprehensive analysis of gene expression data from 500 patients with colorectal cancer using RNA sequencing and identified 47 differentially expressed genes associated with treatment response." (31 words)
- ✅ Short: "We analyzed RNA sequencing data from 500 colorectal cancer patients. We identified 47 genes associated with treatment response." (19 words total, two sentences)

### Bullet Points vs. Paragraphs

**Use Bullet Points For**:
- ✅ Lists of items or findings
- ✅ Key conclusions
- ✅ Methods steps
- ✅ Study characteristics

**Use Short Paragraphs For**:
- ✅ Narrative flow (Introduction)
- ✅ Complex explanations
- ✅ Connected ideas

**Bullet Point Best Practices**:
- Start with action verbs or nouns
- Parallel structure throughout list
- 3-7 bullets per list (not too many)
- Brief (1-2 lines each)

**Example**:
```
Methods
• Participants: 200 adults (18-65 years)
• Design: Double-blind RCT (12 weeks)
• Intervention: Daily 30-min exercise
• Control: Standard care
• Analysis: Mixed models (SPSS v.28)
```

### Acronyms and Jargon

**First Use Rule**: Define at first appearance
```
We used machine learning (ML) to analyze... Later, ML predicted...
```

**Common Acronyms**: May not need definition if universal to field
- DNA, RNA, MRI, CT, PCR (in biomedical context)
- AI, ML, CNN (in computer science context)

**Avoid Excessive Jargon**:
- ❌ "Utilized" → ✅ "Used"
- ❌ "Implement utilization of" → ✅ "Use"
- ❌ "A majority of" → ✅ "Most"

### Numbers and Statistics

**Present Statistics Clearly**:
- Always include measure of variability (SD, SE, CI)
- Report sample sizes: n=50
- Indicate significance: p<0.05, p<0.01, p<0.001
- Use symbols consistently: * for p<0.05, ** for p<0.01

**Format Numbers**:
- Round appropriately (avoid false precision)
- Use consistent decimal places
- Include units: 25 mg/dL, 37°C
- Large numbers: 1,000 or 1000 (be consistent)

**Example**:
```
Treatment increased response by 23.5% (95% CI: 18.2-28.8%, p<0.001, n=150)
```

## Visual-Text Integration

### Figure-Text Relationship

**Figure First, Text Second**:
1. Design poster around key figures
2. Add text to support and explain visuals
3. Ensure figures can stand alone

**Text Placement Relative to Figures**:
- **Above**: Context, "What you're about to see"
- **Below**: Explanation, statistics, caption
- **Beside**: Comparison, interpretation

### Callouts and Annotations

**On-Figure Annotations**:
```latex
\begin{tikzpicture}
  \node[inner sep=0] (img) {\includegraphics[width=10cm]{figure.pdf}};
  \draw[->, thick, red] (8,5) -- (6,3) node[left] {Key region};
  \draw[red, thick] (3,2) circle (1cm) node[above=1.2cm] {Anomaly};
\end{tikzpicture}
```

**Callout Boxes**:
```latex
\begin{tcolorbox}[colback=yellow!10, colframe=orange!80, 
                  title=Key Finding]
Our method reduces errors by 34\% compared to state-of-the-art.
\end{tcolorbox}
```

### Icons for Section Headers

**Visual Section Markers**:
```latex
\usepackage{fontawesome5}

\block{\faFlask~Introduction}{...}
\block{\faCog~Methods}{...}
\block{\faChartBar~Results}{...}
\block{\faLightbulb~Conclusions}{...}
```

## Content Adaptation Strategies

### From Paper to Poster

**Condensation Process**:

**1. Identify Core Message** (The Elevator Pitch):
- What's the one thing you want people to remember?
- If you had 30 seconds, what would you say?

**2. Select Key Results**:
- Choose 3-5 most impactful findings
- Omit supporting/secondary results
- Focus on figures with strong visual impact

**3. Simplify Methods**:
- Visual flowchart > text description
- Omit routine procedures
- Include only essential parameters

**4. Trim Literature Review**:
- One sentence background
- One sentence gap/motivation
- One sentence your contribution

**5. Condense Discussion**:
- Main conclusions only
- Brief limitations
- One sentence future direction

### For Different Audiences

**Specialist Audience** (Same Field):
- Can use field-specific jargon
- Less background needed
- Focus on novel methodology
- Emphasize nuanced findings

**General Scientific Audience**:
- Define key terms
- More context/background
- Broader implications
- Visual metaphors helpful

**Public/Lay Audience**:
- Minimal jargon, all defined
- Extensive context
- Real-world applications
- Analogies and simple language

**Example Adaptation**:

**Specialist**: "CRISPR-Cas9 knockout of BRCA1 induced synthetic lethality with PARP inhibitors"

**General**: "We used gene editing to make cancer cells vulnerable to existing drugs"

**Public**: "We found a way to make cancer treatments work better by targeting specific genetic weaknesses"

## Quality Control Checklist

### Content Review

**Clarity**:
- [ ] Main message immediately clear
- [ ] All acronyms defined
- [ ] Sentences short and direct
- [ ] No unnecessary jargon

**Completeness**:
- [ ] Research question/objective stated
- [ ] Methods sufficiently described
- [ ] Key results presented
- [ ] Conclusions drawn
- [ ] Limitations acknowledged

**Accuracy**:
- [ ] All statistics correct
- [ ] Figure captions accurate
- [ ] References properly cited
- [ ] No overstated claims

**Engagement**:
- [ ] Compelling title
- [ ] Visual interest
- [ ] Clear take-home message
- [ ] Conversation starters

### Readability Testing

**Distance Test**:
- Print at 25% scale
- View from 2-3 feet (simulates 8-12 feet for full poster)
- Can you read: Title? Section headers? Body text?

**Scan Test**:
- Give poster to colleague for 30 seconds
- Ask: "What is this poster about?"
- They should identify: Topic, approach, main finding

**Detail Test**:
- Ask colleague to read poster thoroughly (5 min)
- Ask: "What are the key conclusions?"
- Verify understanding matches your intent

## Common Content Mistakes

**1. Too Much Text**
- ❌ >1000 words
- ❌ Long paragraphs
- ❌ Full paper condensed
- ✅ 300-800 words, bullet points, key findings only

**2. Unclear Message**
- ❌ Multiple unrelated findings
- ❌ No clear conclusion
- ❌ Vague implications
- ✅ 1-3 main points, explicit conclusions

**3. Methods Overkill**
- ❌ Detailed protocols
- ❌ All parameters listed
- ❌ Routine procedures described
- ✅ Visual flowchart, key details only

**4. Poor Figure Integration**
- ❌ Figures without context
- ❌ Unclear captions
- ❌ Text doesn't reference figures
- ✅ Figures central, well-captioned, text integrated

**5. Missing Context**
- ❌ No background
- ❌ Undefined acronyms
- ❌ Assumes expert knowledge
- ✅ Brief context, definitions, accessible to broader audience

## Conclusion

Effective poster content:
- **Concise**: 300-800 words maximum
- **Visual**: 40-50% figures and graphics
- **Clear**: One main message, 3-5 key findings
- **Engaging**: Compelling story, not just facts
- **Accessible**: Appropriate for target audience
- **Actionable**: Clear implications and next steps

Remember: Your poster is a conversation starter, not a comprehensive treatise. Design content to intrigue, engage, and invite discussion.

