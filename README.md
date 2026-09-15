# Benchmark Claim Auditor

## When does a higher benchmark score actually provide strong evidence?

Benchmark leaderboards often reduce model performance to a single aggregate score. This creates a simple question:

> **When does a higher average benchmark score actually provide strong evidence that one model is better than another?**

This project develops a practical auditing workflow for evaluating benchmark claims beyond the headline average.

Instead of treating a small leaderboard gap as sufficient evidence, the auditor examines:

- magnitude of the task-level difference
- consistency across tasks
- statistical uncertainty
- effect size
- sensitivity to aggregation method
- leave-one-task-out stability
- sensitivity to extreme task-level differences

The current case study applies the workflow to **HELM MMLU**, comparing the highest-scoring model in the reference data against the next five models.

---

## Research Question

A benchmark can report:

> Model A scores 87.3% and Model B scores 87.2%.

The leaderboard therefore ranks A above B.

But this does not automatically tell us:

- whether A wins across most tasks
- whether the average difference is statistically distinguishable from zero
- whether the difference is practically meaningful
- whether the conclusion changes under another aggregation method
- whether a small number of subjects strongly influence the result
- whether the ranking survives removal of individual subjects

This project treats benchmark comparison as an **evidence assessment problem**, rather than simply a ranking problem.

---

## Connection to Existing Research

The project is inspired by the 2026 position paper:

**"State-of-the-Art Claims Require State-of-the-Art Evidence"**

by YongKyung Oh.

The original work argues that marginal improvements in aggregate benchmark scores can provide weak evidence of genuine superiority and proposes examining properties such as:

1. **Magnitude**
2. **Consistency**
3. **Stability**

This project uses those ideas as a starting point and builds a more practical auditing workflow around them.

### What is reproduced vs extended?

The project does **not** claim to reproduce the entire original paper.

Instead:

- the underlying MMLU benchmark data comes from the same general benchmark-evaluation ecosystem
- the comparison is performed at the subject level
- paired effect size, win rate, and Wilcoxon analysis provide baseline evidence
- bootstrap uncertainty, aggregation sensitivity, leave-one-subject-out analysis, and outlier sensitivity extend the basic auditing workflow

The goal is a reusable **benchmark claim auditing tool**, not a reimplementation of the entire paper.

---

# Case Study: HELM MMLU

The MMLU data contains:

- **79 models**
- **57 subjects**
- one overall MMLU score
- one score for each subject

The primary model in this experiment is:

**Claude 3.5 Sonnet (20241022)**

Overall score:

**87.3%**

It is compared against the next five models in the reference ranking:

| Model | Overall Score | Gap |
|---|---:|---:|
| Claude 3.5 Sonnet (20241022) | 87.3% | — |
| DeepSeek v3 | 87.2% | +0.1 pp |
| Gemini 1.5 Pro (002) | 86.9% | +0.4 pp |
| Claude 3.5 Sonnet (20240620) | 86.5% | +0.8 pp |
| Claude 3 Opus (20240229) | 84.6% | +2.7 pp |
| Llama 3.1 Instruct Turbo (405B) | 84.5% | +2.8 pp |

---

# Main Findings

## 1. A tiny leaderboard gap can provide very weak evidence

Claude scores **87.3%** versus DeepSeek v3 at **87.2%**.

The headline gap is therefore only:

**+0.1 percentage points**

At the subject level:

- Claude wins: **26**
- ties: **6**
- DeepSeek wins: **25**
- mean difference: **+0.070 pp**
- median difference: **0 pp**
- paired Cohen's d: **0.018**
- Wilcoxon p-value: **0.683**
- 95% bootstrap CI: approximately **[-0.98, +1.06] pp**

The result is therefore highly uncertain at the subject level.

Importantly, this does **not** prove that the two models are equally capable.

It shows that the 0.1-point leaderboard advantage provides **weak evidence of broad subject-level superiority**.

---

## 2. The evidence becomes stronger as the leaderboard gap grows

The five comparisons show a useful progression.

