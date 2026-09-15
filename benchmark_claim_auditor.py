
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def audit_pair(
    df,
    model_a,
    model_b,
    overall_column="MMLU All Subjects - EM",
    n_bootstrap=10000,
    random_seed=42,
):
    """
    Audit the strength of a benchmark comparison between two models.

    Input:
        One row per model.
        One overall benchmark score column.
        Multiple task/subject score columns.

    Returns:
        Dictionary containing descriptive statistics,
        uncertainty estimates, significance tests,
        leave-one-task-out stability, and outlier influence.
    """

    # Find model rows
    matches_a = df[df["Model"] == model_a]
    matches_b = df[df["Model"] == model_b]

    if len(matches_a) != 1:
        raise ValueError(
            f"Expected exactly one row for model_a, found {len(matches_a)}"
        )

    if len(matches_b) != 1:
        raise ValueError(
            f"Expected exactly one row for model_b, found {len(matches_b)}"
        )

    row_a = matches_a.iloc[0]
    row_b = matches_b.iloc[0]

    # Identify task columns
    task_columns = [
        c for c in df.columns
        if c not in ["Model", overall_column]
    ]

    if len(task_columns) == 0:
        raise ValueError("No task columns found.")

    # Convert task scores to numeric
    scores_a = pd.to_numeric(
        row_a[task_columns],
        errors="coerce"
    ).to_numpy(dtype=float)

    scores_b = pd.to_numeric(
        row_b[task_columns],
        errors="coerce"
    ).to_numpy(dtype=float)

    # Check for invalid values
    if np.isnan(scores_a).any() or np.isnan(scores_b).any():
        raise ValueError("Task scores contain missing or non-numeric values.")

    # Model A - Model B
    differences = scores_a - scores_b

    # ---------------------------------------------------------
    # DESCRIPTIVE STATISTICS
    # ---------------------------------------------------------

    wins = int(np.sum(differences > 0))
    ties = int(np.sum(differences == 0))
    losses = int(np.sum(differences < 0))

    mean_difference = float(np.mean(differences))
    median_difference = float(np.median(differences))
    std_difference = float(np.std(differences, ddof=1))

    # Paired Cohen's d
    if std_difference > 0:
        cohens_d = mean_difference / std_difference
    else:
        cohens_d = np.nan

    # Win rate excluding ties
    decisive_comparisons = wins + losses

    if decisive_comparisons > 0:
        win_rate = wins / decisive_comparisons
    else:
        win_rate = np.nan

    # ---------------------------------------------------------
    # WILCOXON SIGNED-RANK TEST
    # ---------------------------------------------------------

    nonzero_differences = differences[
        differences != 0
    ]

    if len(nonzero_differences) > 0:

        wilcoxon_statistic, wilcoxon_p_value = wilcoxon(
            nonzero_differences,
            alternative="two-sided"
        )

        wilcoxon_statistic = float(wilcoxon_statistic)
        wilcoxon_p_value = float(wilcoxon_p_value)

    else:
        wilcoxon_statistic = np.nan
        wilcoxon_p_value = np.nan

    # ---------------------------------------------------------
    # BOOTSTRAP
    # ---------------------------------------------------------

    rng = np.random.default_rng(random_seed)

    bootstrap_means = np.empty(n_bootstrap)

    for i in range(n_bootstrap):

        sample = rng.choice(
            differences,
            size=len(differences),
            replace=True
        )

        bootstrap_means[i] = np.mean(sample)

    bootstrap_ci_lower = float(
        np.percentile(bootstrap_means, 2.5)
    )

    bootstrap_ci_upper = float(
        np.percentile(bootstrap_means, 97.5)
    )

    bootstrap_probability_positive = float(
        np.mean(bootstrap_means > 0)
    )

    # ---------------------------------------------------------
    # LEAVE-ONE-TASK-OUT STABILITY
    # ---------------------------------------------------------

    loo_results = []

    tolerance = 1e-12

    for i, task in enumerate(task_columns):

        remaining = np.delete(
            differences,
            i
        )

        loo_mean = float(
            np.mean(remaining)
        )

        if loo_mean > tolerance:
            winner = model_a

        elif loo_mean < -tolerance:
            winner = model_b

        else:
            winner = "Tie"

        loo_results.append({
            "Removed Task": task,
            "Mean Difference": loo_mean,
            "Winner": winner
        })

    loo_df = pd.DataFrame(loo_results)

    loo_model_a_wins = int(
        np.sum(loo_df["Winner"] == model_a)
    )

    loo_model_b_wins = int(
        np.sum(loo_df["Winner"] == model_b)
    )

    loo_ties = int(
        np.sum(loo_df["Winner"] == "Tie")
    )

    # ---------------------------------------------------------
    # OUTLIER INFLUENCE
    # ---------------------------------------------------------

    absolute_order = np.argsort(
        np.abs(differences)
    )[::-1]

    outlier_results = {}

    for k in [1, 3, 5, 10]:

        k_actual = min(
            k,
            len(differences)
        )

        keep = np.ones(
            len(differences),
            dtype=bool
        )

        keep[
            absolute_order[:k_actual]
        ] = False

        outlier_results[
            f"remove_{k_actual}"
        ] = float(
            np.mean(differences[keep])
        )

    # ---------------------------------------------------------
    # TASK-LEVEL TABLE
    # ---------------------------------------------------------

    task_differences = pd.DataFrame({
        "Task": task_columns,
        "Model A Score": scores_a,
        "Model B Score": scores_b,
        "Difference": differences,
        "Absolute Difference": np.abs(differences)
    })

    task_differences = task_differences.sort_values(
        "Difference",
        ascending=False
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # RETURN RESULTS
    # ---------------------------------------------------------

    return {

        "model_a": model_a,
        "model_b": model_b,

        "overall_score_a": float(
            row_a[overall_column]
        ),

        "overall_score_b": float(
            row_b[overall_column]
        ),

        "overall_gap": float(
            row_a[overall_column]
            - row_b[overall_column]
        ),

        "num_tasks": len(task_columns),

        "wins": wins,
        "ties": ties,
        "losses": losses,

        "win_rate_excluding_ties": float(
            win_rate
        ),

        "mean_difference": mean_difference,
        "median_difference": median_difference,
        "std_difference": std_difference,

        "cohens_d": float(cohens_d),

        "wilcoxon_statistic": wilcoxon_statistic,
        "wilcoxon_p_value": wilcoxon_p_value,

        "bootstrap_ci_lower": bootstrap_ci_lower,
        "bootstrap_ci_upper": bootstrap_ci_upper,

        "bootstrap_probability_positive":
            bootstrap_probability_positive,

        "loo_model_a_wins":
            loo_model_a_wins,

        "loo_model_b_wins":
            loo_model_b_wins,

        "loo_ties":
            loo_ties,

        "loo_results":
            loo_df,

        "outlier_influence":
            outlier_results,

        "task_differences":
            task_differences,

        "bootstrap_distribution":
            bootstrap_means
    }


def summarize_claim(result):
    """
    Produce an interpretable evidence profile.

    IMPORTANT:
    The thresholds used here are engineering heuristics,
    not scientifically validated universal thresholds.
    """

    gap = result["overall_gap"]
    d = result["cohens_d"]
    win_rate = result["win_rate_excluding_ties"]
    p_value = result["wilcoxon_p_value"]

    ci_lower = result["bootstrap_ci_lower"]
    ci_upper = result["bootstrap_ci_upper"]

    loo_a = result["loo_model_a_wins"]
    loo_b = result["loo_model_b_wins"]
    loo_ties = result["loo_ties"]

    total_loo = loo_a + loo_b + loo_ties

    # Does the bootstrap CI exclude zero?
    ci_excludes_zero = (
        ci_lower > 0
        or ci_upper < 0
    )

    # Ranking stability
    if total_loo > 0:
        loo_stability = loo_a / total_loo
    else:
        loo_stability = np.nan

    # Evidence components
    statistically_significant = (
        p_value < 0.05
    )

    meaningful_effect = (
        abs(d) >= 0.2
    )

    consistent = (
        win_rate >= 0.60
    )

    stable = (
        loo_stability >= 0.80
    )

    # Overall classification
    if (
        statistically_significant
        and ci_excludes_zero
        and meaningful_effect
        and consistent
        and stable
    ):
        classification = "Strong evidence"

    elif (
        statistically_significant
        and ci_excludes_zero
        and (consistent or stable)
    ):
        classification = "Moderate evidence"

    elif (
        abs(gap) > 0
        and (
            not ci_excludes_zero
            or not statistically_significant
            or not consistent
            or not stable
        )
    ):
        classification = "Weak / fragile evidence"

    else:
        classification = "No clear superiority"

    return {

        "claim":
            f"{result['model_a']} > {result['model_b']}",

        "classification":
            classification,

        "overall_gap":
            gap,

        "cohens_d":
            d,

        "win_rate":
            win_rate,

        "wilcoxon_p_value":
            p_value,

        "bootstrap_ci_lower":
            ci_lower,

        "bootstrap_ci_upper":
            ci_upper,

        "statistically_significant":
            statistically_significant,

        "ci_excludes_zero":
            ci_excludes_zero,

        "meaningful_effect":
            meaningful_effect,

        "consistent":
            consistent,

        "stable":
            stable,

        "loo_stability":
            loo_stability
    }
