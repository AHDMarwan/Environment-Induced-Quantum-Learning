# EIQL noisy-NISQ stress test
# Two-qubit local depolarization after each collision + symmetric readout flips.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import expm
from pathlib import Path

SEED = 20260814
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], complex); Y = np.array([[0,-1j],[1j,0]], complex); Z = np.array([[1,0],[0,-1]], complex)
Hh = np.array([[1,1],[1,-1]], complex)/np.sqrt(2); ket0 = np.array([1,0], complex); P1 = np.array([[0,0],[0,1]], complex)

def random_su2(rng):
    M = rng.normal(size=(2,2)) + 1j*rng.normal(size=(2,2)); Q,R = np.linalg.qr(M)
    d = np.diag(R); d = d/np.abs(d); Q = Q @ np.diag(np.conj(d)); return Q/np.sqrt(np.linalg.det(Q))

def apply2_state(state,U,q1,q2,n):
    axes=[q1,q2]+[i for i in range(n) if i not in (q1,q2)]; inv=np.argsort(axes)
    t=np.transpose(state.reshape([2]*n),axes).reshape(4,-1)
    return np.transpose((U@t).reshape([2]*n),inv).reshape(-1)

def embed_two(U,q1,q2,n):
    E=np.eye(2**n,dtype=complex); return np.column_stack([apply2_state(E[:,k],U,q1,q2,n) for k in range(2**n)])

def reduced_density(rho, keep, n):
    trace=[i for i in range(n) if i not in keep]; T=rho.reshape([2]*n+[2]*n); current_n=n
    for q in sorted(trace, reverse=True): T=np.trace(T,axis1=q,axis2=q+current_n); current_n-=1
    return T.reshape(2**len(keep),2**len(keep))

def embed_replacement(rest_rho, pair, n):
    pair=set(pair); rest=[q for q in range(n) if q not in pair]; dim=2**n; out=np.zeros((dim,dim),complex)
    for i in range(dim):
        bi=[(i>>(n-1-q))&1 for q in range(n)]
        for j in range(dim):
            bj=[(j>>(n-1-q))&1 for q in range(n)]
            if any(bi[q]!=bj[q] for q in pair): continue
            ri=rj=0
            for q in rest: ri=(ri<<1)|bi[q]; rj=(rj<<1)|bj[q]
            out[i,j]=0.25*rest_rho[ri,rj]
    return out

def local_pair_depolarize(rho,p,pair,n):
    if p<=0: return rho
    rest=[q for q in range(n) if q not in pair]; rest_rho=reduced_density(rho,rest,n)
    return (1-p)*rho + p*embed_replacement(rest_rho,pair,n)

def bloch(psi): return np.array([np.real(np.vdot(psi,P@psi)) for P in (X,Y,Z)])
def hbin(p):
    p=float(np.clip(p,1e-12,1-1e-12)); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def unitvec(k,rng):
    v=rng.normal(size=(k,3)); return v/np.linalg.norm(v,axis=1,keepdims=True)
def proj(n):
    O=n[0]*X+n[1]*Y+n[2]*Z; return [(I2-O)/2,(I2+O)/2]

def build_noisy_density(N=4, gamma=np.pi/2, p2=0.0, seed=0):
    rng=np.random.default_rng(seed); n=N+1; VS,VE=random_su2(rng),random_su2(rng)
    psiS=VS@(Hh@ket0); e0=VE@ket0; psi=psiS
    for _ in range(N): psi=np.kron(psi,e0)
    rho=np.outer(psi,psi.conj()); Yenv=VE@Y@VE.conj().T; Psys=VS@P1@VS.conj().T; Ucol=expm(-1j*gamma*np.kron(Psys,Yenv))
    for j in range(N):
        Uf=embed_two(Ucol,0,j+1,n); rho=Uf@rho@Uf.conj().T; rho=local_pair_depolarize(rho,p2,(0,j+1),n)
    return rho, bloch(e0)

def prep_rhos(rho,N):
    n=N+1; singles=[reduced_density(rho,[j+1],n) for j in range(N)]
    pairs={(i,j):reduced_density(rho,[i+1,j+1],n) for i in range(N) for j in range(i+1,N)}
    return singles,pairs

def observed_stats(rhos,n,readout_q):
    singles,pairs=rhos; Ps=proj(n); ent=[]
    for rho1 in singles:
        p_true=float(np.real(np.trace(Ps[1]@rho1))); p_obs=readout_q+(1-2*readout_q)*p_true; ent.append(hbin(p_obs))
    Q=np.kron(Ps[0],Ps[1])+np.kron(Ps[1],Ps[0]); dis=[]
    for rho2 in pairs.values():
        d_true=float(np.real(np.trace(Q@rho2))); dis.append(2*readout_q*(1-readout_q)+(1-2*readout_q)**2*d_true)
    return min(ent),max(dis)

