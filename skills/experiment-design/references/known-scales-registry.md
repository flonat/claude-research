# Known Scales Registry

> Validated psychological and behavioural scales for recognition during QSF parsing and survey construction.
> Read during Survey mode of `/experiment-design`.

## How to Use This Registry

1. **QSF parsing:** Match question items against known scales to identify validated instruments
2. **Survey construction:** Recommend appropriate scales for measured constructs
3. **Quality check:** Flag modifications to validated scales (changed items, altered anchors)

## Well-Being & Affect

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| SWLS (Satisfaction with Life) | 5 | 7-point Likert | Diener et al. (1985) |
| PANAS (Positive and Negative Affect) | 20 (10+10) | 5-point extent | Watson et al. (1988) |
| PANAS-SF (Short Form) | 10 (5+5) | 5-point extent | Thompson (2007) |
| WHO-5 Well-Being Index | 5 | 6-point frequency | WHO (1998) |
| PHQ-9 (Depression) | 9 | 4-point frequency | Kroenke et al. (2001) |
| GAD-7 (Anxiety) | 7 | 4-point frequency | Spitzer et al. (2006) |
| PSS (Perceived Stress) | 10 or 14 | 5-point frequency | Cohen et al. (1983) |
| PSS-4 (Short Form) | 4 | 5-point frequency | Cohen et al. (1983) |
| K6 (Psychological Distress) | 6 | 5-point frequency | Kessler et al. (2002) |

## Personality

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| BFI-10 (Big Five Short) | 10 (2 per factor) | 5-point agreement | Rammstedt & John (2007) |
| BFI-2 (Big Five) | 60 (12 per factor) | 5-point agreement | Soto & John (2017) |
| BFI-2-S (Short) | 30 | 5-point agreement | Soto & John (2017) |
| BFI-2-XS (Extra Short) | 15 | 5-point agreement | Soto & John (2017) |
| HEXACO-60 | 60 | 5-point agreement | Ashton & Lee (2009) |
| NFC (Need for Cognition) | 18 | 5-point agreement | Cacioppo et al. (1984) |
| NFC-6 (Short Form) | 6 | 5-point agreement | Lins de Holanda Coelho et al. (2020) |

## Trust & Social Preferences

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| Generalized Trust (WVS) | 1 | Binary | World Values Survey |
| Propensity to Trust (Mayer) | 8 | 5-point agreement | Mayer & Davis (1999) |
| Interpersonal Trust (Rotter) | 25 | 5-point agreement | Rotter (1967) |
| Trust in AI | 5-12 | 7-point agreement | Jian et al. (2000); Körber (2019) |
| SVO (Social Value Orientation) | 6 sliders | Continuous | Murphy et al. (2011) |
| Dictator Game | 1 decision | Allocation | Kahneman et al. (1986) |

## Self-Concept

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| Rosenberg Self-Esteem | 10 | 4-point agreement | Rosenberg (1965) |
| GSE (General Self-Efficacy) | 10 | 4-point agreement | Schwarzer & Jerusalem (1995) |
| SES (Socioeconomic Status) | 3 | Ladder/categorical | Adler et al. (2000) |
| Locus of Control | 29 | Forced choice | Rotter (1966) |

## Technology & AI

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| TAM (Technology Acceptance) | 12 | 7-point agreement | Davis (1989) |
| UTAUT (Unified Theory) | 31 | 7-point agreement | Venkatesh et al. (2003) |
| ATI (Affinity for Tech Interaction) | 9 | 6-point agreement | Franke et al. (2019) |
| NARS (Negative Attitudes to Robots) | 14 | 5-point agreement | Nomura et al. (2006) |
| AI Anxiety | 12 | 5-point agreement | Wang & Wang (2022) |
| Automation Trust (Jian) | 12 | 7-point agreement | Jian et al. (2000) |

## Decision Making & Risk

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| DOSPERT (Domain-Specific Risk) | 30 | 7-point likelihood | Blais & Weber (2006) |
| DOSPERT-Brief | 6 | 7-point likelihood | Frey et al. (2017) |
| Maximization Scale | 13 | 7-point agreement | Schwartz et al. (2002) |
| Maximization-7 (Short) | 7 | 7-point agreement | Dalal et al. (2015) |
| CRT (Cognitive Reflection Test) | 3 or 7 | Open-ended | Frederick (2005); Thomson & Oppenheimer (2016) |
| REI (Rational-Experiential Inventory) | 40 | 5-point agreement | Pacini & Epstein (1999) |

## Work & Organisational

| Scale | Items | Response | Key reference |
|-------|-------|----------|---------------|
| Job Satisfaction (MSQ-short) | 20 | 5-point satisfaction | Weiss et al. (1967) |
| Utrecht Work Engagement (UWES-9) | 9 | 7-point frequency | Schaufeli et al. (2006) |
| Organisational Commitment (OCQ) | 15 | 7-point agreement | Mowday et al. (1979) |
| Psychological Safety | 7 | 7-point agreement | Edmondson (1999) |
| Intrinsic Motivation (IMI) | 22 | 7-point agreement | Ryan (1982) |

## Demographics (Standard Items)

| Item | Recommended format |
|------|-------------------|
| Age | Open numeric or brackets (18-24, 25-34, ...) |
| Gender | Male / Female / Non-binary / Prefer not to say / Prefer to self-describe |
| Education | Less than HS / HS / Some college / Bachelor's / Master's / Doctorate |
| Income | Country-appropriate brackets with "Prefer not to say" |
| Employment | Full-time / Part-time / Self-employed / Unemployed / Student / Retired / Other |
| Ethnicity | Country-appropriate categories (follow census conventions) |

## Scale Modification Warnings

When a detected scale differs from the registry version, flag:

| Modification | Severity | Why it matters |
|-------------|----------|----------------|
| Items added | Minor | May affect factor structure |
| Items removed | Major | Breaks validated psychometrics |
| Anchor labels changed | Major | Changes interpretation of scores |
| Number of scale points changed | Major | Invalidates published norms |
| Item wording changed | Major | Affects content validity |
| Response direction reversed | Minor | Acceptable if scoring adjusted |
