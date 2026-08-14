# EIQL benchmark based on Chen et al. (Science Bulletin 2019) photonic Quantum Darwinism architecture.
# Independently hidden local decoder bases, multistart search, subset discovery,
# fidelity-matched isotropic noise proxy, and finite-shot statistic search.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from pathlib import Path

SEED=20260814
OUT=Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
X=np.array([[0,1],[1,0]],complex); Y=np.array([[0,-1j],[1j,0]],complex); Z=np.array([[1,0],[0,-1]],complex); PAULIS=(X,Y,Z)

def random_su2(rng):
    M=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2)); Q,R=np.linalg.qr(M)
    d=np.diag(R); d=d/np.abs(d); Q=Q@np.diag(np.conj(d)); return Q/np.sqrt(np.linalg.det(Q))

def bloch(psi): return np.array([np.real(np.vdot(psi,P@psi)) for P in PAULIS])
def h2_vec(p):
    p=np.clip(p,1e-12,1-1e-12); return -(p*np.log2(p)+(1-p)*np.log2(1-p))
def unitvec(k,rng):
    v=rng.normal(size=(k,3)); return v/np.linalg.norm(v,axis=1,keepdims=True)

def chen_records(theta_deg,seed):
    rng=np.random.default_rng(seed); rec=[]; hel=[]
    for th in theta_deg:
        t=np.deg2rad(th); e0=np.array([1,0],complex); e1=np.array([np.cos(t/2),np.sin(t/2)],complex); V=random_su2(rng)
        r0=bloch(V@e0); r1=bloch(V@e1); rec.append([r0,r1]); d=r0-r1; hel.append(d/np.linalg.norm(d))
    return np.array(rec),np.array(hel)

def pair_d(qj,qk,white=0.0):
    d0=qj[0]*(1-qk[0])+(1-qj[0])*qk[0]; d1=qj[1]*(1-qk[1])+(1-qj[1])*qk[1]
    return (1-white)*(.5*(d0+d1))+white*.5

def entropy_of_q(q,white=0.0):
    p=(1-white)*(.5*(q[0]+q[1]))+white*.5; return float(h2_vec(np.array([p]))[0])

def global_stats(qs,subset,white=0.0):
    ent=[entropy_of_q(qs[j],white) for j in subset]; ds=[pair_d(qs[a],qs[b],white) for a,b in combinations(subset,2)]
    return min(ent),max(ds) if ds else 0.0

def learn_decoders(rec,subset,rng,K=900,passes=5,white=0.0,entropy_floor=.985):
    m=len(rec); pools=[]; axes=np.zeros((m,3)); qs=np.zeros((m,2))
    for j in range(m):
        C=unitvec(K,rng); C=np.vstack([C,-C]); pools.append(C)
        q0=(1+C@rec[j,0])/2; q1=(1+C@rec[j,1])/2; H=h2_vec((1-white)*(.5*(q0+q1))+white*.5); k=np.argmax(H)
        axes[j]=C[k]; qs[j]=[q0[k],q1[k]]
    for _ in range(passes):
        changed=False
        for j in subset:
            C=pools[j]; q0=(1+C@rec[j,0])/2; q1=(1+C@rec[j,1])/2; H=h2_vec((1-white)*(.5*(q0+q1))+white*.5)
            others=[k for k in subset if k!=j]; unaffected=0.0
            for a,b in combinations(others,2): unaffected=max(unaffected,pair_d(qs[a],qs[b],white))
            dmax=np.full(len(C),unaffected)
            for k in others:
                qk=qs[k]; d0=q0*(1-qk[0])+(1-q0)*qk[0]; d1=q1*(1-qk[1])+(1-q1)*qk[1]
                dmax=np.maximum(dmax,(1-white)*(.5*(d0+d1))+white*.5)
            other_h=min([entropy_of_q(qs[k],white) for k in others], default=1.0); hmin=np.minimum(H,other_h); feasible=hmin>=entropy_floor
            if np.any(feasible):
                idx=np.where(feasible)[0]; kbest=idx[np.argmin(dmax[idx])]
            else:
                hstar=hmin.max(); idx=np.where(hmin>=hstar-1e-4)[0]; kbest=idx[np.argmin(dmax[idx])]
            old=axes[j].copy(); axes[j]=C[kbest]; qs[j]=[q0[kbest],q1[kbest]]; changed |= np.linalg.norm(old-axes[j])>1e-9
        if not changed: break
    h,d=global_stats(qs,subset,white); return axes,qs,h,d

def axis_errors(axes,hel):
    return np.degrees(np.arccos(np.clip(np.abs(np.sum(axes*hel,axis=1)),-1,1)))
