#!/usr/bin/env python3
"""Correlated-nuisance failure benchmark for EIQL.

The environment carries two balanced common variables on each fragment:
  * X: the system pointer bit, recorded with independent bit-flip probability p;
  * N: a nuisance bit, redundantly copied perfectly but independent of X.

Two local decoder families are available: read the X-record qubit or read the
N-record qubit. Both have one bit of marginal entropy. The nuisance decoder has
zero cross-fragment disagreement, so the EIQL lexicographic tie-break selects it
even though I(X;Z)=0. This deliberately violates the single-latent SBS premise
and demonstrates why agreement + richness alone is not an SBS witness.
"""

import math
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 20260814
M = 4
P = 0.03
N_SHOTS = 600
TRIALS = 1000
RICH_TOL = 0.03
EPS = 0.10

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def h2(x):
    if x <= 0 or x >= 1:
        return 0.0
    return -x * math.log2(x) - (1 - x) * math.log2(1 - x)


def entropy_binary(bits):
    return h2(float(bits.mean()))


def worst_pair_disagreement(z):
    vals = []
    for i in range(z.shape[1]):
        for j in range(i + 1, z.shape[1]):
            vals.append(np.mean(z[:, i] != z[:, j]))
    return float(max(vals))


def mutual_info_binary(x, z):
    joint = np.zeros((2, 2), float)
    for a, b in zip(x, z):
        joint[int(a), int(b)] += 1
    joint /= joint.sum()
    px = joint.sum(axis=1)
    pz = joint.sum(axis=0)
    mi = 0.0
    for a in range(2):
        for b in range(2):
            if joint[a, b] > 0:
                mi += joint[a, b] * math.log2(joint[a, b] / (px[a] * pz[b]))
    return mi


def population_summary():
    d_pointer = 2 * P * (1 - P)
    return pd.DataFrame([
        {
            "decoder": "pointer-record",
            "population_R_bits": 1.0,
            "population_D": d_pointer,
            "population_I_XZ_bits": 1 - h2(P),
            "physical_meaning": "system pointer",
        },
        {
            "decoder": "nuisance-record",
            "population_R_bits": 1.0,
            "population_D": 0.0,
            "population_I_XZ_bits": 0.0,
            "physical_meaning": "shared nuisance independent of S",
        },
    ])


def run_finite_shot():
    rng = np.random.default_rng(SEED)
    rows = []
    for t in range(TRIALS):
        x = rng.integers(0, 2, N_SHOTS)
        nuisance = rng.integers(0, 2, N_SHOTS)
        flips = rng.random((N_SHOTS, M)) < P
        zx = np.bitwise_xor(x[:, None], flips.astype(np.int8))
        zn = np.tile(nuisance[:, None], (1, M))

        stats = []
        for name, z in [("pointer-record", zx), ("nuisance-record", zn)]:
            R = min(entropy_binary(z[:, j]) for j in range(M))
            D = worst_pair_disagreement(z)
            I = np.mean([mutual_info_binary(x, z[:, j]) for j in range(M)])
            stats.append((name, R, D, I))

        feasible = [s for s in stats if s[2] <= EPS]
        rstar = max(s[1] for s in feasible)
        near = [s for s in feasible if s[1] >= rstar - RICH_TOL]
        selected = min(near, key=lambda s: s[2])
        rows.append({
            "trial": t,
            "selected": selected[0],
            "selected_R": selected[1],
            "selected_D": selected[2],
            "selected_I_XZ": selected[3],
            "pointer_R": stats[0][1],
            "pointer_D": stats[0][2],
            "pointer_I_XZ": stats[0][3],
            "nuisance_R": stats[1][1],
            "nuisance_D": stats[1][2],
            "nuisance_I_XZ": stats[1][3],
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    pop = population_summary()
    runs = run_finite_shot()
    summary = pd.DataFrame([{
        "m_fragments": M,
        "pointer_flip_p": P,
        "shots_per_candidate": N_SHOTS,
        "trials": TRIALS,
        "epsilon": EPS,
        "richness_tolerance_bits": RICH_TOL,
        "nuisance_selected_fraction": float(np.mean(runs.selected == "nuisance-record")),
        "mean_selected_D": runs.selected_D.mean(),
        "mean_selected_I_XZ_bits": runs.selected_I_XZ.mean(),
        "mean_pointer_D": runs.pointer_D.mean(),
        "mean_pointer_I_XZ_bits": runs.pointer_I_XZ.mean(),
    }])
    pop.to_csv(OUT / "population.csv", index=False)
    runs.to_csv(OUT / "finite_shot_runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)
    print(pop.to_string(index=False))
    print("\nFinite-shot summary")
    print(summary.to_string(index=False))
