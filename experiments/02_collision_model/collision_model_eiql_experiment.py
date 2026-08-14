# Environment-Induced Quantum Learning: collision-model experiment
# Executed in ChatGPT session, seed 20260813.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.optimize import differential_evolution
from pathlib import Path

SEED = 20260813
rng = np.random.default_rng(SEED)

# ---------- basic quantum utilities ----------
I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
ket0 = np.array([1,0], dtype=complex)
ket1 = np.array([0,1], dtype=complex)
ketp = (ket0 + ket1)/np.sqrt(2)

def random_su2(rng):
    M = rng.normal(size=(2,2)) + 1j*rng.normal(size=(2,2))
    Q, R = np.linalg.qr(M)
    phases = np.diag(R)
    phases = phases / np.abs(phases)
    Q = Q @ np.diag(np.conj(phases))
    det = np.linalg.det(Q)
    Q = Q / np.sqrt(det)
    return Q

VS = random_su2(rng)
VE = random_su2(rng)
A_pointer = VS @ Z @ VS.conj().T
P1_pointer = VS @ np.array([[0,0],[0,1]], complex) @ VS.conj().T
Y_env = VE @ Y @ VE.conj().T
env0 = VE @ ket0

def bloch_of_state(psi):
    return np.array([np.real(np.vdot(psi, X @ psi)), np.real(np.vdot(psi, Y @ psi)), np.real(np.vdot(psi, Z @ psi))])

hidden_env_axis = bloch_of_state(env0)

def unit_from_angles(theta, phi):
    return np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])

def apply_one(state, U, q, nq):
    t = state.reshape([2]*nq)
    axes = [q] + [i for i in range(nq) if i != q]
    inv = np.argsort(axes)
    t = np.transpose(t, axes).reshape(2, -1)
    t = U @ t
    t = np.transpose(t.reshape([2]*nq), inv)
    return t.reshape(-1)

def apply_two(state, U, q1, q2, nq):
    axes = [q1, q2] + [i for i in range(nq) if i not in (q1, q2)]
    inv = np.argsort(axes)
    t = np.transpose(state.reshape([2]*nq), axes).reshape(4, -1)
    t = U @ t
    return np.transpose(t.reshape([2]*nq), inv).reshape(-1)

def reduced_density_pure(state, keep, nq):
    keep = list(keep)
    trace = [i for i in range(nq) if i not in keep]
    t = np.transpose(state.reshape([2]*nq), keep + trace)
    t = t.reshape(2**len(keep), 2**len(trace))
    return t @ t.conj().T

def measurement_projectors(n):
    op = n[0]*X + n[1]*Y + n[2]*Z
    return [(I2-op)/2, (I2+op)/2]

def binary_mi(joint):
    joint = np.real_if_close(joint).astype(float)
    joint = np.clip(joint, 0, None); joint = joint/joint.sum()
    pa = joint.sum(axis=1, keepdims=True); pb = joint.sum(axis=0, keepdims=True)
    den = pa @ pb; mask = joint > 0
    return float(np.sum(joint[mask]*np.log2(joint[mask]/den[mask])))

def pair_joint_from_rho(rho2, n):
    Ms = measurement_projectors(n)
    joint = np.zeros((2,2), float)
    for a in range(2):
        for b in range(2):
            joint[a,b] = np.real(np.trace(np.kron(Ms[a], Ms[b]) @ rho2))
    joint = np.clip(joint,0,None)
    return joint/joint.sum()

def build_collision_state(N=6, gamma_deg=90, drift_deg=0, scrambled=False, seed=0):
    rr = np.random.default_rng(seed); nq=N+1
    psiS = VS @ ketp
    state = psiS
    for _ in range(N): state = np.kron(state, env0)
    gamma = np.deg2rad(gamma_deg); drift = np.deg2rad(drift_deg)
    C_drift = VS @ X @ VS.conj().T
    Udrift = expm(-1j*(drift/2)*C_drift) if drift_deg != 0 else I2
    for j in range(N):
        if scrambled:
            Vj = random_su2(rr); P1j = Vj @ np.array([[0,0],[0,1]], complex) @ Vj.conj().T
        else:
            P1j = P1_pointer
        Ucol = expm(-1j * gamma * np.kron(P1j, Y_env))
        state = apply_two(state, Ucol, 0, j+1, nq)
        if j < N-1 and drift_deg != 0:
            state = apply_one(state, Udrift, 0, nq)
    return state/np.linalg.norm(state)

def population_objective_from_state(state, N, n):
    vals=[]
    for i in range(N):
        for j in range(i+1,N):
            rho2 = reduced_density_pure(state, [i+1,j+1], N+1)
            vals.append(binary_mi(pair_joint_from_rho(rho2,n)))
    return float(np.mean(vals))

def optimize_env_measurement(state,N,seed=0):
    def obj(v): return -population_objective_from_state(state,N,unit_from_angles(*v))
    res=differential_evolution(obj, [(0,np.pi),(0,2*np.pi)], seed=seed, tol=1e-9, polish=True)
    n=unit_from_angles(*res.x)
    angle=np.rad2deg(np.arccos(np.clip(abs(np.dot(n, hidden_env_axis)),-1,1)))
    return n,-res.fun,angle

def system_env_mi(state,N,n,env_index=1):
    rho = reduced_density_pure(state,[0,env_index],N+1)
    Ms = measurement_projectors(n)
    Ps = [VS @ np.array([[1,0],[0,0]],complex) @ VS.conj().T, VS @ np.array([[0,0],[0,1]],complex) @ VS.conj().T]
    joint=np.zeros((2,2),float)
    for a in range(2):
        for b in range(2): joint[a,b]=np.real(np.trace(np.kron(Ps[a],Ms[b])@rho))
    return binary_mi(joint)