| Comparison | Overall Gap | Mean Difference | Cohen's d | Win Rate | Evidence |
|---|---:|---:|---:|---:|---|
| DeepSeek v3 | +0.1 pp | +0.070 pp | 0.018 | 51.0% | Weak / fragile |
| Gemini 1.5 Pro | +0.4 pp | +0.393 pp | 0.092 | 63.0% | Weak / fragile |
| Claude 3.5 Sonnet (20240620) | +0.8 pp | +0.726 pp | 0.272 | 63.3% | Moderate |
| Claude 3 Opus | +2.7 pp | +2.705 pp | 0.756 | 82.7% | Strong |
| Llama 3.1 405B | +2.8 pp | +2.746 pp | 0.890 | 83.0% | Strong |

The important observation is not a particular universal threshold.

Instead:

> **A leaderboard gap becomes more convincing when it is accompanied by consistent task-level wins, meaningful effect size, uncertainty that excludes zero, and stability under perturbation.**

The thresholds used by the auditor should therefore be interpreted as practical heuristics, not universal statistical laws.

---

# 3. Mean, median, and trimmed mean can tell different stories

Aggregation itself can affect the conclusion.

For Claude vs DeepSeek:

- mean difference: **+0.070 pp**
- median difference: **0 pp**
- 10% trimmed mean: **+0.219 pp**

The mean suggests a small Claude advantage.

The median produces a tie.

The trimmed mean restores a positive advantage.

This demonstrates why a single aggregate statistic can hide information about the distribution of task-level outcomes.

For larger gaps, the conclusion is much less sensitive to the aggregation method.

---

# 4. The overall ranking is stable, but individual models can move

Across all 79 MMLU models, rankings produced using:

- arithmetic mean
- median
- 10% trimmed mean

are highly correlated.

Spearman correlations:

| Comparison | Spearman ρ |
|---|---:|
| Mean vs Median | 0.986 |
| Mean vs 10% Trimmed Mean | 0.999 |
| Median vs 10% Trimmed Mean | 0.990 |

This means the overall leaderboard is not completely transformed by changing the aggregation method.

However, some individual models move substantially in rank.

The practical lesson is:

> High rank correlation does not mean every individual model's position is equally robust.

---

# 5. Leave-one-subject-out analysis exposes stability

For every model comparison, the auditor removes each subject one at a time and recomputes the mean difference.

For Claude vs DeepSeek:

- minimum leave-one-out mean: approximately **−0.143 pp**
- maximum: approximately **+0.316 pp**
- range: approximately **0.459 pp**

Claude wins the leave-one-subject-out comparison in:

- **50 / 57** cases

DeepSeek wins in:

- **6 / 57**

There is:

- **1 tie**

The key point is that the headline +0.1 pp difference is small enough that individual subjects can materially change the aggregate difference, even though Claude remains ahead in most leave-one-out analyses.

---

# 6. Extreme subjects influence the aggregate

The auditor also removes the most extreme absolute subject-level differences.

For Claude vs DeepSeek:

| Analysis | Mean Difference |
|---|---:|
| All subjects | +0.070 pp |
| Remove 10 most extreme subjects | +0.219 pp |

The extreme subjects include large differences in **both directions**.

Therefore, the correct interpretation is **not** that outliers simply "created" Claude's advantage.

Instead:

> **The aggregate mean is sensitive to extreme task-level differences, and those differences can materially change the reported average.**

This is precisely why outlier sensitivity is useful when auditing benchmark claims.

---

# Methodology

For a pair of models A and B, the auditor constructs paired task-level differences:

**dᵢ = score(A, i) − score(B, i)**

It then evaluates several dimensions of evidence.

## 1. Magnitude

### Mean difference

The average task-level advantage.

### Median difference

The typical task-level advantage under a median-based aggregation.

### 10% trimmed mean

The mean after removing the most extreme 10% of task-level differences.

### Paired Cohen's d

A standardized measure of the magnitude of the paired differences.

---

## 2. Consistency

The auditor counts:

- wins
- ties
- losses

and calculates:

**Win Rate = wins / (wins + losses)**

Ties are excluded from the denominator.

---

## 3. Statistical evidence

### Wilcoxon signed-rank test

A paired non-parametric test is applied to non-zero task-level differences.

### Bootstrap confidence interval

The task-level differences are resampled **10,000 times** to estimate uncertainty around the mean difference.

The bootstrap analysis reports:

- 95% confidence interval
- fraction of bootstrap samples with positive mean difference

---

## 4. Stability

### Leave-one-subject-out analysis

Each subject is removed once.

The mean difference is recomputed.

This produces:

- minimum mean difference
- maximum mean difference
- range

