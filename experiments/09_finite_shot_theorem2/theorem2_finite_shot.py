#!/usr/bin/env python3
"""Finite-shot verification of the binary two-fragment EIQL theorem.

The learner sees only same-event randomized single-qubit Pauli-shadow snapshots.
For each physical event a balanced hidden record X in {0,1} prepares two
conditionally independent qubit records with random local orientations and the
same Bloch contrast c. Consecutive physical events are paired exactly as in the
finite-shot estimator in the manuscript.

Outputs:
  outputs/runs.csv
  outputs/summary.csv
  outputs/finite_shot_theorem2.png

The theorem bound is intentionally plotted even when conservative. Regions in
which e_N >= lambda are marked as non-vacuous = False rather than clipped into
a misleading numerical guarantee.
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
    """Return normalized Pauli-basis coefficients of qubit shadow snapshots."""
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
    if e_n < lam:
        bound = e_n / (lam - e_n)
        nonvacuous = True
    else:
        bound = math.nan
        nonvacuous = False
    return lam, e_n, bound, nonvacuous


def main():
    rows = []
    for contrast in CONTRASTS:
        for n_pairs in N_PAIRS_GRID:
            lam, e_n, bound, nonvacuous = theorem_quantities(contrast, n_pairs)
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
                    "leading_singular_value_hat": leading_sv,
                    "lambda_signal": lam,
                    "e_N_beta": e_n,
                    "theorem_bound": bound,
                    "bound_nonvacuous": nonvacuous,
                    "beta": BETA,
                })

    runs = pd.DataFrame(rows)
    summary = runs.groupby(["contrast_c", "n_pairs", "physical_events"], as_index=False).agg(
        median_sin_error=("sin_angle_error", "median"),
        q90_sin_error=("sin_angle_error", lambda x: float(np.quantile(x, 0.90))),
        mean_sin_error=("sin_angle_error", "mean"),
        sd_sin_error=("sin_angle_error", "std"),
        mean_leading_sv=("leading_singular_value_hat", "mean"),
        lambda_signal=("lambda_signal", "first"),
        e_N_beta=("e_N_beta", "first"),
        theorem_bound=("theorem_bound", "first"),
        bound_nonvacuous=("bound_nonvacuous", "first"),
    )

    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    for contrast in CONTRASTS:
        sub = summary[summary.contrast_c == contrast].sort_values("physical_events")
        ax.plot(sub.physical_events, sub.median_sin_error, marker="o", label=f"c={contrast:.2f}: median")
        ax.plot(sub.physical_events, sub.q90_sin_error, marker=".", linestyle="--", label=f"c={contrast:.2f}: 90%")
        valid = sub[sub.bound_nonvacuous]
        if len(valid):
            ax.plot(valid.physical_events, np.minimum(valid.theorem_bound, 1.5), linestyle=":", marker="x",
                    label=f"c={contrast:.2f}: theorem bound")
    ax.set_xscale("log")
    ax.set_xlabel("Physical events n = 2N")
    ax.set_ylabel("Hilbert-Schmidt sin-angle error")
    ax.set_ylim(0, 1.05)
    ax.set_title("Finite-shot two-fragment decoder recovery")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "finite_shot_theorem2.png", dpi=220)
    plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
