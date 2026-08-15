#!/usr/bin/env python3
"""End-to-end finite-shot virtual collision experiment for EIQL.

A six-qubit statevector (one system + five environment fragments) is generated
from |+>_S |0...0>_E by sequential controlled-Ry system-environment collision
unitaries. Each environment fragment is then conjugated by an independently
hidden local SU(2) rotation. The learner receives only finite-shot Pauli outcomes
from an orthogonal-array schedule, with symmetric readout flips, and reconstructs
local decoder axes from environment-environment connected pair moments.

The primary success criterion is deliberately strict: every recovered fragment
axis must be within 5 degrees of its oracle Helstrom direction. Mean-axis success
is retained as a secondary diagnostic.
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

I2 = np.eye(2, dtype=complex)
P1 = np.array([[0, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.array([[1, 0], [0, -1]], complex)
PAULI = np.array([X, Y, Z])


def random_su2(rng):
    mat = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    q, r = np.linalg.qr(mat)
    d = np.diag(r)
    d = d / np.abs(d)
    q = q @ np.diag(np.conj(d))
    return q / np.sqrt(np.linalg.det(q))


def ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def kron_all(ops):
    out = np.array([[1.0 + 0.0j]])
    for op in ops:
        out = np.kron(out, op)
    return out


def controlled_single_qubit_unitary(control, target, unitary, n_qubits):
    """I + |1><1|_control tensor (U-I)_target on an n-qubit register."""
    ops = []
    for q in range(n_qubits):
        if q == control:
            ops.append(P1)
        elif q == target:
            ops.append(unitary - I2)
        else:
            ops.append(I2)
    return np.eye(2**n_qubits, dtype=complex) + kron_all(ops)


def apply_single_qubit_state(state, unitary, target, n_qubits):
    tensor = state.reshape([2] * n_qubits)
    moved = np.moveaxis(tensor, target, 0).reshape(2, -1)
    moved = unitary @ moved
    rebuilt = moved.reshape([2] + [2] * (n_qubits - 1))
    return np.moveaxis(rebuilt, 0, target).reshape(-1)


def collision_state(theta_deg):
    """Generate the global S-E state by explicit sequential controlled collisions."""
    n_qubits = M + 1
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    zero = np.array([1, 0], dtype=complex)
    state = plus
    for _ in range(M):
        state = np.kron(state, zero)

    u = ry(np.deg2rad(theta_deg))
    for target in range(1, M + 1):
        cu = controlled_single_qubit_unitary(0, target, u, n_qubits)
        state = cu @ state
    return state / np.linalg.norm(state)


def hide_environment_bases(state, rng):
    n_qubits = M + 1
    hidden = []
    out = state.copy()
    for target in range(1, M + 1):
        u = random_su2(rng)
        hidden.append(u)
        out = apply_single_qubit_state(out, u, target, n_qubits)
    return out, hidden


def conditional_local_records(global_state):
    """Extract local conditional states from the explicit global state."""
    tensor = global_state.reshape([2] * (M + 1))
    records = np.zeros((M, 2, 3), dtype=float)
    oracle = np.zeros((M, 3), dtype=float)

    for x in (0, 1):
        branch = tensor[x].reshape(-1)
        branch /= np.linalg.norm(branch)
        branch_tensor = branch.reshape([2] * M)
        for j in range(M):
            moved = np.moveaxis(branch_tensor, j, 0).reshape(2, -1)
            rho = moved @ moved.conj().T
            records[j, x] = [float(np.real(np.trace(p @ rho))) for p in PAULI]

    for j in range(M):
        delta = records[j, 1] - records[j, 0]
        oracle[j] = delta / np.linalg.norm(delta)
    return records, oracle


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
    base_states = {theta: collision_state(theta) for theta in THETA_GRID}
    rows = []

    for theta in THETA_GRID:
        distinguishability = float(np.sin(np.deg2rad(theta) / 2))
        for shots in SHOTS_PER_SETTING:
            for world in range(WORLDS):
                rng = np.random.default_rng(SEED + theta * 100000 + shots * 100 + world)
                hidden_state, _ = hide_environment_bases(base_states[theta], rng)
                records, oracle = conditional_local_records(hidden_state)
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
                    "success_all_fragments_le_5deg": bool(errs.max() <= SUCCESS_DEG),
                    "readout_flip_probability": READOUT_Q,
                    "explicit_global_statevector_dynamics": True,
                })

    runs = pd.DataFrame(rows)
    summary = runs.groupby([
        "theta_deg", "local_trace_distinguishability_D", "shots_per_setting", "total_physical_events"
    ], as_index=False).agg(
        strict_all_fragment_success_rate=("success_all_fragments_le_5deg", "mean"),
        mean_error_success_rate=("success_mean_error_le_5deg", "mean"),
        median_mean_axis_error_deg=("mean_axis_error_deg", "median"),
        q90_mean_axis_error_deg=("mean_axis_error_deg", lambda x: float(np.quantile(x, 0.90))),
        median_max_axis_error_deg=("max_axis_error_deg", "median"),
        q90_max_axis_error_deg=("max_axis_error_deg", lambda x: float(np.quantile(x, 0.90))),
    )
    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    pivot = summary.pivot(
        index="local_trace_distinguishability_D",
        columns="shots_per_setting",
        values="strict_all_fragment_success_rate",
    )
    fig, ax = plt.subplots(figsize=(7.5, 4.9))
    image = ax.imshow(pivot.values, origin="lower", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)), [str(x) for x in pivot.columns])
    ylabels = []
    for d in pivot.index:
        theta = summary.loc[np.isclose(summary.local_trace_distinguishability_D, d), "theta_deg"].iloc[0]
        ylabels.append(f"{d:.3f} ({theta:g}°)")
    ax.set_yticks(range(len(pivot.index)), ylabels)
    ax.set_xlabel("Shots per OA Pauli setting")
    ax.set_ylabel("Local trace distinguishability D (collision angle)")
    ax.set_title(f"Explicit collision dynamics: P(max axis error <= {SUCCESS_DEG:g}°), readout q={READOUT_Q}")
    for iy in range(len(pivot.index)):
        for ix in range(len(pivot.columns)):
            ax.text(ix, iy, f"{pivot.values[iy, ix]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="All-fragment recovery probability")
    fig.tight_layout()
    fig.savefig(OUT / "collision_recovery_phase_diagram.png", dpi=220)
    plt.close(fig)

    print(f"Orthogonal-array settings for M={M}: {len(schedule)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
