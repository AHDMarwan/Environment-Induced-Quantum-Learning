#!/usr/bin/env python3
"""Finite-shot verification of the binary two-fragment EIQL theorem.

The learner sees only same-event randomized single-qubit Pauli-shadow snapshots.
For each physical event a balanced hidden record X in {0,1} prepares two
conditionally independent qubit records with random local orientations and the
same Bloch contrast c. Consecutive physical events are paired exactly as in the
finite-shot estimator in the manuscript.

Besides the conservative explicit theorem bound, this benchmark estimates the
empirical scaling exponent and the contrast-rescaled quantity c^2 sqrt(N) err.
For a signal singular value proportional to c^2, N^{-1/2} estimation predicts an
approximately constant rescaled error.
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 20260815
BETA = 0.10
CONTRASTS = [0.50, 0.75, 1.00]
N_PAIRS_GRID = [512, 2048, 8192, 32768, 131072]
WORLDS = 30
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

SQRT2 = math.sqrt(2.0)
B_SHADOW = math.sqrt(5.0)


def random_unit(rng):
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)


def shadow_coefficients(contrast, direction, hidden_x, rng):
    n = len(hidden_x)
    axes = rng.integers(0, 3, size=n)
    branch_sign = 2 * hidden_x - 1
    means = branch_sign * contrast * direction[axes]
    outcomes = np.where(rng.random(n) < (1.0 + means) / 2.0, 1.0, -1.0)

    coeff = np.zeros((n, 4), dtype=float)
    coeff[:, 0] = 1.0 / SQRT2
    coeff[np.arange(n), axes + 1] = 3.0 * outcomes / SQRT2
    return coeff


def estimate_connected_operator(contrast, n_pairs, rng):
    dir_i = random_unit(rng)
    dir_j = random_unit(rng)
    hidden_x = rng.integers(0, 2, size=2 * n_pairs)

    ri = shadow_coefficients(contrast, dir_i, hidden_x, rng)
    rj = shadow_coefficients(contrast, dir_j, hidden_x, rng)

    di = ri[0::2] - ri[1::2]
    dj = rj[0::2] - rj[1::2]
    omega_hat = 0.5 * np.einsum("ni,nj->ij", di, dj) / n_pairs

    u, s, vh = np.linalg.svd(omega_hat, full_matrices=False)
    true_i = np.r_[0.0, SQRT2 * contrast * dir_i]
    true_j = np.r_[0.0, SQRT2 * contrast * dir_j]
    true_i /= np.linalg.norm(true_i)
    true_j /= np.linalg.norm(true_j)

    sin_i = math.sqrt(max(0.0, 1.0 - abs(float(u[:, 0] @ true_i)) ** 2))
    sin_j = math.sqrt(max(0.0, 1.0 - abs(float(vh[0] @ true_j)) ** 2))
    return 0.5 * (sin_i + sin_j), float(s[0])


def theorem_quantities(contrast, n_pairs):
    lam = 0.5 * contrast**2
    e_n = (2.0 * B_SHADOW**2 / math.sqrt(n_pairs)) * (
        1.0 + math.sqrt(2.0 * math.log(1.0 / BETA))
    )
    existence_condition = bool(e_n < lam)
    bound = e_n / (lam - e_n) if existence_condition else math.nan
    informative_bound = bool(existence_condition and bound < 1.0)
    return lam, e_n, bound, existence_condition, informative_bound


def linear_fit_loglog(x, y):
    lx = np.log(np.asarray(x, dtype=float))
    ly = np.log(np.asarray(y, dtype=float))
    slope, intercept = np.polyfit(lx, ly, 1)
    pred = slope * lx + intercept
    ss_res = float(np.sum((ly - pred) ** 2))
    ss_tot = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(slope), float(intercept), r2


def main():
    rows = []
    for contrast in CONTRASTS:
        for n_pairs in N_PAIRS_GRID:
            lam, e_n, bound, existence_condition, informative_bound = theorem_quantities(contrast, n_pairs)
            for world in range(WORLDS):
                seed = SEED + int(1000 * contrast) * 10_000_000 + n_pairs + world
                rng = np.random.default_rng(seed)
                sin_error, leading_sv = estimate_connected_operator(contrast, n_pairs, rng)
                rows.append({
                    "contrast_c": contrast,
                    "n_pairs": n_pairs,
                    "physical_events": 2 * n_pairs,
                    "world": world,
                    "sin_angle_error": sin_error,
                    "rescaled_error_c2_sqrtN": contrast**2 * math.sqrt(n_pairs) * sin_error,
                    "leading_singular_value_hat": leading_sv,
                    "lambda_signal": lam,
                    "e_N_beta": e_n,
                    "theorem_bound": bound,
                    "theorem_existence_condition_e_lt_lambda": existence_condition,
                    "theorem_bound_informative_lt_one": informative_bound,
                    "beta": BETA,
                })

    runs = pd.DataFrame(rows)
    summary = runs.groupby(["contrast_c", "n_pairs", "physical_events"], as_index=False).agg(
        median_sin_error=("sin_angle_error", "median"),
        q90_sin_error=("sin_angle_error", lambda x: float(np.quantile(x, 0.90))),
        median_rescaled_error=("rescaled_error_c2_sqrtN", "median"),
        q90_rescaled_error=("rescaled_error_c2_sqrtN", lambda x: float(np.quantile(x, 0.90))),
        mean_sin_error=("sin_angle_error", "mean"),
        sd_sin_error=("sin_angle_error", "std"),
        mean_leading_sv=("leading_singular_value_hat", "mean"),
        lambda_signal=("lambda_signal", "first"),
        e_N_beta=("e_N_beta", "first"),
        theorem_bound=("theorem_bound", "first"),
        theorem_existence_condition_e_lt_lambda=("theorem_existence_condition_e_lt_lambda", "first"),
        theorem_bound_informative_lt_one=("theorem_bound_informative_lt_one", "first"),
    )

    fit_rows = []
    for contrast in CONTRASTS:
        sub = summary[summary.contrast_c == contrast].sort_values("n_pairs")
        slope, intercept, r2 = linear_fit_loglog(sub.n_pairs, sub.median_sin_error)
        fit_rows.append({
            "contrast_c": contrast,
            "loglog_slope_vs_N_pairs": slope,
            "expected_slope": -0.5,
            "loglog_intercept": intercept,
            "r_squared": r2,
            "mean_median_rescaled_error_c2_sqrtN": float(sub.median_rescaled_error.mean()),
            "sd_median_rescaled_error_c2_sqrtN": float(sub.median_rescaled_error.std()),
        })
    fits = pd.DataFrame(fit_rows)

    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)
    fits.to_csv(OUT / "scaling_fits.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    ax = axes[0]
    for contrast in CONTRASTS:
        sub = summary[summary.contrast_c == contrast].sort_values("physical_events")
        ax.plot(sub.physical_events, sub.median_sin_error, marker="o", label=f"c={contrast:.2f}")
        ax.plot(sub.physical_events, sub.q90_sin_error, linestyle="--", alpha=0.65)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Physical events n = 2N")
    ax.set_ylabel("HS sin-angle error")
    ax.set_title("Finite-shot decoder recovery")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    ax = axes[1]
    for contrast in CONTRASTS:
        sub = summary[summary.contrast_c == contrast].sort_values("physical_events")
        ax.plot(sub.physical_events, sub.median_rescaled_error, marker="o", label=f"c={contrast:.2f}")
    pooled = float(summary.median_rescaled_error.mean())
    ax.axhline(pooled, linestyle=":", label=f"pooled mean {pooled:.2f}")
    ax.set_xscale("log")
    ax.set_xlabel("Physical events n = 2N")
    ax.set_ylabel(r"$c^2\sqrt{N}\,\mathrm{median}(\sin\theta)$")
    ax.set_title("Contrast-rescaled data collapse")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "finite_shot_theorem2.png", dpi=220)
    plt.close(fig)

    print(summary.to_string(index=False))
    print("\nScaling fits")
    print(fits.to_string(index=False))


if __name__ == "__main__":
    main()