This measures how sensitive the conclusion is to individual subjects.

---

## 5. Outlier sensitivity

The auditor removes the:

- 1 most extreme subject
- 3 most extreme subjects
- 5 most extreme subjects
- 10 most extreme subjects

based on absolute task-level difference.

This reveals whether the aggregate result is highly sensitive to extreme task-level outcomes.

---

## 6. Aggregation sensitivity

The same comparison is evaluated using:

- mean
- median
- 10% trimmed mean

This tests whether the conclusion depends heavily on the chosen aggregation rule.

---

# Evidence Classification

The auditor provides an interpretable evidence label:

- **Strong evidence**
- **Moderate evidence**
- **Weak / fragile evidence**
- **No clear superiority**

These labels are intended as a **practical evidence heuristic**.

They are **not** universal statistical thresholds and should not be interpreted as formal hypothesis-test outcomes.

The underlying statistics are always reported separately.

---

# Figures

The project currently produces eight research figures.

### 1. Leaderboard gap vs subject-level mean difference

Shows whether the aggregate leaderboard gap corresponds to task-level improvement.

### 2. Mean difference with bootstrap CI

Shows uncertainty around the task-level mean difference.

### 3. Subject-level win rate

Shows consistency across subjects.

### 4. Aggregation sensitivity

Compares mean, median, and trimmed mean conclusions.

### 5. Leave-one-subject-out stability

Shows sensitivity to individual subjects.

### 6. Outlier sensitivity

Shows how extreme task-level differences affect the aggregate.

### 7. Leaderboard gap vs effect size

Compares headline improvement with standardized task-level effect size.

### 8. Evidence profile

Provides a visual summary of several diagnostics.

The evidence profile is a visualization aid only and is **not** treated as a validated composite score.

---

# Repository Structure

```text
benchmark-claim-auditor/
│
├── benchmark_claim_auditor.py
│
├── data/
│   └── mmlu.csv
│
├── figures/
│   ├── overall_vs_subject_mean_gap.png
│   ├── mean_difference_bootstrap_ci.png
│   ├── subject_win_rate.png
│   ├── aggregation_sensitivity.png
│   ├── loo_stability.png
│   ├── outlier_sensitivity.png
│   ├── overall_gap_vs_effect_size.png
│   └── evidence_profile.png
│
├── results/
│   ├── mmlu_claim_audit.csv
│   ├── mmlu_claim_audit.json
│   └── reproducibility_manifest.json
│
└── README.md

# Reproducibility

The main experiment uses:

Python 3.x
NumPy
pandas
SciPy
Matplotlib
random seed: 42
bootstrap resamples: 10,000

The complete numerical results are stored in:

results/mmlu_claim_audit.csv
results/mmlu_claim_audit.json

The experiment configuration is recorded in:

results/reproducibility_manifest.json

The reusable analysis logic is contained in:

benchmark_claim_auditor.py
Limitations

This project is intentionally a benchmark-auditing case study rather than a claim about all benchmarks.

1. Single benchmark case study

The current empirical analysis focuses on MMLU.

Results should not automatically be generalized to every benchmark.

2. Observational benchmark data

The analysis evaluates reported model scores rather than independently rerunning every model evaluation.

3. Model versions matter

Different model snapshots may have different training data, prompting, evaluation settings, or release conditions.

4. Statistical significance is not practical significance

A statistically detectable difference is not necessarily important in practice.

Likewise, failure to reach statistical significance does not prove equality.

5. Evidence labels are heuristics

The classification system is an interpretability layer over several diagnostics, not a formally validated statistical decision procedure.

6. Task weighting is not universally determined

Equal weighting treats every MMLU subject equally. Different weighting schemes could produce different aggregate conclusions.

What This Project Demonstrates

The main contribution of this project is not a new benchmark or a new model.

It demonstrates a research workflow for asking:

Is the evidence actually strong enough to support the claim suggested by the leaderboard?

The workflow moves from:

headline score → task-level differences → magnitude → consistency → uncertainty → stability → sensitivity → evidence profile

This makes benchmark comparisons more transparent and gives researchers a systematic way to stress-test leaderboard claims.

References

Oh, YongKyung.
State-of-the-Art Claims Require State-of-the-Art Evidence.
ICML 2026, in press.

The implementation is informed by the accompanying benchmark-fragility research and its publicly available analysis framework.
