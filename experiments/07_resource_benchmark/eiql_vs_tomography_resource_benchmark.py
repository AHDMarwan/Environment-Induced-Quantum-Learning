import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import product, combinations
from pathlib import Path

OUT = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")
SEED = 20260814

# ---------- Basic qubit utilities ----------
X = np.array([[0,1],[1,0]], complex)
Y = np.array([[0,-1j],[1j,0]], complex)
Z = np.array([[1,0],[0,-1]], complex)
PAULI = np.array([X,Y,Z])

def random_su2(rng):
    M = rng.normal(size=(2,2)) + 1j*rng.normal(size=(2,2))
    Q,R = np.linalg.qr(M)
    d = np.diag(R)
    d = d / np.abs(d)
    Q = Q @ np.diag(np.conj(d))
    return Q / np.sqrt(np.linalg.det(Q))

def bloch(psi):
    return np.array([np.real(np.vdot(psi, P @ psi)) for P in PAULI])

def random_unit(rng):
    v = rng.normal(size=3)
    return v / np.linalg.norm(v)

def make_records(theta_deg, rng):
    """
    Equal-prior binary record states.
    For each fragment:
      X=0 -> hidden local rotation of |0>
      X=1 -> hidden local rotation of cos(theta/2)|0>+sin(theta/2)|1>
    The Helstrom direction is proportional to r0-r1.
    """
    records, oracle_axes = [], []
    for th in theta_deg:
        t = np.deg2rad(th)
        e0 = np.array([1,0], complex)
        e1 = np.array([np.cos(t/2), np.sin(t/2)], complex)
        V = random_su2(rng)
        r0, r1 = bloch(V @ e0), bloch(V @ e1)
        records.append([r0, r1])
        d = r0-r1
        oracle_axes.append(d/np.linalg.norm(d))
    return np.array(records), np.array(oracle_axes)

# ---------- Orthogonal-array measurement schedule ----------
def oa_schedule(m):
    """
    Fixed environment-only Pauli measurement design over GF(3).
    Every pair of fragments sees all 9 ordered Pauli-basis pairs equally often.

    9 settings support up to 4 fragments.
    27 settings support up to 13 fragments.
    """
    q = 3
    for k in range(1,6):
        if (q**k - 1)//(q-1) >= m:
            break

    reps = []
    for v in product(range(3), repeat=k):
        if all(x == 0 for x in v):
            continue
        first = next(x for x in v if x != 0)
        inv = 1 if first == 1 else 2
        vn = tuple((x*inv) % 3 for x in v)
        if vn not in reps:
            reps.append(vn)
    reps = reps[:m]

    rows = []
    for t in product(range(3), repeat=k):
        rows.append([
            sum(t[a]*v[a] for a in range(k)) % 3
            for v in reps
        ])
    return np.array(rows, dtype=int)

# ---------- Sampling ----------
def sample_environment_only(records, shots_per_setting, rng, readout_q=0.0,
                            independent_null=False):
    m = len(records)
    sched = oa_schedule(m)
    data = []

    for row in sched:
        if independent_null:
            hidden = rng.integers(0, 2, size=(shots_per_setting, m))
        else:
            x = rng.integers(0, 2, size=shots_per_setting)
            hidden = np.tile(x[:,None], (1,m))

        out = np.empty((shots_per_setting, m), dtype=np.int8)
        for j, basis in enumerate(row):
            r = records[j, hidden[:,j], :]
            p_plus = (1 + r[:,basis]) / 2
            s = np.where(rng.random(shots_per_setting) < p_plus, 1, -1)
            if readout_q > 0:
                flip = rng.random(shots_per_setting) < readout_q
                s[flip] *= -1
            out[:,j] = s
        data.append(out)
    return sched, data