N=4; epsilon=0.10; Qaxes=5000
p2_values=[0.0,0.002,0.005,0.01,0.02]; ro_values=[0.0,0.005,0.01,0.02,0.05]
rows=[]
for pi,p2 in enumerate(p2_values):
    rho,axis=build_noisy_density(N=N,p2=p2,seed=SEED); rhos=prep_rhos(rho,N); rng=np.random.default_rng(SEED+1000+pi); cands=unitvec(Qaxes,rng)
    for q in ro_values:
        vals=np.array([observed_stats(rhos,n,q) for n in cands]); feasible=vals[:,1] <= epsilon
        if feasible.any():
            hstar=vals[feasible,0].max(); near=feasible & (vals[:,0] >= hstar-1e-3); inds=np.where(near)[0]; k=inds[np.argmin(vals[inds,1])]
            angle=np.degrees(np.arccos(np.clip(abs(cands[k]@axis),-1,1))); rows.append([p2,q,hstar,vals[k,1],angle,True])
        else:
            hstar=vals[:,0].max(); near=vals[:,0] >= hstar-1e-3; rows.append([p2,q,hstar,vals[near,1].min(),np.nan,False])
noise_df=pd.DataFrame(rows,columns=["two_qubit_depolarizing_p","readout_flip_q","max_richness_bits","best_disagreement","angle_deg","feasible_at_epsilon_0p10"])
noise_df.to_csv(OUT/"eiql_noisy_nisq_results.csv",index=False)

settings=[("clean",0.0,0.0),("mild",0.005,0.01),("moderate",0.01,0.02),("readout-heavy",0.002,0.05),("beyond-eps",0.02,0.05)]
multi_rows=[]; n_worlds=12; Qmulti=3500
for si,(label,p2,q) in enumerate(settings):
    for w in range(n_worlds):
        rho,axis=build_noisy_density(N=4,p2=p2,seed=SEED+5000+100*si+w); rhos=prep_rhos(rho,4)
        rr=np.random.default_rng(SEED+8000+100*si+w); cands=unitvec(Qmulti,rr); vals=np.array([observed_stats(rhos,n,q) for n in cands]); feasible=vals[:,1] <= 0.10
        if feasible.any():
            hstar=vals[feasible,0].max(); near=feasible & (vals[:,0]>=hstar-1e-3); inds=np.where(near)[0]; k=inds[np.argmin(vals[inds,1])]
            ang=np.degrees(np.arccos(np.clip(abs(cands[k]@axis),-1,1))); multi_rows.append([label,p2,q,w,True,hstar,vals[k,1],ang])
        else:
            hstar=vals[:,0].max(); near=vals[:,0]>=hstar-1e-3; multi_rows.append([label,p2,q,w,False,hstar,vals[near,1].min(),np.nan])
multi_df=pd.DataFrame(multi_rows,columns=["setting","p2","readout_q","world","feasible","max_richness_bits","best_disagreement","axis_error_deg"])
multi_summary=multi_df.groupby(["setting","p2","readout_q"]).agg(feasible_fraction=("feasible","mean"),richness_mean=("max_richness_bits","mean"),disagreement_mean=("best_disagreement","mean"),disagreement_sd=("best_disagreement","std"),axis_error_mean_deg=("axis_error_deg","mean"),axis_error_sd_deg=("axis_error_deg","std")).reset_index()
multi_df.to_csv(OUT/"eiql_noisy_nisq_multiseed.csv",index=False); multi_summary.to_csv(OUT/"eiql_noisy_nisq_multiseed_summary.csv",index=False)

fig,ax=plt.subplots(figsize=(7.4,4.6))
for p2,g in noise_df.groupby("two_qubit_depolarizing_p"): ax.plot(g["readout_flip_q"],g["best_disagreement"],marker="o",label=f"p2={p2:g}")
ax.axhline(epsilon,linestyle="--",label="EIQL tolerance eps=0.10"); ax.set_xlabel("Symmetric readout bit-flip probability q"); ax.set_ylabel("Best worst-pair disagreement")
ax.set_title("EIQL under gate depolarization and readout noise"); ax.grid(True,alpha=0.25); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(OUT/"eiql_noisy_nisq_disagreement.png",dpi=190); plt.close(fig)

print(noise_df.round(5).to_string(index=False)); print("\nMULTI-SEED\n",multi_summary.round(5).to_string(index=False))
