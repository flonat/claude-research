# Machine Learning / NLP Checklist

> Load when the paper uses: classification, prediction, topic modelling, LLM annotation, text analysis, deep learning, or any ML pipeline.

## Critical Red Flags

| Issue | What to check | Severity |
|-------|--------------|----------|
| **Data leakage** | Information from test set bleeding into training? Temporal leakage (future data predicting past)? Feature engineering using full dataset? | Critical — invalidates all results |
| **Inappropriate baselines** | Comparing to weak strawmen rather than current SOTA? Missing obvious baselines? | Major |
| **Benchmark gaming** | Optimising for specific benchmarks rather than general capability? Hyperparameter tuning on test set? | Major |
| **LLM evaluation pitfalls** | Training data contamination? Prompt sensitivity not tested? No statistical testing of differences? | Critical if LLM is the method |

## Standard Checks

### Data Pipeline
- [ ] Train/validation/test split clearly described
- [ ] Split strategy appropriate (random, temporal, stratified, grouped)
- [ ] No data leakage between splits (check feature engineering pipeline)
- [ ] Class balance reported and handled (oversampling, weighting, stratification)
- [ ] Preprocessing steps documented and applied consistently across splits

### Model Selection
- [ ] Multiple models compared (not just one)
- [ ] Hyperparameter tuning on validation set only (never test)
- [ ] Model complexity justified (why this architecture?)
- [ ] Regularisation strategy described
- [ ] Cross-validation or bootstrap for uncertainty quantification

### Evaluation
- [ ] Metrics appropriate for the task and class balance
- [ ] Confidence intervals or significance tests on performance metrics
- [ ] Per-class performance reported (not just aggregate)
- [ ] Confusion matrix or equivalent breakdown
- [ ] Comparison to human performance where applicable

### LLM-Specific (if applicable)
- [ ] Prompt documented verbatim
- [ ] Prompt sensitivity tested (multiple phrasings, same task)
- [ ] Model version and temperature specified
- [ ] Training data contamination addressed
- [ ] Human validation sample: N >= 200, inter-annotator agreement kappa >= 0.7
- [ ] Cost and reproducibility implications discussed
- [ ] Zero-shot vs few-shot vs fine-tuned — choice justified

### NLP / Text Analysis
- [ ] Preprocessing justified (stopwords, stemming, frequency thresholds)
- [ ] Document unit defined (post, paragraph, article)
- [ ] For topic models: K selection method reported (coherence, held-out likelihood)
- [ ] Topic validation: 20+ documents per topic read by human
- [ ] For embeddings: model choice and dimensionality justified

### Interpretability
- [ ] Feature importance or attention analysis (if claiming explanatory insights)
- [ ] Limitations of interpretation acknowledged (correlation != causation in ML)
- [ ] Spurious correlations investigated (are predictions driven by artifacts?)

## Common Mistakes to Flag

1. Reporting accuracy on imbalanced datasets (use F1, AUC, or balanced accuracy)
2. Tuning hyperparameters on the test set (inflated performance)
3. Using LLM annotations without human validation
4. Claiming "the model understands X" from classification performance
5. Presenting ML predictions as causal evidence
6. No error analysis — what does the model get wrong and why?
7. Prompt engineering as methodology without systematic evaluation

## Probing Questions

See `skills/shared/method-probing-questions.md` — sections: Machine Learning / Classification, Topic Modeling / NLP.