def env_outcome_distribution(state,N,n):
    vals, vecs=np.linalg.eigh(n[0]*X+n[1]*Y+n[2]*Z)
    Umeas=vecs.conj().T; st=state.copy()
    for q in range(1,N+1): st=apply_one(st,Umeas,q,N+1)
    probs=np.abs(st.reshape([2]*(N+1)))**2
    p=probs.sum(axis=0).reshape(-1); p=np.clip(p,0,None)
    return p/p.sum()

def bits_from_indices(indices,N):
    shifts=np.arange(N-1,-1,-1)
    return ((indices[:,None]>>shifts)&1).astype(int)

def empirical_pair_mi(outcomes):
    vals=[]
    for i in range(outcomes.shape[1]):
        for j in range(i+1,outcomes.shape[1]):
            joint=np.zeros((2,2),float); np.add.at(joint,(outcomes[:,i],outcomes[:,j]),1)
            vals.append(binary_mi(joint))
    return float(np.mean(vals))

def finite_collision_learn(state,N,m_per_candidate=200,n_candidates=200,seed=0):
    rr=np.random.default_rng(seed)
    V=rr.normal(size=(n_candidates,3)); V/=np.linalg.norm(V,axis=1,keepdims=True)
    bestJ=-1; bestn=None
    for n in V:
        p=env_outcome_distribution(state,N,n)
        inds=rr.choice(len(p),size=m_per_candidate,p=p)
        J=empirical_pair_mi(bits_from_indices(inds,N))
        if J>bestJ: bestJ=J; bestn=n.copy()
    angle=np.rad2deg(np.arccos(np.clip(abs(np.dot(bestn,hidden_env_axis)),-1,1)))
    return bestJ,population_objective_from_state(state,N,bestn),angle

def pointer_coherence(rhoS):
    rp = VS.conj().T @ rhoS @ VS
    return float(abs(rp[0,1]))

def system_entropy_bits(rhoS):
    vals = np.linalg.eigvalsh((rhoS+rhoS.conj().T)/2)
    vals = np.clip(np.real(vals),1e-15,1)
    return float(-np.sum(vals*np.log2(vals)))

def collision_trajectory(N=8, gamma_deg=45):
    nq=N+1; state=VS@ketp
    for _ in range(N): state=np.kron(state,env0)
    Ucol=expm(-1j*np.deg2rad(gamma_deg)*np.kron(P1_pointer,Y_env))
    rows=[]
    rhoS=reduced_density_pure(state,[0],nq); rows.append((0,pointer_coherence(rhoS),system_entropy_bits(rhoS)))
    for j in range(N):
        state=apply_two(state,Ucol,0,j+1,nq)
        rhoS=reduced_density_pure(state,[0],nq)
        rows.append((j+1,pointer_coherence(rhoS),system_entropy_bits(rhoS)))
    return pd.DataFrame(rows,columns=["collisions","pointer_coherence","system_entropy_bits"])

def helstrom_axis_for_gamma(gamma_deg):
    Ue=expm(-1j*np.deg2rad(gamma_deg)*Y_env)
    r0=bloch_of_state(env0); r1=bloch_of_state(Ue@env0); d=r0-r1
    return d/np.linalg.norm(d)

def build_fully_scrambled_state(N=6,gamma_deg=90,seed=0):
    rr=np.random.default_rng(seed); nq=N+1; state=VS@ketp; local=[]
    for _ in range(N):
        Vej=random_su2(rr); ej=Vej@ket0; local.append((Vej,ej)); state=np.kron(state,ej)
    for j in range(N):
        Vsj=random_su2(rr); P1j=Vsj@np.array([[0,0],[0,1]],complex)@Vsj.conj().T
        Vej,_=local[j]; Yej=Vej@Y@Vej.conj().T
        state=apply_two(state,expm(-1j*np.deg2rad(gamma_deg)*np.kron(P1j,Yej)),0,j+1,nq)
    return state/np.linalg.norm(state)

if __name__ == "__main__":
    N=6
    settings=[("stable",g,0,False) for g in [90,75,60,45,30]] + [("drift",90,d,False) for d in [5,15,30]] + [("scrambled",g,0,True) for g in [90,60]]
    rows=[]
    for idx,(kind,gamma,drift,scrambled) in enumerate(settings):
        state=build_collision_state(N,gamma,drift,scrambled,SEED+idx)
        n,J,angle=optimize_env_measurement(state,N,SEED+100+idx)
        rows.append({"model":kind,"gamma_deg":gamma,"drift_deg":drift,"population_pair_MI_bits":J,"angle_to_true_env_record_axis_deg":angle,"system_pointer_vs_env_MI_bits":system_env_mi(state,N,n)})
    coll_df=pd.DataFrame(rows)
    print(coll_df.round(5).to_string(index=False))

    outdir=Path(__file__).resolve().parent/"outputs"; outdir.mkdir(parents=True,exist_ok=True)
    coll_df.to_csv(outdir/"collision_model_population_results.csv",index=False)

    traj45=collision_trajectory(8,45); traj45.to_csv(outdir/"collision_model_decoherence_trajectory.csv",index=False)
    stable_check=[]
    for gamma in [90,75,60,45,30]:
        state=build_collision_state(N,gamma,0,False,SEED+gamma)
        n,J,_=optimize_env_measurement(state,N,SEED+300+gamma)
        hel=helstrom_axis_for_gamma(gamma)
        ang=np.rad2deg(np.arccos(np.clip(abs(np.dot(n,hel)),-1,1)))
        stable_check.append({"gamma_deg":gamma,"angle_to_Helstrom_deg":ang,"MI_bits":J})
    pd.DataFrame(stable_check).to_csv(outdir/"collision_model_helstrom_check.csv",index=False)
