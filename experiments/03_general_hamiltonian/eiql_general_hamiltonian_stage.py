# EIQL Stage 3: unknown general Hamiltonians
# Environment-only learner on controlled general two-qubit interaction families.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import expm
from scipy.spatial.transform import Rotation
from scipy.optimize import minimize
from pathlib import Path

SEED3 = 20260813 + 300
I2 = np.eye(2, dtype=complex)
PAULIS=[np.array([[0,1],[1,0]],complex),np.array([[0,-1j],[1j,0]],complex),np.array([[1,0],[0,-1]],complex)]
X,Y,Z=PAULIS
OUT=Path(__file__).resolve().parent/"outputs"; OUT.mkdir(parents=True,exist_ok=True)

def random_so3(rng): return Rotation.random(random_state=rng).as_matrix()
def bloch_state(r):
    rho=(I2+r[0]*X+r[1]*Y+r[2]*Z)/2; vals,vecs=np.linalg.eigh(rho); return vecs[:,np.argmax(vals)]
def orthogonal_unit(v):
    basis=np.eye(3)[np.argmin(np.abs(v))]; u=np.cross(v,basis); return u/np.linalg.norm(u)
def pauli_from_vec(v): return v[0]*X+v[1]*Y+v[2]*Z

def two_qubit_H_from_J(J):
    H=np.zeros((4,4),complex)
    for a in range(3):
        for b in range(3): H += J[a,b]*np.kron(PAULIS[a],PAULIS[b])
    return H

def apply_two(state,U,q1,q2,nq):
    axes=[q1,q2]+[i for i in range(nq) if i not in (q1,q2)]; inv=np.argsort(axes)
    t=np.transpose(state.reshape([2]*nq),axes).reshape(4,-1); t=U@t
    return np.transpose(t.reshape([2]*nq),inv).reshape(-1)

def apply_one(state,U,q,nq):
    axes=[q]+[i for i in range(nq) if i!=q]; inv=np.argsort(axes)
    t=np.transpose(state.reshape([2]*nq),axes).reshape(2,-1); t=U@t
    return np.transpose(t.reshape([2]*nq),inv).reshape(-1)

def reduced_density_pure(state,keep,nq):
    trace=[i for i in range(nq) if i not in keep]; t=np.transpose(state.reshape([2]*nq),list(keep)+trace)
    t=t.reshape(2**len(keep),2**len(trace)); return t@t.conj().T

def measurement_projectors(n):
    O=pauli_from_vec(n); return [(I2-O)/2,(I2+O)/2]
def binary_mi(joint):
    joint=np.clip(np.real_if_close(joint).astype(float),0,None); joint/=joint.sum(); pa=joint.sum(1,keepdims=True); pb=joint.sum(0,keepdims=True); den=pa@pb; mask=joint>1e-15
    return float(np.sum(joint[mask]*np.log2(joint[mask]/den[mask])))
def pair_mi(rho2,n):
    M=measurement_projectors(n); joint=np.array([[np.real(np.trace(np.kron(M[a],M[b])@rho2)) for b in range(2)] for a in range(2)])
    return binary_mi(joint)

def collision_from_J(J,N=5,gamma=np.pi/4):
    U,s,Vh=np.linalg.svd(J); u1=U[:,0]; v1=Vh.T[:,0]; psiE=bloch_state(orthogonal_unit(v1)); psiS=bloch_state(orthogonal_unit(u1)); state=psiS
    for _ in range(N): state=np.kron(state,psiE)
    Ucol=expm(-1j*gamma*two_qubit_H_from_J(J))
    for j in range(N): state=apply_two(state,Ucol,0,j+1,N+1)
    return state/np.linalg.norm(state),u1,v1,s

def pair_rhos(state,N): return [reduced_density_pure(state,[i+1,j+1],N+1) for i in range(N) for j in range(i+1,N)]
def unit_from_angles(v):
    theta,phi=v; return np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
def angles_from_unit(n): return np.array([np.arccos(np.clip(n[2],-1,1)),np.arctan2(n[1],n[0])%(2*np.pi)])

def optimize_common_measurement(rhos,rng,n_random=220):
    dirs=rng.normal(size=(n_random,3)); dirs/=np.linalg.norm(dirs,axis=1,keepdims=True)
    def stats(n):
        vals=np.array([pair_mi(r,n) for r in rhos]); return vals.mean(),np.quantile(vals,.25),vals.std(),vals.min()
    avgs=np.array([stats(n)[0] for n in dirs]); x0=angles_from_unit(dirs[np.argmax(avgs)])
    res=minimize(lambda v:-stats(unit_from_angles(v))[0],x0,method="Nelder-Mead",options={"maxiter":250,"xatol":1e-8,"fatol":1e-10})
    n=unit_from_angles(res.x); mean,q25,std,mn=stats(n); return n,mean,q25,std,mn

def make_J(eps,rng):
    Rs=random_so3(rng); Re=random_so3(rng); return Rs@np.diag([1.0,eps,0.7*eps])@Re.T

