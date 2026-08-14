import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.linalg import expm
from pathlib import Path

SEED=20260814
OUT=Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
I=np.eye(2,dtype=complex)
X=np.array([[0,1],[1,0]],complex)
Y=np.array([[0,-1j],[1j,0]],complex)
Z=np.array([[1,0],[0,-1]],complex)
Hh=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
ket0=np.array([1,0],complex)
P1=np.array([[0,0],[0,1]],complex)

def rsu2(r):
    M=r.normal(size=(2,2))+1j*r.normal(size=(2,2)); Q,R=np.linalg.qr(M)
    d=np.diag(R); d=d/np.abs(d); Q=Q@np.diag(np.conj(d)); return Q/np.sqrt(np.linalg.det(Q))

def a1(s,U,q,n):
    ax=[q]+[i for i in range(n) if i!=q]; inv=np.argsort(ax)
    t=np.transpose(s.reshape([2]*n),ax).reshape(2,-1)
    return np.transpose((U@t).reshape([2]*n),inv).reshape(-1)

def a2(s,U,q1,q2,n):
    ax=[q1,q2]+[i for i in range(n) if i not in (q1,q2)]; inv=np.argsort(ax)
    t=np.transpose(s.reshape([2]*n),ax).reshape(4,-1)
    return np.transpose((U@t).reshape([2]*n),inv).reshape(-1)

def red(s,keep,n):
    rest=[i for i in range(n) if i not in keep]
    t=np.transpose(s.reshape([2]*n),list(keep)+rest).reshape(2**len(keep),2**len(rest))
    return t@t.conj().T

def bloch(psi): return np.array([np.real(np.vdot(psi,P@psi)) for P in (X,Y,Z)])
def hbin(p):
    p=np.clip(float(p),1e-12,1-1e-12); return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))
def unitvec(k,r):
    v=r.normal(size=(k,3)); return v/np.linalg.norm(v,axis=1,keepdims=True)
def pauli_axis(n): return n[0]*X+n[1]*Y+n[2]*Z
def proj(n):
    O=pauli_axis(n); return [(I-O)/2,(I+O)/2]

def build(N=4,gamma=np.pi/2,drift=0,scr=False,seed=0):
    r=np.random.default_rng(seed); nq=N+1; VS,VE=rsu2(r),rsu2(r)
    ps=VS@(Hh@ket0); e0=VE@ket0; st=ps
    for _ in range(N): st=np.kron(st,e0)
    Yenv=VE@Y@VE.conj().T; Psys=VS@P1@VS.conj().T; D=VS@X@VS.conj().T
    for j in range(N):
        Pj=(rsu2(r)@P1@rsu2(r).conj().T) if False else Psys
        if scr:
            Vj=rsu2(r); Pj=Vj@P1@Vj.conj().T
        st=a2(st,expm(-1j*gamma*np.kron(Pj,Yenv)),0,j+1,nq)
        if j<N-1 and drift: st=a1(st,expm(-1j*(drift/2)*D),0,nq)
    return st/np.linalg.norm(st), bloch(e0)

def prep_rhos(st,N):
    nq=N+1
    singles=[red(st,[j+1],nq) for j in range(N)]
    pairs={(i,j):red(st,[i+1,j+1],nq) for i in range(N) for j in range(i+1,N)}
    return singles,pairs

def stats_exact_pre(rhos,n):
    singles,pairs=rhos; Ps=proj(n)
    ent=[hbin(np.real(np.trace(Ps[1]@rho))) for rho in singles]
    Q=np.kron(Ps[0],Ps[1])+np.kron(Ps[1],Ps[0])
    dis=[float(np.real(np.trace(Q@rho))) for rho in pairs.values()]
    return min(ent),max(dis)

def env_dist(st,N,n):
    vals,vecs=np.linalg.eigh(pauli_axis(n)); U=vecs.conj().T; s=st.copy()
    for q in range(1,N+1): s=a1(s,U,q,N+1)
    p=np.abs(s.reshape([2]*(N+1)))**2; p=p.sum(axis=0).reshape(-1); p=np.clip(p,0,None)
    return p/p.sum()

def bits(idx,N):
    sh=np.arange(N-1,-1,-1); return ((idx[:,None]>>sh)&1).astype(int)