def sample_system_assisted(records, system_axis, shots_per_setting, rng,
                           readout_q=0.0):
    """
    Stronger baseline: direct access to S.
    Reconstructs each S-E_j 3x3 correlation matrix using 9 settings:
    S in X/Y/Z and every E_j in X/Y/Z.
    """
    m = len(records)
    data = {}
    for a in range(3):
        for b in range(3):
            x = rng.integers(0, 2, size=shots_per_setting)

            s_bias = (1-2*x) * system_axis[a]
            s = np.where(rng.random(shots_per_setting) < (1+s_bias)/2, 1, -1)
            if readout_q > 0:
                flip = rng.random(shots_per_setting) < readout_q
                s[flip] *= -1

            E = np.empty((shots_per_setting, m), dtype=np.int8)
            for j in range(m):
                r = records[j, x, :]
                e = np.where(rng.random(shots_per_setting) < (1+r[:,b])/2, 1, -1)
                if readout_q > 0:
                    flip = rng.random(shots_per_setting) < readout_q
                    e[flip] *= -1
                E[:,j] = e
            data[(a,b)] = (s,E)
    return data

# ---------- EIQL moment decoder ----------
def estimate_eiql_axes(schedule, data, m):
    # Local means
    mu = np.zeros((m,3))
    for j in range(m):
        for a in range(3):
            vals = [data[r][:,j] for r,row in enumerate(schedule) if row[j] == a]
            mu[j,a] = np.concatenate(vals).mean()

    # Centered pair-correlation matrices
    C = {}
    for i,j in combinations(range(m),2):
        M = np.zeros((3,3))
        for a in range(3):
            for b in range(3):
                vals = [
                    data[r][:,i] * data[r][:,j]
                    for r,row in enumerate(schedule)
                    if row[i] == a and row[j] == b
                ]
                M[a,b] = np.concatenate(vals).mean()
        C[(i,j)] = M - np.outer(mu[i], mu[j])

    # Each local decoder direction is the leading eigendirection of
    # redundancy accumulated over all other fragments.
    axes = []
    for i in range(m):
        A = np.zeros((3,3))
        for j in range(m):
            if i == j:
                continue
            Cij = C[(i,j)] if i < j else C[(j,i)].T
            A += Cij @ Cij.T
        vals, vecs = np.linalg.eigh(A)
        axes.append(vecs[:,-1])
    axes = np.array(axes)

    # Free output relabeling: synchronize signs through fragment 0.
    for j in range(1,m):
        if axes[0] @ C[(0,j)] @ axes[j] < 0:
            axes[j] *= -1

    signal = np.mean([
        np.linalg.svd(M, compute_uv=False)[0] for M in C.values()
    ])
    return axes, signal

def estimate_system_assisted_axes(data, m):
    axes = []
    for j in range(m):
        C = np.zeros((3,3))
        for a in range(3):
            for b in range(3):
                s,E = data[(a,b)]
                C[a,b] = np.mean(s*E[:,j]) - np.mean(s)*np.mean(E[:,j])
        _,_,vh = np.linalg.svd(C)
        axes.append(vh[0])
    return np.array(axes)

# ---------- Evaluation ----------
def axis_errors_deg(axes, oracle_axes):
    dots = np.abs(np.sum(axes*oracle_axes, axis=1))
    return np.degrees(np.arccos(np.clip(dots,-1,1)))

def worst_disagreement(axes, records, readout_q=0.0):
    m = len(records)

    # Evaluation-only label alignment to the hidden branch convention.
    biases = np.array([
        axes[j] @ (records[j,0]-records[j,1]) / 2 for j in range(m)
    ])
    aligned = axes * np.where(biases >= 0,1,-1)[:,None]

    ds = []
    for i,j in combinations(range(m),2):
        pi0 = (1 + aligned[i] @ records[i,0])/2
        pi1 = (1 + aligned[i] @ records[i,1])/2
        pj0 = (1 + aligned[j] @ records[j,0])/2
        pj1 = (1 + aligned[j] @ records[j,1])/2
        d = 0.5 * (
            pi0*(1-pj0)+(1-pi0)*pj0 +
            pi1*(1-pj1)+(1-pi1)*pj1
        )
        if readout_q > 0:
            d = 2*readout_q*(1-readout_q) + (1-2*readout_q)**2 * d
        ds.append(d)
    return max(ds)

def helstrom_error(theta_deg):
    return (1-np.sin(np.deg2rad(theta_deg)/2))/2

def oracle_worst_floor(theta_deg, readout_q=0.0):
    es = [helstrom_error(t) for t in theta_deg]
    vals = []
    for i,j in combinations(range(len(es)),2):
        d = es[i] + es[j] - 2*es[i]*es[j]
        if readout_q > 0:
            d = 2*readout_q*(1-readout_q) + (1-2*readout_q)**2*d
        vals.append(d)
    return max(vals)

