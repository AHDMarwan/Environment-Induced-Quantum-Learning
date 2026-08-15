#!/usr/bin/env python3
"""End-to-end finite-shot virtual collision experiment for EIQL.

A system pointer bit controls identical single-qubit collision rotations on m
independent environment ancillas. Each fragment is then hidden behind an
independent unknown SU(2) basis. The learner receives only finite-shot Pauli
measurement outcomes from an orthogonal-array schedule, with symmetric readout
flips. Decoder axes are reconstructed from environment-environment connected
pair moments.
"""

from pathlib import Path
from itertools import product, combinations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SEED = 20260815
M = 5
THETA_GRID = [20, 40, 60, 90, 120, 180]
SHOTS_PER_SETTING = [32, 64, 128, 256, 512]
WORLDS = 35
READOUT_Q = 0.02
SUCCESS_DEG = 5.0
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
PAULI = np.array([X, Y, Z])


def random_su2(rng):
    m = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    q, r = np.linalg.qr(m)
    d = np.diag(r)
    d = d / np.abs(d)
    q = q @ np.diag(np.conj(d))
    return q / np.sqrt(np.linalg.det(q))


def bloch(psi):
    return np.array([np.real(np.vdot(psi, p @ psi)) for p in PAULI])


def make_collision_records(theta_deg, rng):
    t = np.deg2rad(theta_deg)
    e0 = np.array([1, 0], complex)
    e1 = np.array([np.cos(t / 2), np.sin(t / 2)], complex)
    records = []
    oracle = []
    for _ in range(M):
        u = random_su2(rng)
        r0, r1 = bloch(u @ e0), bloch(u @ e1)
        records.append([r0, r1])
        d = r1 - r0
        oracle.append(d / np.linalg.norm(d))
    return np.asarray(records), np.asarray(oracle)


def oa_schedule(m):
    q = 3
    for k in range(1, 6):
        if (q**k - 1) // (q - 1) >= m:
            break
    reps = []
    for v in product(range(3), repeat=k):
        if all(x == 0 for x in v):
            continue
        first = next(x for x in v if x != 0)
        inv = 1 if first == 1 else 2
        vn = tuple((x * inv) % 3 for x in v)
        if vn not in reps:
            reps.append(vn)
    reps = reps[:m]
    rows = []
    for t in product(range(3), repeat=k):
        rows.append([sum(t[a] * v[a] for a in range(k)) % 3 for v in reps])
    return np.asarray(rows, dtype=int)


def sample_counts(records, shots, rng):
    schedule = oa_schedule(M)
    data = []
    for row in schedule:
        x = rng.integers(0, 2, size=shots)
        out = np.empty((shots, M), dtype=np.int8)
        for j, axis in enumerate(row):
            r = records[j, x, :]
            p_plus = (1 + r[:, axis]) / 2
            s = np.where(rng.random(shots) < p_plus, 1, -1)
            if READOUT_Q:
                s[rng.random(shots) < READOUT_Q] *= -1
            out[:, j] = s
        data.append(out)
    return schedule, data


def estimate_axes(schedule, data):
    means = np.zeros((M, 3))
    for j in range(M):
        for a in range(3):
            vals = [data[r][:, j] for r, row in enumerate(schedule) if row[j] == a]
            means[j, a] = np.concatenate(vals).mean()

    corr = {}
    for i, j in combinations(range(M), 2):
        mat = np.zeros((3, 3))
        for a in range(3):
            for b in range(3):
                vals = [
                    data[r][:, i] * data[r][:, j]
                    for r, row in enumerate(schedule)
                    if row[i] == a and row[j] == b
                ]
                mat[a, b] = np.concatenate(vals).mean()
        corr[(i, j)] = mat - np.outer(means[i], means[j])

    axes = []
    for i in range(M):
        gram = np.zeros((3, 3))
        for j in range(M):
            if i == j:
                continue
            cij = corr[(i, j)] if i < j else corr[(j, i)].T
            gram += cij @ cij.T
        _, vecs = np.linalg.eigh(gram)
        axes.append(vecs[:, -1])
    return np.asarray(axes)


def axis_errors_deg(axes, oracle):
    dots = np.abs(np.sum(axes * oracle, axis=1))
    return np.degrees(np.arccos(np.clip(dots, -1, 1)))


def main():
    schedule = oa_schedule(M)
    rows = []
    for theta in THETA_GRID:
        distinguishability = float(np.sin(np.deg2rad(theta) / 2))
        for shots in SHOTS_PER_SETTING:
            for world in range(WORLDS):
                rng = np.random.default_rng(SEED + theta * 100000 + shots * 100 + world)
                records, oracle = make_collision_records(theta, rng)
                sched, data = sample_counts(records, shots, rng)
                axes = estimate_axes(sched, data)
                errs = axis_errors_deg(axes, oracle)
                rows.append({
                    "theta_deg": theta,
                    "local_trace_distinguishability_D": distinguishability,
                    "shots_per_setting": shots,
                    "distinct_settings": len(schedule),
                    "total_physical_events": len(schedule) * shots,
                    "world": world,
                    "mean_axis_error_deg": float(errs.mean()),
                    "max_axis_error_deg": float(errs.max()),
                    "success_mean_error_le_5deg": bool(errs.mean() <= SUCCESS_DEG),
                    "readout_flip_probability": READOUT_Q,
                })

    runs = pd.DataFrame(rows)
    summary = runs.groupby([
        "theta_deg", "local_trace_distinguishability_D", "shots_per_setting", "total_physical_events"
    ], as_index=False).agg(
        success_rate=("success_mean_error_le_5deg", "mean"),
        median_mean_axis_error_deg=("mean_axis_error_deg", "median"),
        q90_mean_axis_error_deg=("mean_axis_error_deg", lambda x: float(np.quantile(x, 0.90))),
        median_max_axis_error_deg=("max_axis_error_deg", "median"),
    )
    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    pivot = summary.pivot(index="theta_deg", columns="shots_per_setting", values="success_rate")
    fig, ax = plt.subplots(figsize=(7.3, 4.8))
    image = ax.imshow(pivot.values, origin="lower", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), [str(x) for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), [str(x) for x in pivot.index])
    ax.set_xlabel("Shots per OA Pauli setting")
    ax.set_ylabel("Collision angle theta [deg]")
    ax.set_title(f"Virtual collision experiment: P(mean axis error <= {SUCCESS_DEG:g} deg), q={READOUT_Q}")
    for iy in range(len(pivot.index)):
        for ix in range(len(pivot.columns)):
            ax.text(ix, iy, f"{pivot.values[iy, ix]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="Recovery success probability")
    fig.tight_layout()
    fig.savefig(OUT / "collision_recovery_phase_diagram.png", dpi=220)
    plt.close(fig)

    print(f"Orthogonal-array settings for M={M}: {len(schedule)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
