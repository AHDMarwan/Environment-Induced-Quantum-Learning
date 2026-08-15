#!/usr/bin/env python3
"""Finite-shot multiclass benchmark: two-view ambiguity versus three-view recovery.

The two-view distribution is the exact three-class commuting counterexample from
Appendix B of the manuscript. It admits two distinct latent decompositions with
different Bayes/MAP decoders on view A. A generic third stochastic view C is
then appended to the first decomposition. From finite samples of (A,B,C), a
spectral three-view method reconstructs the latent factors up to a common
permutation.

Important methodological point: the recovery routine never uses the true latent
matrix A. Oracle permutation matching is isolated in align_for_evaluation() and
is used only to compute errors/success rates, exactly matching identifiability
up to a common latent-label permutation.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

SEED = 20260815
SHOTS_GRID = [1000, 3000, 10000, 30000, 100000]
WORLDS = 80
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

p = np.array([3/10, 3/10, 2/5], dtype=float)
A = np.array([
    [3/5, 1/5, 1/5],
    [3/10, 3/5, 1/5],
    [1/10, 1/5, 3/5],
], dtype=float)
B = np.array([
    [1/2, 1/5, 3/10],
    [3/10, 1/2, 1/5],
    [1/5, 3/10, 1/2],
], dtype=float)

p_alt = np.array([39/200, 81/200, 2/5], dtype=float)
A_alt = np.array([
    [3/5, 41/135, 1/5],
    [3/10, 47/90, 1/5],
    [1/10, 47/270, 3/5],
], dtype=float)
B_alt = np.array([
    [43/65, 1/5, 3/10],
    [5/26, 1/2, 1/5],
    [19/130, 3/10, 1/2],
], dtype=float)

C = np.array([
    [0.70, 0.20, 0.10],
    [0.20, 0.60, 0.20],
    [0.10, 0.20, 0.70],
], dtype=float)
W = np.array([0.20, -0.70, 1.10], dtype=float)


def map_decoder(weights, response):
    return np.argmax(response * weights[None, :], axis=1)


def exact_two_view_distribution(weights, left, right):
    return left @ np.diag(weights) @ right.T


def sample_three_view(n, rng):
    latent = rng.choice(3, size=n, p=p)
    a = np.empty(n, dtype=np.int8)
    b = np.empty(n, dtype=np.int8)
    c = np.empty(n, dtype=np.int8)
    for x in range(3):
        idx = np.where(latent == x)[0]
        if not len(idx):
            continue
        a[idx] = rng.choice(3, size=len(idx), p=A[:, x])
        b[idx] = rng.choice(3, size=len(idx), p=B[:, x])
        c[idx] = rng.choice(3, size=len(idx), p=C[:, x])
    return a, b, c


def empirical_moments(a, b, c):
    n = len(a)
    pab = np.zeros((3, 3), dtype=float)
    slices = np.zeros((3, 3, 3), dtype=float)
    for y, z, w in zip(a, b, c):
        pab[y, z] += 1
        slices[w, y, z] += 1
    pab /= n
    slices /= n
    return pab, slices


def recover_three_view(pab, slices):
    """Recover unordered latent factors from observables only."""
    if np.linalg.cond(pab) > 1e7:
        raise np.linalg.LinAlgError("ill-conditioned P_AB")
    weighted = np.tensordot(W, slices, axes=(0, 0))
    obs = weighted @ np.linalg.inv(pab)
    eigvals, eigvecs = np.linalg.eig(obs)
    if np.max(np.abs(np.imag(eigvals))) > 1e-5:
        raise np.linalg.LinAlgError("unstable complex spectrum")

    rec_a = np.real(eigvecs)
    for k in range(3):
        if rec_a[:, k].sum() < 0:
            rec_a[:, k] *= -1
        rec_a[:, k] = np.clip(rec_a[:, k], 1e-8, None)
        rec_a[:, k] /= rec_a[:, k].sum()

    factor = np.linalg.solve(rec_a, pab)
    rec_p = factor.sum(axis=1)
    rec_p = np.clip(rec_p, 1e-10, None)
    rec_p /= rec_p.sum()
    return rec_p, rec_a


def align_for_evaluation(rec_p, rec_a):
    """Oracle label matching used only after recovery for benchmark scoring."""
    cost = np.zeros((3, 3))
    for recovered in range(3):
        for truth in range(3):
            cost[recovered, truth] = np.linalg.norm(rec_a[:, recovered] - A[:, truth])
    row, col = linear_sum_assignment(cost)

    order = np.empty(3, dtype=int)
    for recovered, truth in zip(row, col):
        order[truth] = recovered
    return rec_p[order], rec_a[:, order]


def main():
    P = exact_two_view_distribution(p, A, B)
    P_alt = exact_two_view_distribution(p_alt, A_alt, B_alt)
    true_decoder = map_decoder(p, A)
    alt_decoder = map_decoder(p_alt, A_alt)

    exact = pd.DataFrame([{
        "two_view_max_abs_difference": float(np.max(np.abs(P - P_alt))),
        "true_decoder": "-".join(map(str, true_decoder.tolist())),
        "alternative_decoder": "-".join(map(str, alt_decoder.tolist())),
        "decoder_outcomes_that_conflict": int(np.sum(true_decoder != alt_decoder)),
        "three_view_C_condition_number": float(np.linalg.cond(C)),
        "P_AB_condition_number": float(np.linalg.cond(P)),
        "oracle_alignment_used_only_for_evaluation": True,
    }])
    exact.to_csv(OUT / "exact_ambiguity.csv", index=False)

    rows = []
    for shots in SHOTS_GRID:
        for world in range(WORLDS):
            rng = np.random.default_rng(SEED + shots * 1000 + world)
            aa, bb, cc = sample_three_view(shots, rng)
            pab, slices = empirical_moments(aa, bb, cc)
            try:
                p_raw, a_raw = recover_three_view(pab, slices)
                p_hat, a_hat = align_for_evaluation(p_raw, a_raw)
                decoder_hat = map_decoder(p_hat, a_hat)
                success = bool(np.array_equal(decoder_hat, true_decoder))
                a_error = float(np.linalg.norm(a_hat - A))
                p_error = float(np.linalg.norm(p_hat - p, ord=1))
                failed = False
            except np.linalg.LinAlgError:
                success = False
                a_error = np.nan
                p_error = np.nan
                failed = True
            rows.append({
                "shots": shots,
                "world": world,
                "decoder_success": success,
                "spectral_failure": failed,
                "A_frobenius_error_after_label_matching": a_error,
                "p_l1_error_after_label_matching": p_error,
            })

    runs = pd.DataFrame(rows)
    summary = runs.groupby("shots", as_index=False).agg(
        decoder_success_rate=("decoder_success", "mean"),
        spectral_failure_rate=("spectral_failure", "mean"),
        median_A_error=("A_frobenius_error_after_label_matching", "median"),
        q90_A_error=("A_frobenius_error_after_label_matching", lambda x: float(np.nanquantile(x, 0.90))),
        median_p_l1_error=("p_l1_error_after_label_matching", "median"),
    )
    runs.to_csv(OUT / "finite_shot_runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.plot(summary.shots, summary.decoder_success_rate, marker="o", label="three-view decoder recovery")
    ax.axhline(1.0, linestyle=":", label="population target")
    ax.set_xscale("log")
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Three-view samples")
    ax.set_ylabel("Probability of exact MAP-decoder recovery")
    ax.set_title("A generic third view resolves an exact two-view ambiguity")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "two_vs_three_view_recovery.png", dpi=220)
    plt.close(fig)

    print(exact.to_string(index=False))
    print("\nFinite-shot three-view recovery")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