# ---------- Main benchmark ----------
theta_A = [180,180,180,180,180]
theta_B = [180,180,180,72,100]
shots_grid = [64,128,256,512]
worlds = 40

rows = []
for name, theta in [("Chen_A_strong",theta_A), ("Chen_B_mixed",theta_B)]:
    for shots in shots_grid:
        for w in range(worlds):
            rng = np.random.default_rng(SEED + 100000*w + shots + (0 if name.endswith("strong") else 50000))
            rec, oracle = make_records(theta, rng)

            # EIQL: 27 env-only settings, N shots each.
            sched, env_data = sample_environment_only(rec, shots, rng)
            eiql_axes, signal = estimate_eiql_axes(sched, env_data, len(theta))

            # Stronger S-assisted baseline: 9 settings, 3N shots each.
            # Equal total number of copies: 27*N == 9*(3N).
            sys_axis = random_unit(rng)
            sys_data = sample_system_assisted(rec, sys_axis, 3*shots, rng)
            sys_axes = estimate_system_assisted_axes(sys_data, len(theta))

            rows.append({
                "setting": name,
                "shots_per_eiql_setting": shots,
                "world": w,
                "total_copies_each_method": 27*shots,
                "eiql_axis_error_deg": axis_errors_deg(eiql_axes,oracle).mean(),
                "eiql_worst_disagreement": worst_disagreement(eiql_axes,rec),
                "eiql_pair_signal": signal,
                "system_assisted_axis_error_deg": axis_errors_deg(sys_axes,oracle).mean(),
                "system_assisted_worst_disagreement": worst_disagreement(sys_axes,rec),
            })

bench = pd.DataFrame(rows)
summary = bench.groupby(["setting","shots_per_eiql_setting"]).agg(
    total_copies=("total_copies_each_method","first"),
    eiql_axis_error_mean=("eiql_axis_error_deg","mean"),
    eiql_axis_error_sd=("eiql_axis_error_deg","std"),
    eiql_D_mean=("eiql_worst_disagreement","mean"),
    eiql_D_sd=("eiql_worst_disagreement","std"),
    system_axis_error_mean=("system_assisted_axis_error_deg","mean"),
    system_axis_error_sd=("system_assisted_axis_error_deg","std"),
    system_D_mean=("system_assisted_worst_disagreement","mean"),
    system_D_sd=("system_assisted_worst_disagreement","std"),
).reset_index()

# ---------- Readout-noise stress at 256 shots/setting ----------
noise_rows = []
for q in [0.0,0.02,0.05]:
    for name,theta in [("Chen_A_strong",theta_A),("Chen_B_mixed",theta_B)]:
        for w in range(30):
            rng = np.random.default_rng(SEED + 700000 + 10000*w + int(1000*q) + (0 if name.endswith("strong") else 1234))
            rec,oracle = make_records(theta,rng)
            sched,data = sample_environment_only(rec,256,rng,readout_q=q)
            axes,signal = estimate_eiql_axes(sched,data,len(theta))
            noise_rows.append({
                "setting":name, "readout_q":q, "world":w,
                "axis_error_deg":axis_errors_deg(axes,oracle).mean(),
                "observed_worst_disagreement":worst_disagreement(axes,rec,readout_q=q),
                "oracle_observed_floor":oracle_worst_floor(theta,readout_q=q),
                "pair_signal":signal
            })
noise_df = pd.DataFrame(noise_rows)
noise_summary = noise_df.groupby(["setting","readout_q"]).agg(
    axis_error_mean=("axis_error_deg","mean"),
    axis_error_sd=("axis_error_deg","std"),
    D_mean=("observed_worst_disagreement","mean"),
    D_sd=("observed_worst_disagreement","std"),
    oracle_floor=("oracle_observed_floor","first"),
    pair_signal_mean=("pair_signal","mean"),
).reset_index()

# ---------- Permutation / independent-fragment null ----------
null_rows = []
for w in range(60):
    rng = np.random.default_rng(SEED + 900000 + w)
    rec,oracle = make_records(theta_A,rng)

    sched,d_real = sample_environment_only(rec,256,rng,independent_null=False)
    axes_real,signal_real = estimate_eiql_axes(sched,d_real,5)

    sched,d_null = sample_environment_only(rec,256,rng,independent_null=True)
    axes_null,signal_null = estimate_eiql_axes(sched,d_null,5)

    null_rows.append({
        "world":w,
        "real_pair_signal":signal_real,
        "null_pair_signal":signal_null,
        "real_D":worst_disagreement(axes_real,rec),
        # independent balanced fragments have population D=0.5 regardless of axes
        "null_population_D":0.5
    })