def emp_stats(o):
    ent=[hbin(o[:,j].mean()) for j in range(o.shape[1])]
    dis=[np.mean(o[:,i]!=o[:,j]) for i in range(o.shape[1]) for j in range(i+1,o.shape[1])]
    return min(ent),max(dis)

def learn_finite(st,rhos,N,cands,eps,shots,rng,tau=0.03):
    vals=[]
    for n in cands:
        p=env_dist(st,N,n); idx=rng.choice(len(p),size=shots,p=p); h,d=emp_stats(bits(idx,N))
        if d<=eps: vals.append((h,d,n.copy()))
    if not vals: return None
    hstar=max(v[0] for v in vals); near=[v for v in vals if v[0]>=hstar-tau]
    chosen=min(near,key=lambda t:t[1]); h,d=stats_exact_pre(rhos,chosen[2])
    return h,d,chosen[2]

cases={
    'stable-perfect':dict(gamma=np.pi/2,drift=0,scr=False),
    'stable-partial':dict(gamma=np.pi/3,drift=0,scr=False),
    'drift-15deg':dict(gamma=np.pi/2,drift=np.deg2rad(15),scr=False),
    'scrambled-system':dict(gamma=np.pi/2,drift=0,scr=True),
    'no-collision':dict(gamma=0,drift=0,scr=False),
}
N=4
eps_grid=np.array([0.01,0.02,0.05,0.10,0.15,0.20,0.25,0.30,0.40])
Q=6000
front=[]
for ci,(name,pars) in enumerate(cases.items()):
    st,axis=build(N=N,seed=SEED+100*ci,**pars); rhos=prep_rhos(st,N)
    r=np.random.default_rng(SEED+40000+ci); cands=unitvec(Q,r)
    vals=np.array([stats_exact_pre(rhos,n) for n in cands])
    for eps in eps_grid:
        mask=vals[:,1]<=eps
        if not np.any(mask): front.append([name,eps,np.nan,np.nan])
        else:
            hstar=vals[mask,0].max(); near=mask & (vals[:,0]>=hstar-1e-3); dmin=vals[near,1].min()
            front.append([name,eps,hstar,dmin])
front_df=pd.DataFrame(front,columns=['case','epsilon','O_epsilon_MC_bits','tie_break_disagreement'])
front_df.to_csv(OUT/'eiql_v21_frontier_mc.csv',index=False)

def independent_baseline(eps):
    eps=np.asarray(eps,float); p=(1-np.sqrt(np.maximum(0,1-2*eps)))/2
    return np.array([hbin(x) for x in p])
base_df=pd.DataFrame({'epsilon':eps_grid,'R_ind_bits':independent_baseline(eps_grid)})
base_df.to_csv(OUT/'eiql_v21_independent_baseline.csv',index=False)

finite=[]
for ci,name in enumerate(cases):
    st,axis=build(N=N,seed=SEED+800+ci,**cases[name]); rhos=prep_rhos(st,N)
    for rep in range(20):
        r=np.random.default_rng(SEED+10000+100*ci+rep); cands=unitvec(500,r)
        out=learn_finite(st,rhos,N,cands,0.10,600,r)
        if out is None: finite.append([name,rep,np.nan,np.nan,np.nan])
        else:
            h,d,n=out; ang=np.degrees(np.arccos(np.clip(abs(n@axis),-1,1))); finite.append([name,rep,h,d,ang])
fin_df=pd.DataFrame(finite,columns=['case','rep','min_entropy_bits','max_disagreement','angle_deg'])
fin_df.to_csv(OUT/'eiql_v21_finite_runs.csv',index=False)
rows=[]
for name,g in fin_df.groupby('case'):
    valid=g.dropna(); n=len(valid)
    def stat(col):
        if n==0: return (np.nan,np.nan,np.nan)
        mean=valid[col].mean(); sd=valid[col].std(ddof=1) if n>1 else 0.; ci=1.96*sd/np.sqrt(n) if n>1 else 0.
        return mean,sd,ci
    hm,hs,hci=stat('min_entropy_bits'); dm,ds,dci=stat('max_disagreement'); am,as_,aci=stat('angle_deg')
    rows.append([name,n/20,hm,hs,hci,dm,ds,dci,am,as_,aci])