def fidelity_proxy_p(F,d=64): return float(np.clip((1-F)/(1-1/d),0,1))
def helstrom_error(theta_deg): return (1-np.sin(np.deg2rad(theta_deg)/2))/2
def ideal_pair_floor(theta_i,theta_j):
    ei=helstrom_error(theta_i); ej=helstrom_error(theta_j); return ei+ej-2*ei*ej

def learn_multistart(rec,subset,seed,K=650,passes=5,restarts=8,white=0.0,entropy_floor=.985):
    best=None
    for r in range(restarts):
        rr=np.random.default_rng(seed+7919*r); axes,qs,h,d=learn_decoders(rec,subset,rr,K,passes,white,entropy_floor); key=(-h,d)
        if best is None or key < best[0]: best=(key,axes,qs,h,d)
    return best[1:]

def finite_stats_for_candidates(rec,qs,subset,j,C,shots,rng,white=0.0):
    K=len(C); q0=(1+C@rec[j,0])/2; q1=(1+C@rec[j,1])/2
    pm=(1-white)*(.5*(q0+q1))+white*.5; Hj=h2_vec(rng.binomial(shots,pm)/shots); Hmins=Hj.copy()
    for k in subset:
        if k==j: continue
        pk=(1-white)*(.5*(qs[k,0]+qs[k,1]))+white*.5; Hmins=np.minimum(Hmins,h2_vec(rng.binomial(shots,pk,size=K)/shots))
    dmax=np.zeros(K)
    for a,b in combinations(subset,2):
        if j in (a,b):
            k=b if a==j else a; qk=qs[k]; d0=q0*(1-qk[0])+(1-q0)*qk[0]; d1=q1*(1-qk[1])+(1-q1)*qk[1]; d=(1-white)*(.5*(d0+d1))+white*.5
        else: d=np.full(K,pair_d(qs[a],qs[b],white))
        dmax=np.maximum(dmax,rng.binomial(shots,np.clip(d,0,1))/shots)
    return q0,q1,Hmins,dmax

def finite_fast_once(rec,subset,rng,K=180,passes=4,shots=700,white=0.0,entropy_floor=.97):
    m=len(rec); pools=[]; axes=np.zeros((m,3)); qs=np.zeros((m,2))
    for j in range(m):
        C=unitvec(K,rng); C=np.vstack([C,-C]); pools.append(C); q0=(1+C@rec[j,0])/2; q1=(1+C@rec[j,1])/2
        H=h2_vec(rng.binomial(shots,(1-white)*(.5*(q0+q1))+white*.5)/shots); kb=np.argmax(H); axes[j]=C[kb]; qs[j]=[q0[kb],q1[kb]]
    for _ in range(passes):
        for j in subset:
            C=pools[j]; q0,q1,hmin,dmax=finite_stats_for_candidates(rec,qs,subset,j,C,shots,rng,white); feas=hmin>=entropy_floor
            if np.any(feas): idx=np.where(feas)[0]; kb=idx[np.argmin(dmax[idx])]
            else:
                hstar=hmin.max(); idx=np.where(hmin>=hstar-0.005)[0]; kb=idx[np.argmin(dmax[idx])]
            axes[j]=C[kb]; qs[j]=[q0[kb],q1[kb]]
    h,d=global_stats(qs,subset,white); return axes,qs,h,d

def finite_fast_multistart(rec,subset,seed,K=180,passes=4,shots=700,restarts=4,white=0.0):
    best=None
    for r in range(restarts):
        rr=np.random.default_rng(seed+15485863*r); axes,qs,h,d=finite_fast_once(rec,subset,rr,K,passes,shots,white); key=(-h,d)
        if best is None or key<best[0]: best=(key,axes,qs,h,d)
    return best[1:]

thetaA=[180,180,180,180,180]; thetaB=[180,180,180,72,100]
pA=fidelity_proxy_p(.859); pB=fidelity_proxy_p(.703)
settings=[("A_ideal",thetaA,0.0),("B_ideal",thetaB,0.0),("A_fidelity_proxy",thetaA,pA),("B_fidelity_proxy",thetaB,pB)]

# Multi-start population benchmark.
refined=[]; nworld=12
for si,(name,theta,white) in enumerate(settings):
    for w in range(nworld):
        rec,hel=chen_records(theta,SEED+1000*si+w); axes,qs,h,d=learn_multistart(rec,list(range(5)),SEED+40000*si+100*w,K=650,passes=5,restarts=8,white=white)
        err=axis_errors(axes,hel); refined.append([name,w,h,d,err.mean(),err.max(),white])
