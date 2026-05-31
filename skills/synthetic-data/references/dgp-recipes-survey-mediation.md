# DGP Recipes: Survey & Mediation

> Data generating process recipes for survey data and mediation analysis. Read during all modes of /synthetic-data.

## Survey Data (Likert Scales, Demographics, Attention Checks)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

df <- fabricate(
  N = 400,
  # Demographics
  age = round(rnorm(N, mean = 35, sd = 12)),
  age = pmax(18, pmin(age, 80)),                     # clip to [18, 80]
  female = draw_binary(prob = 0.55, N = N),
  education = sample(c("high_school", "bachelors", "masters", "phd"),
                     N, replace = TRUE,
                     prob = c(0.25, 0.40, 0.25, 0.10)),

  # Treatment condition
  condition = sample(c("control", "ai_low", "ai_high"),
                     N, replace = TRUE),

  # Latent constructs
  trust_latent = rnorm(N, mean = ifelse(condition == "ai_high", 0.5, 0), sd = 1),
  satisfaction_latent = rnorm(N, mean = 0, sd = 1) + 0.4 * trust_latent,

  # Likert items (7-point scale) with floor/ceiling effects
  trust_1 = pmin(7, pmax(1, round(4 + trust_latent + rnorm(N, sd = 0.8)))),
  trust_2 = pmin(7, pmax(1, round(4 + trust_latent + rnorm(N, sd = 0.9)))),
  trust_3 = pmin(7, pmax(1, round(4 + trust_latent + rnorm(N, sd = 0.7)))),
  trust_4_r = pmin(7, pmax(1, round(4 - trust_latent + rnorm(N, sd = 0.8)))),  # reverse-coded
  satisfaction_1 = pmin(7, pmax(1, round(4 + satisfaction_latent + rnorm(N, sd = 0.8)))),
  satisfaction_2 = pmin(7, pmax(1, round(4 + satisfaction_latent + rnorm(N, sd = 0.9)))),

  # Attention check: "Please select 'Strongly Agree'"
  attention_correct = draw_binary(prob = 0.92, N = N),

  # Response time (log-normal, seconds)
  response_time = round(rlnorm(N, meanlog = log(300), sdlog = 0.5))
)

# Add realistic missingness (MAR: older respondents more likely to skip items)
miss_prob <- plogis(-3 + 0.03 * df$age)
for (col in c("trust_2", "satisfaction_2")) {
  df[[col]][runif(nrow(df)) < miss_prob] <- NA
}

write.csv(df, "data/synthetic/survey.csv", row.names = FALSE)
cat("Missingness rate:", mean(is.na(df$trust_2)), "\n")
```

### Python: numpy

```python
import numpy as np
import pandas as pd
from scipy.special import expit  # logistic function

np.random.seed(42)

N = 400
age = np.clip(np.round(np.random.normal(35, 12, N)).astype(int), 18, 80)
female = np.random.binomial(1, 0.55, N)
education = np.random.choice(
    ["high_school", "bachelors", "masters", "phd"],
    N, p=[0.25, 0.40, 0.25, 0.10],
)
condition = np.random.choice(["control", "ai_low", "ai_high"], N)

# Latent constructs
trust_latent = np.random.normal(
    np.where(condition == "ai_high", 0.5, 0), 1
)
satisfaction_latent = np.random.normal(0, 1, N) + 0.4 * trust_latent

# Likert items (7-point)
def to_likert(latent, noise_sd=0.8):
    return np.clip(np.round(4 + latent + np.random.normal(0, noise_sd, N)), 1, 7).astype(int)

trust_1 = to_likert(trust_latent, 0.8)
trust_2 = to_likert(trust_latent, 0.9)
trust_3 = to_likert(trust_latent, 0.7)
trust_4_r = to_likert(-trust_latent, 0.8)  # reverse-coded
satisfaction_1 = to_likert(satisfaction_latent, 0.8)
satisfaction_2 = to_likert(satisfaction_latent, 0.9)

# Attention check
attention_correct = np.random.binomial(1, 0.92, N)

# Response time (log-normal)
response_time = np.round(np.random.lognormal(np.log(300), 0.5, N)).astype(int)