summary=pd.DataFrame(rows,columns=['case','feasible_rate','Hmin_mean','Hmin_sd','Hmin_95CI_half','Dmax_mean','Dmax_sd','Dmax_95CI_half','angle_mean_deg','angle_sd_deg','angle_95CI_half_deg'])
summary.to_csv(OUT/'eiql_v21_finite_summary.csv',index=False)

st,axis=build(N=N,seed=SEED+999,**cases['stable-perfect']); rhos=prep_rhos(st,N)
r=np.random.default_rng(SEED+30000); cands=unitvec(800,r); out=learn_finite(st,rhos,N,cands,0.10,1000,r)
if out is None: raise RuntimeError('No stable-perfect finite-shot solution')
_,_,n=out; p=env_dist(st,N,n); idx=r.choice(len(p),size=3000,p=p); o=bits(idx,N); obs_h,obs_d=emp_stats(o)
B=1000; null=[]
for _ in range(B):
    sh=o.copy()
    for j in range(N): sh[:,j]=sh[r.permutation(len(sh)),j]
    null.append(emp_stats(sh))
null_df=pd.DataFrame(null,columns=['min_entropy_bits','max_disagreement']); null_df.to_csv(OUT/'eiql_v21_permutation_null.csv',index=False)
count=int((null_df.max_disagreement<=obs_d).sum()); pval=(1+count)/(B+1)
perm_summary=pd.DataFrame([{'B':B,'observed_min_entropy_bits':obs_h,'observed_max_disagreement':obs_d,'null_D_mean':null_df.max_disagreement.mean(),'null_D_sd':null_df.max_disagreement.std(ddof=1),'null_D_5pct':null_df.max_disagreement.quantile(.05),'null_D_median':null_df.max_disagreement.median(),'null_D_95pct':null_df.max_disagreement.quantile(.95),'lower_tail_count':count,'permutation_p_value':pval}])
perm_summary.to_csv(OUT/'eiql_v21_permutation_summary.csv',index=False)

st,axis=build(N=N,seed=SEED,**cases['stable-perfect']); rhos=prep_rhos(st,N)
r=np.random.default_rng(SEED+77777); allc=unitvec(20000,r); allvals=np.array([stats_exact_pre(rhos,n) for n in allc]); conv=[]
for q in [50,100,300,1000,3000,6000,10000,20000]:
    vals=allvals[:q]; hstar=vals[:,0].max(); near=vals[:,0]>=hstar-1e-3
    k=np.where(near)[0][np.argmin(vals[near,1])]; n=allc[k]
    ang=np.degrees(np.arccos(np.clip(abs(n@axis),-1,1))); conv.append([q,hstar,vals[k,1],ang])
conv_df=pd.DataFrame(conv,columns=['candidate_axes','max_richness_bits','tie_break_min_disagreement','angle_to_hidden_axis_deg'])
conv_df.to_csv(OUT/'eiql_v21_search_convergence.csv',index=False)

fig,ax=plt.subplots(figsize=(7.4,4.7))
for name in cases:
    g=front_df[front_df['case']==name]; ax.plot(g.epsilon,g.O_epsilon_MC_bits,marker='o',label=name)
ax.plot(base_df.epsilon,base_df.R_ind_bits,linestyle='--',linewidth=2,label='analytic independent baseline')
ax.set_xlabel('Allowed worst-pair disagreement epsilon'); ax.set_ylabel('Maximum minimum fragment entropy (bits)')
ax.set_title('Monte-Carlo approximation to the EIQL population frontier'); ax.set_ylim(-0.03,1.05); ax.grid(True,alpha=.25); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT/'eiql_v21_frontier.png',dpi=190); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.4)); ax.plot(conv_df.candidate_axes,conv_df.tie_break_min_disagreement,marker='o')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Number of randomly sampled Bloch axes'); ax.set_ylabel('Best disagreement among near-max-richness axes')
ax.set_title('Monte-Carlo search convergence: stable-perfect case'); ax.grid(True,alpha=.25)
fig.tight_layout(); fig.savefig(OUT/'eiql_v21_search_convergence.png',dpi=190); plt.close(fig)

print('FRONTIER\n',front_df.to_string(index=False))
print('\nFINITE SUMMARY\n',summary.to_string(index=False))
print('\nPERMUTATION\n',perm_summary.to_string(index=False))
print('\nCONVERGENCE\n',conv_df.to_string(index=False))