def env_outcome_distribution(state,N,n):
    _,vecs=np.linalg.eigh(pauli_from_vec(n)); st=state.copy()
    for q in range(1,N+1): st=apply_one(st,vecs.conj().T,q,N+1)
    p=(np.abs(st.reshape([2]*(N+1)))**2).sum(axis=0).reshape(-1); p=np.clip(p,0,None); return p/p.sum()
def bits_from_indices(indices,N):
    shifts=np.arange(N-1,-1,-1); return ((indices[:,None]>>shifts)&1).astype(int)
def empirical_pair_stats(outcomes):
    vals=[]
    for i in range(outcomes.shape[1]):
        for j in range(i+1,outcomes.shape[1]):
            joint=np.zeros((2,2),float); np.add.at(joint,(outcomes[:,i],outcomes[:,j]),1); vals.append(binary_mi(joint))
    vals=np.asarray(vals); return vals.mean(),np.quantile(vals,.25),vals.std(),vals.min()
def sample_env(state,N,n,m,rng):
    p=env_outcome_distribution(state,N,n); return bits_from_indices(rng.choice(len(p),size=m,p=p),N)

def finite_unknown_H_learn(J,N=5,train_shots=180,val_shots=2500,n_candidates=140,seed=0):
    rng=np.random.default_rng(seed); state,u1,v1,s=collision_from_J(J,N=N,gamma=np.pi/4)
    candidates=rng.normal(size=(n_candidates,3)); candidates/=np.linalg.norm(candidates,axis=1,keepdims=True); best_score=-np.inf; best_n=None
    for n in candidates:
        mean,*_=empirical_pair_stats(sample_env(state,N,n,train_shots,rng))
        if mean>best_score: best_score=mean; best_n=n.copy()
    val=sample_env(state,N,best_n,val_shots,rng); val_mean,val_q25,val_std,val_min=empirical_pair_stats(val); null_q25=[]
    for _ in range(80):
        sh=val.copy()
        for j in range(N): sh[:,j]=sh[rng.permutation(val_shots),j]
        _,qq,_,_=empirical_pair_stats(sh); null_q25.append(qq)
    null95=float(np.quantile(null_q25,.95))
    return {"pointer_fraction":s[0]**2/np.sum(s**2),"commutator_residual":np.sqrt(s[1]**2+s[2]**2)/s[0],"train_best_mean_MI":best_score,"val_mean_MI":val_mean,"val_q25_MI":val_q25,"val_min_MI":val_min,"null95_q25_MI":null95,"excess_over_null95":val_q25-null95}

N=5; eps_grid=[0.0,0.05,0.10,0.20,0.40,0.70,1.00]; rows=[]
for eps in eps_grid:
    for rep in range(10):
        rng=np.random.default_rng(SEED3+int(eps*10000)+rep); J=make_J(eps,rng); state,u1,v1,s=collision_from_J(J,N=N,gamma=np.pi/4); _,mean,q25,std,mn=optimize_common_measurement(pair_rhos(state,N),rng)
        rows.append({"eps":eps,"rep":rep,"pointer_fraction":s[0]**2/np.sum(s**2),"commutator_residual":np.sqrt(s[1]**2+s[2]**2)/s[0],"learned_mean_MI_bits":mean,"learned_q25_MI_bits":q25,"pair_MI_std_bits":std,"learned_min_MI_bits":mn})
gen_df=pd.DataFrame(rows); summary=gen_df.groupby("eps").agg(pointer_fraction=("pointer_fraction","mean"),commutator_residual=("commutator_residual","mean"),mean_MI=("learned_mean_MI_bits","mean"),mean_MI_std=("learned_mean_MI_bits","std"),q25_MI=("learned_q25_MI_bits","mean"),min_MI=("learned_min_MI_bits","mean"),pair_dispersion=("pair_MI_std_bits","mean")).reset_index()
gen_df.to_csv(OUT/"general_H_population_results.csv",index=False); summary.to_csv(OUT/"general_H_summary.csv",index=False)

finite_rows=[]
for eps in [0.0,0.10,0.20,0.40,0.70,1.00]:
    for rep in range(6):
        rng=np.random.default_rng(SEED3+50000+int(eps*10000)+rep); out=finite_unknown_H_learn(make_J(eps,rng),seed=SEED3+70000+int(eps*10000)+rep); out.update(eps=eps,rep=rep); finite_rows.append(out)
finite_H_df=pd.DataFrame(finite_rows); finite_summary=finite_H_df.groupby("eps").agg(pointer_fraction=("pointer_fraction","mean"),residual=("commutator_residual","mean"),val_q25_mean=("val_q25_MI","mean"),val_q25_std=("val_q25_MI","std"),null95_mean=("null95_q25_MI","mean"),excess_mean=("excess_over_null95","mean"),excess_min=("excess_over_null95","min")).reset_index()
finite_H_df.to_csv(OUT/"general_H_finite_results.csv",index=False); finite_summary.to_csv(OUT/"general_H_finite_summary.csv",index=False)

print(summary.round(5).to_string(index=False)); print("\nFINITE\n",finite_summary.round(5).to_string(index=False))
