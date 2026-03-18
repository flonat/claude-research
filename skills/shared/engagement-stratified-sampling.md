# Engagement-Stratified Sampling

> Shared reference for social media and digital trace research. Ensures representative sampling across the engagement distribution. Prevents viral-content bias. Adapted from CommDAAF (Xu 2026).

## Principle

**Convenience samples over-represent viral content.** Most social media datasets are skewed — a small fraction of posts drive most engagement. Sampling without stratification produces findings that describe viral content, not typical content. Engagement-stratified sampling ensures coverage across the full distribution.

---

## Standard Engagement Tiers

| Tier | Percentile | Purpose | Typical content |
|------|------------|---------|-----------------|
| **Viral** | Top 5% | What makes content break out | Influencer posts, breakthrough moments |
| **High** | 75th–95th | Successful content | Engaged audiences, topical resonance |
| **Medium** | 25th–75th | Baseline performance | Typical posts, average engagement |
| **Low** | Bottom 25% | Why content fails / background noise | Low visibility, potential bot content |
| **Zero** | Engagement = 0 | No-spread baseline | Posts that never circulated |

---

## Engagement Metric Construction

### Standard composite (social media platforms)

```python
import numpy as np

# Log-transform to handle skewness, +1 to handle zeros
data['engagement'] = (
    np.log(data['retweet_count'] + 1) +
    np.log(data['like_count'] + 1) +
    np.log(data['quote_count'].fillna(0) + 1)
)
```

**Document any modification** to this formula. Platform-specific variants:

| Platform | Available metrics | Notes |
|----------|------------------|-------|
| X/Twitter | Retweets, likes, quotes, replies | Quote count often missing in older data |
| Reddit | Upvotes, comments, awards | Score = upvotes - downvotes |
| YouTube | Views, likes, comments | Views dominate; consider likes/views ratio |
| Bluesky | Likes, reposts, replies | Open API, no auth required |
| Instagram | Likes, comments, shares, saves | Shares/saves often not available |

### R equivalent

```r
data$engagement <- log(data$retweet_count + 1) +
                   log(data$like_count + 1) +
                   log(replace_na(data$quote_count, 0) + 1)
```

---

## Stratified Sampling Implementation

### Python

```python
def engagement_stratified_sample(data, engagement_col='engagement',
                                  n_per_tier=100, seed=42):
    """Sample equally from each engagement tier."""
    p95 = data[engagement_col].quantile(0.95)
    p75 = data[engagement_col].quantile(0.75)
    p25 = data[engagement_col].quantile(0.25)

    def assign_tier(val):
        if val >= p95: return 'viral'
        elif val >= p75: return 'high'
        elif val >= p25: return 'medium'
        else: return 'low'

    data = data.copy()
    data['engagement_tier'] = data[engagement_col].apply(assign_tier)

    sample = (data.groupby('engagement_tier')
              .apply(lambda x: x.sample(min(len(x), n_per_tier),
                                        random_state=seed))
              .reset_index(drop=True))

    return sample
```

### R

```r
engagement_stratified_sample <- function(data, engagement_col = "engagement",
                                          n_per_tier = 100, seed = 42) {
  set.seed(seed)
  q <- quantile(data[[engagement_col]], probs = c(0.25, 0.75, 0.95))

  data$engagement_tier <- cut(data[[engagement_col]],
    breaks = c(-Inf, q[1], q[2], q[3], Inf),
    labels = c("low", "medium", "high", "viral"))

  data %>%
    group_by(engagement_tier) %>%
    slice_sample(n = min(n(), n_per_tier)) %>%
    ungroup()
}
```

---

## Multi-Criteria Sampling

When engagement is one of several strata:

```python
def multi_criteria_sample(data, strata, total_n=500, seed=42):
    """
    strata = {
        'engagement_tier': {'allocation': 'equal'},
        'language': {'allocation': 'proportional'},
        'date': {'allocation': 'coverage'}  # at least 1 per unique value
    }
    """
    # Implementation depends on specific constraints
    # Key principle: engagement strata are equal, others proportional or coverage
    pass
```

**Common multi-criteria designs:**

| Criterion | Allocation | Rationale |
|-----------|-----------|-----------|
| Engagement tier | Equal | Prevent viral bias |
| Language | Proportional | Reflect population distribution |
| Time period | Coverage (≥1 per day) | Prevent temporal blind spots |
| Account type | Proportional or capped | Prevent influencer domination |
| Verified status | Capped (≤30%) | Verified accounts are over-studied |

---

## Power Analysis for Stratified Designs

| Design | Min n/group | Detects | Total for 4 tiers |
|--------|------------|---------|-------------------|
| 2-group comparison, d=0.5 | 64 | Medium effect | 128 |
| 2-group comparison, d=0.3 | 175 | Small effect | 350 |
| 7 frames × 4 tiers, d=0.3 | 50/cell | Small effect | 1,400 |
| Regression, 5 predictors | 100 total | Medium R² | 100 |

**Rule:** Calculate power before committing to sample size. Under-powered stratified samples are worse than well-powered random samples.

---

## Saturation Detection

For qualitative or exploratory coding:

```python
def check_saturation(coded_data, code_var='frame', window=50, threshold=0.05):
    """Check if last `window` items added < `threshold` proportion of new codes."""
    all_codes = set()
    new_code_positions = []

    for i, item in enumerate(coded_data):
        code = item[code_var]
        if code not in all_codes:
            all_codes.add(code)
            new_code_positions.append(i)

    if not new_code_positions:
        return {'saturated': True, 'n': len(coded_data), 'last_new': 0}

    last_new = new_code_positions[-1]
    items_since = len(coded_data) - last_new
    return {
        'saturated': items_since >= window,
        'n': len(coded_data),
        'last_new': last_new,
        'items_since_new': items_since
    }
```

**Saturation guideline:** If the last 50 coded items produced no new codes/themes, consider stopping.

---

## Integration

### In `/data-analysis` Phase 1

When data includes engagement metrics (likes, shares, retweets, etc.), automatically:
1. Compute composite engagement score
2. Assign tiers
3. Report tier distribution in EDA output
4. Flag if analysis sample is not engagement-stratified

### In `/experiment-design`

When designing content analysis studies:
1. Include engagement stratification in sampling plan
2. Calculate power per tier
3. Document tier boundaries in pre-analysis plan

### In review agents

Check whether social media studies:
- Report their sampling strategy
- Account for engagement distribution
- Avoid over-representing viral content
- Flag as Major if unstratified convenience sample is used for causal claims

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Sampling by keyword only | Over-represents viral posts with the keyword | Stratify by engagement after keyword filter |
| Using "top tweets" API endpoint | Only returns high-engagement content | Use full archive search, then stratify |
| Treating retweet count as continuous DV | Highly skewed, zero-inflated | Use engagement tiers as strata or log-transform |
| Equal allocation when one tier is tiny | Viral tier (5%) may have < n_per_tier items | Sample min(available, target), report actual n |
