#!/usr/bin/env python3
"""Stress test for residual conditional inter-fragment correlations.

We start from equal-prior binary product records with Bloch contrast c along Z
and add a traceless correlation term gamma X tensor Z / 4 to each conditional
state. The perturbation preserves both local conditional marginals but violates
conditional independence, giving a controlled model-mismatch axis for the
robust binary decoder theorem.
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 20260815
CONTRAST = 0.65
GAMMAS = np.round(np.arange(0.0, 0.211, 0.03), 2)
N_PAIRS = 8192
WORLDS = 30
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = [X, Y, Z]
BASIS = [I / math.sqrt(2), X / math.sqrt(2), Y / math.sqrt(2), Z / math.sqrt(2)]


def partial_trace_two_qubits(rho, keep):
    r = rho.reshape(2, 2, 2, 2)
    if keep == 0:
        return np.einsum("abcb->ac", r)
    return np.einsum("abad->bd", r)


def entropy_bits(rho):
    vals = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    vals = vals[vals > 1e-14]
    return float(-np.sum(vals * np.log2(vals)))


def mutual_information_bits(rho):
    return (
        entropy_bits(partial_trace_two_qubits(rho, 0))
        + entropy_bits(partial_trace_two_qubits(rho, 1))
        - entropy_bits(rho)
    )


def conditional_state(x, gamma):
    s = 1.0 if x == 1 else -1.0
    ri = (I + s * CONTRAST * Z) / 2
    rj = (I + s * CONTRAST * Z) / 2
    rho = np.kron(ri, rj) + (gamma / 4.0) * np.kron(X, Z)
    min_eval = float(np.linalg.eigvalsh((rho + rho.conj().T) / 2).min())
    if min_eval < -1e-10:
        raise ValueError(f"gamma={gamma} is not positive semidefinite; min eigenvalue={min_eval}")
    return rho


def operator_coeff_matrix(op):
    out = np.zeros((4, 4), dtype=float)
    for a, aa in enumerate(BASIS):
        for b, bb in enumerate(BASIS):
            out[a, b] = float(np.real(np.trace(np.kron(aa, bb).conj().T @ op)))
    return out


def population_quantities(gamma):
    rhos = [conditional_state(0, gamma), conditional_state(1, gamma)]
    avg = 0.5 * (rhos[0] + rhos[1])
    ri_bar = 0.5 * (partial_trace_two_qubits(rhos[0], 0) + partial_trace_two_qubits(rhos[1], 0))
    rj_bar = 0.5 * (partial_trace_two_qubits(rhos[0], 1) + partial_trace_two_qubits(rhos[1], 1))
    omega = avg - np.kron(ri_bar, rj_bar)

    mat = operator_coeff_matrix(omega)
    u, s, _ = np.linalg.svd(mat, full_matrices=False)
    delta_i = partial_trace_two_qubits(rhos[1], 0) - partial_trace_two_qubits(rhos[0], 0)
    true = np.array([np.real(np.trace(b.conj().T @ delta_i)) for b in BASIS], dtype=float)
    true /= np.linalg.norm(true)
    pop_sin = math.sqrt(max(0.0, 1.0 - abs(float(u[:, 0] @ true)) ** 2))

    nu = max(0.0, 0.5 * (mutual_information_bits(rhos[0]) + mutual_information_bits(rhos[1])))
    delta_norm = float(np.linalg.norm(delta_i, "fro"))
    lam = 0.25 * delta_norm**2
    eta = math.sqrt(2.0 * math.log(2.0) * nu)
    bound = eta / (lam - eta) if eta < lam else math.nan
    return rhos, nu, lam, eta, bound, pop_sin, float(s[0])


def expectation_tables(rhos):
    local_i = np.zeros((2, 3))
    local_j = np.zeros((2, 3))
    corr = np.zeros((2, 3, 3))
    for x in (0, 1):
        ri = partial_trace_two_qubits(rhos[x], 0)
        rj = partial_trace_two_qubits(rhos[x], 1)
        for a in range(3):
            local_i[x, a] = np.real(np.trace(PAULI[a] @ ri))
            local_j[x, a] = np.real(np.trace(PAULI[a] @ rj))
            for b in range(3):
                corr[x, a, b] = np.real(np.trace(np.kron(PAULI[a], PAULI[b]) @ rhos[x]))
    return local_i, local_j, corr


def paired_shadow_estimate(rhos, rng):
    local_i, local_j, corr = expectation_tables(rhos)
    n_events = 2 * N_PAIRS
    hidden = rng.integers(0, 2, size=n_events)
    ai = rng.integers(0, 3, size=n_events)
    aj = rng.integers(0, 3, size=n_events)

    mi = local_i[hidden, ai]
    mj = local_j[hidden, aj]
    cij = corr[hidden, ai, aj]
    p_pp = (1 + mi + mj + cij) / 4
    p_pm = (1 + mi - mj - cij) / 4
    p_mp = (1 - mi + mj - cij) / 4
    u = rng.random(n_events)

    si = np.empty(n_events, dtype=float)
    sj = np.empty(n_events, dtype=float)
    cut1 = p_pp
    cut2 = p_pp + p_pm
    cut3 = p_pp + p_pm + p_mp
    mask1 = u < cut1
    mask2 = (u >= cut1) & (u < cut2)
    mask3 = (u >= cut2) & (u < cut3)
    mask4 = u >= cut3
    si[mask1], sj[mask1] = 1, 1
    si[mask2], sj[mask2] = 1, -1
    si[mask3], sj[mask3] = -1, 1
    si[mask4], sj[mask4] = -1, -1

    ci = np.zeros((n_events, 4), dtype=float)
    cj = np.zeros((n_events, 4), dtype=float)
    ci[:, 0] = 1 / math.sqrt(2)
    cj[:, 0] = 1 / math.sqrt(2)
    ci[np.arange(n_events), ai + 1] = 3 * si / math.sqrt(2)
    cj[np.arange(n_events), aj + 1] = 3 * sj / math.sqrt(2)

    di = ci[0::2] - ci[1::2]
    dj = cj[0::2] - cj[1::2]
    omega_hat = 0.5 * np.einsum("ni,nj->ij", di, dj) / N_PAIRS
    uhat, _, _ = np.linalg.svd(omega_hat, full_matrices=False)
    true = np.array([0.0, 0.0, 0.0, 1.0])
    return math.sqrt(max(0.0, 1.0 - abs(float(uhat[:, 0] @ true)) ** 2))


def main():
    pop_rows = []
    shot_rows = []
    for gamma in GAMMAS:
        rhos, nu, lam, eta, bound, pop_sin, leading_sv = population_quantities(float(gamma))
        pop_rows.append({
            "gamma": gamma,
            "conditional_mutual_information_bits": nu,
            "lambda_signal": lam,
            "eta_pinsker": eta,
            "robust_bound": bound,
            "bound_nonvacuous": bool(eta < lam),
            "population_sin_angle": pop_sin,
            "population_leading_singular_value": leading_sv,
        })
        for world in range(WORLDS):
            rng = np.random.default_rng(SEED + int(round(gamma * 1000)) * 10000 + world)
            shot_rows.append({
                "gamma": gamma,
                "world": world,
                "n_pairs": N_PAIRS,
                "physical_events": 2 * N_PAIRS,
                "finite_shot_sin_angle": paired_shadow_estimate(rhos, rng),
            })

    pop = pd.DataFrame(pop_rows)
    shots = pd.DataFrame(shot_rows)
    finite = shots.groupby("gamma", as_index=False).agg(
        finite_median_sin_angle=("finite_shot_sin_angle", "median"),
        finite_q90_sin_angle=("finite_shot_sin_angle", lambda x: float(np.quantile(x, 0.90))),
        finite_mean_sin_angle=("finite_shot_sin_angle", "mean"),
    )
    summary = pop.merge(finite, on="gamma", how="left")

    pop.to_csv(OUT / "population.csv", index=False)
    shots.to_csv(OUT / "finite_shot_runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.plot(summary.conditional_mutual_information_bits, summary.population_sin_angle,
            marker="o", label="population direction error")
    ax.plot(summary.conditional_mutual_information_bits, summary.finite_median_sin_angle,
            marker="s", label=f"finite-shot median (2N={2*N_PAIRS})")
    ax.plot(summary.conditional_mutual_information_bits, summary.finite_q90_sin_angle,
            linestyle="--", marker=".", label="finite-shot 90% quantile")
    valid = summary[summary.bound_nonvacuous]
    if len(valid):
        ax.plot(valid.conditional_mutual_information_bits, np.minimum(valid.robust_bound, 1.5),
                linestyle=":", marker="x", label="Pinsker/Wedin bound")
    ax.set_xlabel(r"Conditional mutual information $I(E_i:E_j|X)$ [bits]")
    ax.set_ylabel("Hilbert-Schmidt sin-angle error")
    ax.set_ylim(0, 1.05)
    ax.set_title("Controlled violation of conditional independence")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "conditional_correlation_stress.png", dpi=220)
    plt.close(fig)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