df = pd.DataFrame({
    "id": range(1, N + 1),
    "age": age, "female": female, "education": education,
    "condition": condition,
    "trust_1": trust_1, "trust_2": trust_2, "trust_3": trust_3,
    "trust_4_r": trust_4_r,
    "satisfaction_1": satisfaction_1, "satisfaction_2": satisfaction_2,
    "attention_correct": attention_correct,
    "response_time": response_time,
})

# MAR missingness: older respondents more likely to skip
miss_prob = expit(-3 + 0.03 * age)
for col in ["trust_2", "satisfaction_2"]:
    mask = np.random.random(N) < miss_prob
    df.loc[mask, col] = np.nan

df.to_csv("data/synthetic/survey.csv", index=False)
print(f"Missingness rate (trust_2): {df['trust_2'].isna().mean():.2%}")
```

---

## Mediation (X -> M -> Y with Direct and Indirect Effects)

### R: fabricatr

```r
library(fabricatr)

set.seed(42)

# Path coefficients
a <- 0.4   # X -> M
b <- 0.5   # M -> Y (controlling for X)
c_prime <- 0.2  # X -> Y direct effect
# Indirect effect = a * b = 0.20
# Total effect = c_prime + a * b = 0.40

df <- fabricate(
  N = 600,
  # Covariates
  age = round(rnorm(N, 35, 10)),
  female = draw_binary(prob = 0.5, N = N),

  # Treatment
  X = draw_binary(prob = 0.5, N = N),

  # Mediator (continuous)
  noise_m = rnorm(N, sd = 0.8),
  M = 3.0 + a * X + 0.01 * age + noise_m,

  # Outcome
  noise_y = rnorm(N, sd = 0.7),
  Y = 1.0 + c_prime * X + b * M + 0.02 * age - 0.1 * female + noise_y
)

cat("True indirect effect (a*b):", a * b, "\n")
cat("True direct effect (c'):", c_prime, "\n")
cat("True total effect:", c_prime + a * b, "\n")

write.csv(df, "data/synthetic/mediation.csv", row.names = FALSE)
```

### Python: numpy

```python
import numpy as np
import pandas as pd

np.random.seed(42)

N = 600
a = 0.4      # X -> M
b = 0.5      # M -> Y
c_prime = 0.2  # X -> Y direct

age = np.round(np.random.normal(35, 10, N)).astype(int)
female = np.random.binomial(1, 0.5, N)
X = np.random.binomial(1, 0.5, N)

noise_m = np.random.normal(0, 0.8, N)
M = 3.0 + a * X + 0.01 * age + noise_m

noise_y = np.random.normal(0, 0.7, N)
Y = 1.0 + c_prime * X + b * M + 0.02 * age - 0.1 * female + noise_y

df = pd.DataFrame({
    "id": range(1, N + 1),
    "age": age, "female": female,
    "X": X, "M": np.round(M, 4), "Y": np.round(Y, 4),
})

print(f"True indirect effect (a*b): {a * b}")
print(f"True direct effect (c'): {c_prime}")
print(f"True total effect: {c_prime + a * b}")

df.to_csv("data/synthetic/mediation.csv", index=False)
```

---

## Summary Table

| Design | Key parameters | Typical N | R package | Python package |
|--------|---------------|-----------|-----------|----------------|
| Simple RCT | Effect size, noise SD | 200-1000 | fabricatr | numpy |
| Factorial 2x2 | Main effects, interaction | 400-1600 | fabricatr | numpy |
| Factorial 2x3 | Main effects, interactions | 600-1800 | fabricatr | numpy |
| Cluster RCT | ICC, n_clusters, cluster_size | 400-1200 | fabricatr | numpy |
| DiD (staggered) | Unit/time FE, treatment timing, TE dynamics | 500-5000 | fabricatr + dplyr | numpy + pandas |
| RDD | Cutoff, slopes, jump | 500-2000 | fabricatr | numpy |
| Survey | Latent constructs, Likert noise, missingness | 200-1000 | fabricatr | numpy + scipy |
| Mediation | Path coefficients (a, b, c') | 400-1000 | fabricatr | numpy |