null_df = pd.DataFrame(null_rows)

# ---------- Settings scaling ----------
scale_rows = []
for m in range(2,13):
    oa_n = len(oa_schedule(m))
    scale_rows.append({
        "environment_fragments_m":m,
        "total_qubits_if_system_included":m+1,
        "EIQL_env_only_pair_moments_settings":oa_n,
        "system_assisted_pair_tomography_settings":9,
        "full_Pauli_QST_settings":3**(m+1),
        "QST_to_EIQL_setting_ratio":3**(m+1)/oa_n
    })
scaling = pd.DataFrame(scale_rows)

# ---------- Save ----------
bench.to_csv(OUT/"eiql_vs_tomography_runs.csv", index=False)
summary.to_csv(OUT/"eiql_vs_tomography_summary.csv", index=False)
noise_df.to_csv(OUT/"eiql_vs_tomography_noise_runs.csv", index=False)
noise_summary.to_csv(OUT/"eiql_vs_tomography_noise_summary.csv", index=False)
null_df.to_csv(OUT/"eiql_vs_tomography_null.csv", index=False)
scaling.to_csv(OUT/"eiql_vs_tomography_scaling.csv", index=False)

# ---------- Figures ----------
fig,ax = plt.subplots(figsize=(7.6,4.8))
for setting,grp in summary.groupby("setting"):
    ax.errorbar(
        grp["total_copies"],grp["eiql_axis_error_mean"],
        yerr=grp["eiql_axis_error_sd"],marker="o",capsize=3,
        label=f"EIQL env-only — {setting}"
    )
    ax.errorbar(
        grp["total_copies"],grp["system_axis_error_mean"],
        yerr=grp["system_axis_error_sd"],marker="s",capsize=3,
        label=f"S-assisted baseline — {setting}"
    )
ax.set_xscale("log")
ax.set_xlabel("Total copies / shots (equal budget)")
ax.set_ylabel("Mean decoder-axis error (degrees)")
ax.set_title("Environment-only EIQL vs system-assisted correlation tomography")
ax.grid(True,alpha=0.25)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(OUT/"eiql_vs_tomography_equal_budget.png",dpi=190)
plt.show()

fig,ax = plt.subplots(figsize=(7.4,4.7))
ax.semilogy(
    scaling["environment_fragments_m"],
    scaling["full_Pauli_QST_settings"],
    marker="o",label="Full Pauli QST"
)
ax.semilogy(
    scaling["environment_fragments_m"],
    scaling["EIQL_env_only_pair_moments_settings"],
    marker="s",label="EIQL env-only pair-moment design"
)
ax.semilogy(
    scaling["environment_fragments_m"],
    scaling["system_assisted_pair_tomography_settings"],
    marker="^",label="S-assisted task-specific baseline"
)
ax.set_xlabel("Number of environment fragments m")
ax.set_ylabel("Distinct measurement settings")
ax.set_title("Measurement-setting scaling")
ax.grid(True,alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"eiql_vs_tomography_settings_scaling.png",dpi=190)
plt.show()

# ---------- Concise printed report ----------
pd.set_option("display.max_columns",20)
print("\nEQUAL-TOTAL-COPY BENCHMARK (40 hidden-basis worlds)")
print(summary.round(5).to_string(index=False))

print("\nREADOUT-NOISE STRESS, 256 shots per EIQL setting (30 worlds)")
print(noise_summary.round(5).to_string(index=False))

print("\nNULL CONTROL, 256 shots/setting (60 worlds)")
print(pd.DataFrame({
    "real_pair_signal_mean":[null_df.real_pair_signal.mean()],
    "null_pair_signal_mean":[null_df.null_pair_signal.mean()],
    "real_D_mean":[null_df.real_D.mean()],
    "null_population_D":[0.5]
}).round(5).to_string(index=False))

print("\nRESOURCE SCALING")
print(scaling.to_string(index=False))