refined=pd.DataFrame(refined,columns=["setting","world","min_entropy","worst_pair_disagreement","mean_axis_error_deg","max_axis_error_deg","white_noise_proxy"])
ref_sum=refined.groupby("setting").agg(min_entropy_mean=("min_entropy","mean"),disagreement_mean=("worst_pair_disagreement","mean"),disagreement_sd=("worst_pair_disagreement","std"),axis_error_mean_deg=("mean_axis_error_deg","mean"),axis_error_sd_deg=("mean_axis_error_deg","std")).reset_index()
refined.to_csv(OUT/"eiql_chen_multistart_runs.csv",index=False); ref_sum.to_csv(OUT/"eiql_chen_multistart_summary.csv",index=False)

# Three-fragment quality ranking in setting B.
subs=[]
for w in range(12):
    rec,hel=chen_records(thetaB,SEED+50000+w)
    for subset in combinations(range(5),3):
        axes,qs,h,d=learn_multistart(rec,list(subset),SEED+60000+100*w+sum((j+2)*1000 for j in subset),K=450,passes=4,restarts=5)
        subs.append([w,"".join(str(j+2) for j in subset),h,d])
subs=pd.DataFrame(subs,columns=["world","subset","entropy","disagreement"]); subs.to_csv(OUT/"eiql_chen_subset_runs.csv",index=False)
subsum=subs.groupby("subset").agg(entropy_mean=("entropy","mean"),disagreement_mean=("disagreement","mean"),disagreement_sd=("disagreement","std")).reset_index(); subsum.to_csv(OUT/"eiql_chen_subset_summary.csv",index=False)

# Finite-shot statistic search.
fs_rows=[]; shot_grid=[200,500,700,1500]
for si,(name,theta) in enumerate([("A_ideal",thetaA),("B_ideal",thetaB)]):
    for shots in shot_grid:
        for w in range(10):
            rec,hel=chen_records(theta,SEED+120000+1000*si+w); axes,qs,h,d=finite_fast_multistart(rec,list(range(5)),SEED+130000+10000*si+100*w+shots,K=160,passes=4,shots=shots,restarts=4)
            er=axis_errors(axes,hel); fs_rows.append([name,shots,w,h,d,er.mean(),er.max()])
fs=pd.DataFrame(fs_rows,columns=["setting","shots_per_statistic","world","validated_min_entropy","validated_worst_disagreement","mean_axis_error_deg","max_axis_error_deg"])
fs_sum=fs.groupby(["setting","shots_per_statistic"]).agg(entropy_mean=("validated_min_entropy","mean"),disagreement_mean=("validated_worst_disagreement","mean"),disagreement_sd=("validated_worst_disagreement","std"),axis_error_mean_deg=("mean_axis_error_deg","mean"),axis_error_sd_deg=("mean_axis_error_deg","std")).reset_index()
fs.to_csv(OUT/"eiql_chen_finite_stat_runs.csv",index=False); fs_sum.to_csv(OUT/"eiql_chen_finite_stat_summary.csv",index=False)

subfs=[]
for w in range(10):
    rec,hel=chen_records(thetaB,SEED+150000+w)
    for subset in combinations(range(5),3):
        axes,qs,h,d=finite_fast_multistart(rec,list(subset),SEED+160000+100*w+sum((j+2)*1000 for j in subset),K=130,passes=4,shots=700,restarts=4)
        subfs.append([w,"".join(str(j+2) for j in subset),h,d])
subfs=pd.DataFrame(subfs,columns=["world","subset","entropy","disagreement"]); subfs.to_csv(OUT/"eiql_chen_finite_subset_runs.csv",index=False)

fig,ax=plt.subplots(figsize=(7.6,4.6)); order=["A_ideal","B_ideal","A_fidelity_proxy","B_fidelity_proxy"]; g=ref_sum.set_index("setting").loc[order]
ax.bar(order,g["disagreement_mean"],yerr=g["disagreement_sd"],capsize=4); floors=[]
for nm in order:
    theta=dict((s[0],s[1]) for s in settings)[nm]; white=dict((s[0],s[2]) for s in settings)[nm]
    intr=max(ideal_pair_floor(theta[i],theta[j]) for i,j in combinations(range(5),2)); floors.append((1-white)*intr+white*.5)
ax.scatter(np.arange(len(order)),floors,marker="x",s=70,label="oracle physical floor"); ax.set_ylabel("Worst-pair disagreement"); ax.set_title("EIQL on Chen architecture: learned vs physical floor"); ax.tick_params(axis="x",rotation=18); ax.legend(); fig.tight_layout(); fig.savefig(OUT/"eiql_chen_multistart_vs_oracle.png",dpi=190); plt.close(fig)

print(ref_sum.round(6).to_string(index=False)); print("\nSUBSET RANKING\n",subsum.sort_values("disagreement_mean").to_string(index=False)); print("\nFINITE SHOT\n",fs_sum.round(5).to_string(index=False))
