# EIQL-inspired synthetic multimodal medical experiment
# Seed family based on 20260813.

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, adjusted_rand_score, normalized_mutual_info_score, r2_score
from scipy.optimize import linear_sum_assignment

SEED = 20260813
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
MOD_DIMS = {"Blood": 20, "MRI": 50, "ECG": 15}
N_TRAIN, N_IID, N_SHIFT = 6000, 2000, 2000

def latent_features(z):
    z1, z2, z3 = z[:,0], z[:,1], z[:,2]
    return np.column_stack([z1,z2,z3,z1*z2,z1*z3,z2*z3,z1**2,z2**2,z3**2,np.tanh(z1),np.tanh(z2),np.tanh(z3)])

def generate_latent(n, rng):
    y = rng.integers(0, 3, size=n)
    means = np.array([[-1.6,-1.1,-1.3],[0.0,0.3,0.1],[1.5,1.1,1.4]])
    scales = np.array([[0.45,0.45,0.45],[0.55,0.55,0.55],[0.50,0.50,0.50]])
    z = means[y] + rng.normal(size=(n,3))*scales[y]
    age = rng.normal(loc=np.array([-0.2,0.0,0.25])[y], scale=0.9)
    return y, z, age

def build_generators(rng):
    phi_dim=12; gens={}
    weights={"Blood":np.array([0.8,1.25,0.7]),"MRI":np.array([0.75,0.7,1.35]),"ECG":np.array([1.25,0.8,0.65])}
    for name,d in MOD_DIMS.items():
        W=rng.normal(scale=1/np.sqrt(phi_dim),size=(phi_dim,d)); W[:3]*=weights[name][:,None]; a=rng.normal(scale=0.22,size=d); gens[name]=(W,a)
    shortcut=rng.normal(size=(3,MOD_DIMS["MRI"])); shortcut/=np.linalg.norm(shortcut,axis=1,keepdims=True)
    return gens,shortcut

GEN_RNG=np.random.default_rng(SEED+1)
GENERATORS,MRI_SHORTCUT=build_generators(GEN_RNG)

def make_split(n, seed, shortcut_mode="trainlike"):
    rng=np.random.default_rng(seed); y,z,age=generate_latent(n,rng); phi=latent_features(z)
    if shortcut_mode=="trainlike":
        correct=rng.random(n)<0.90; h=np.where(correct,y,rng.integers(0,3,size=n))
    elif shortcut_mode=="shift": h=rng.integers(0,3,size=n)
    else: raise ValueError(shortcut_mode)
    Xs={}
    for name,d in MOD_DIMS.items():
        W,a=GENERATORS[name]; signal=phi@W+age[:,None]*a[None,:]; noise_scale={"Blood":0.80,"MRI":0.75,"ECG":0.85}[name]
        X=signal+rng.normal(scale=noise_scale,size=(n,d)); nuisance=rng.normal(size=(n,3)); B=rng.normal(scale=0.18,size=(3,d)); X+=nuisance@B
        if name=="MRI": X += 4.0*MRI_SHORTCUT[h]
        Xs[name]=X.astype(np.float64)
    return Xs,y,z,age,h

class RedundancyGCCA:
    def __init__(self,pca_dim=8,latent_dim=3): self.pca_dim=pca_dim; self.latent_dim=latent_dim
    def fit(self,Xdict):
        self.mods=list(Xdict.keys()); self.scalers={}; self.pcas={}; Zs=[]
        for m in self.mods:
            sc=StandardScaler().fit(Xdict[m]); Xs=sc.transform(Xdict[m]); pca=PCA(n_components=self.pca_dim,whiten=True,random_state=SEED).fit(Xs); Z=pca.transform(Xs)
            self.scalers[m]=sc; self.pcas[m]=pca; Zs.append(Z)
        n=len(Zs[0]); p=self.pca_dim; M=len(Zs); R=np.zeros((M*p,M*p))
        for i in range(M):
            for j in range(M):
                if i!=j: R[i*p:(i+1)*p,j*p:(j+1)*p]=(Zs[i].T@Zs[j])/(n-1)
        vals,vecs=np.linalg.eigh((R+R.T)/2); order=np.argsort(vals)[::-1][:self.latent_dim]; self.eigvals_=vals[order]; V=vecs[:,order]
        self.Wblocks={m:V[i*p:(i+1)*p] for i,m in enumerate(self.mods)}; self.view_scales={}
        for m,Z in zip(self.mods,Zs):
            s=(Z@self.Wblocks[m]).std(axis=0,ddof=1); self.view_scales[m]=np.where(s>1e-8,s,1.0)
        return self
    def transform_views(self,Xdict):
        return {m:(self.pcas[m].transform(self.scalers[m].transform(Xdict[m]))@self.Wblocks[m])/self.view_scales[m] for m in self.mods}
    def transform(self,Xdict,available=None):
        if available is None: available=self.mods
        views=self.transform_views(Xdict); return np.mean([views[m] for m in available],axis=0)

class ConcatPCA:
    def __init__(self,latent_dim=3): self.latent_dim=latent_dim
    def fit(self,Xdict):
        self.mods=list(Xdict.keys()); self.scalers={m:StandardScaler().fit(Xdict[m]) for m in self.mods}; X=np.concatenate([self.scalers[m].transform(Xdict[m]) for m in self.mods],axis=1); self.pca=PCA(n_components=self.latent_dim,random_state=SEED).fit(X); return self
    def transform(self,Xdict): return self.pca.transform(np.concatenate([self.scalers[m].transform(Xdict[m]) for m in self.mods],axis=1))

def cluster_acc(y_true, clusters):
    k=len(np.unique(y_true)); C=np.zeros((k,k),dtype=int)
    for c,y in zip(clusters,y_true): C[c,y]+=1
    r,c=linear_sum_assignment(-C); mapping={rr:cc for rr,cc in zip(r,c)}; return accuracy_score(y_true,np.array([mapping[x] for x in clusters]))

def evaluate_one(train,iid,shift):
    Xtr,ytr,ztr,atr,htr=train; Xi,yi,zi,ai,hi=iid; Xs,ys,zs,as_,hs=shift
    eiql=RedundancyGCCA().fit(Xtr); pca=ConcatPCA().fit(Xtr); reps={"EIQL":(eiql.transform(Xtr),eiql.transform(Xi),eiql.transform(Xs)),"ConcatPCA":(pca.transform(Xtr),pca.transform(Xi),pca.transform(Xs))}
    sc_mri=StandardScaler().fit(Xtr["MRI"]); pca_mri=PCA(n_components=3,random_state=SEED).fit(sc_mri.transform(Xtr["MRI"])); reps["MRI-PCA"]=(pca_mri.transform(sc_mri.transform(Xtr["MRI"])),pca_mri.transform(sc_mri.transform(Xi["MRI"])),pca_mri.transform(sc_mri.transform(Xs["MRI"])))
    rows=[]
    for name,(Rtr,Ri,Rs) in reps.items():
        clf=LogisticRegression(max_iter=3000).fit(Rtr,ytr); acc_iid=accuracy_score(yi,clf.predict(Ri)); acc_shift=accuracy_score(ys,clf.predict(Rs)); reg=LinearRegression().fit(Rtr,ztr)
        hclf=LogisticRegression(max_iter=3000).fit(Rtr,htr); km=KMeans(n_clusters=3,n_init=40,random_state=SEED).fit(Rtr); cl_shift=km.predict(Rs)
        rows.append({"method":name,"IID_class_acc":acc_iid,"SHIFT_class_acc":acc_shift,"accuracy_drop":acc_iid-acc_shift,"latent_Z_R2_IID":r2_score(zi,reg.predict(Ri),multioutput="variance_weighted"),"latent_Z_R2_SHIFT":r2_score(zs,reg.predict(Rs),multioutput="variance_weighted"),"shortcut_h_acc_SHIFT":accuracy_score(hs,hclf.predict(Rs)),"SHIFT_cluster_acc":cluster_acc(ys,cl_shift),"SHIFT_ARI":adjusted_rand_score(ys,cl_shift),"SHIFT_NMI":normalized_mutual_info_score(ys,cl_shift)})
    scalers={m:StandardScaler().fit(Xtr[m]) for m in Xtr}; Ctr=np.concatenate([scalers[m].transform(Xtr[m]) for m in Xtr],axis=1); Ci=np.concatenate([scalers[m].transform(Xi[m]) for m in Xi],axis=1); Cs=np.concatenate([scalers[m].transform(Xs[m]) for m in Xs],axis=1); clf=LogisticRegression(max_iter=3000).fit(Ctr,ytr)
    rows.append({"method":"Raw supervised logistic","IID_class_acc":accuracy_score(yi,clf.predict(Ci)),"SHIFT_class_acc":accuracy_score(ys,clf.predict(Cs)),"accuracy_drop":accuracy_score(yi,clf.predict(Ci))-accuracy_score(ys,clf.predict(Cs)),"latent_Z_R2_IID":np.nan,"latent_Z_R2_SHIFT":np.nan,"shortcut_h_acc_SHIFT":np.nan,"SHIFT_cluster_acc":np.nan,"SHIFT_ARI":np.nan,"SHIFT_NMI":np.nan})
    return pd.DataFrame(rows),eiql

def make_split_with_generators(n,seed,generators,shortcut,shortcut_mode="trainlike"):
    rng=np.random.default_rng(seed); y,z,age=generate_latent(n,rng); phi=latent_features(z)
    if shortcut_mode=="trainlike":
        correct=rng.random(n)<0.90; h=np.where(correct,y,rng.integers(0,3,size=n))
    elif shortcut_mode=="shift": h=rng.integers(0,3,size=n)
    elif shortcut_mode=="reversed":
        target=(y+1)%3; correct=rng.random(n)<0.90; h=np.where(correct,target,rng.integers(0,3,size=n))
    else: raise ValueError(shortcut_mode)
    Xs={}
    for name,d in MOD_DIMS.items():
        W,a=generators[name]; signal=phi@W+age[:,None]*a[None,:]; noise_scale={"Blood":0.80,"MRI":0.75,"ECG":0.85}[name]; X=signal+rng.normal(scale=noise_scale,size=(n,d)); nuisance=rng.normal(size=(n,3)); B=rng.normal(scale=0.18,size=(3,d)); X+=nuisance@B
        if name=="MRI": X+=4.0*shortcut[h]
        Xs[name]=X.astype(np.float64)
    return Xs,y,z,age,h

def evaluate_core(train,iid,shift):
    Xtr,ytr,ztr,atr,htr=train; Xi,yi,zi,ai,hi=iid; Xs,ys,zs,as_,hs=shift
    models={}; eiql=RedundancyGCCA().fit(Xtr); models["EIQL"]=(eiql.transform(Xtr),eiql.transform(Xi),eiql.transform(Xs),eiql); pca=ConcatPCA().fit(Xtr); models["ConcatPCA"]=(pca.transform(Xtr),pca.transform(Xi),pca.transform(Xs),None)
    sc=StandardScaler().fit(Xtr["MRI"]); pm=PCA(n_components=3,random_state=SEED).fit(sc.transform(Xtr["MRI"])); models["MRI-PCA"]=(pm.transform(sc.transform(Xtr["MRI"])),pm.transform(sc.transform(Xi["MRI"])),pm.transform(sc.transform(Xs["MRI"])),None)
    rows=[]
    for name,(Rtr,Ri,Rs,extra) in models.items():
        clf=LogisticRegression(max_iter=2500).fit(Rtr,ytr); iid_acc=accuracy_score(yi,clf.predict(Ri)); sh_acc=accuracy_score(ys,clf.predict(Rs)); reg=LinearRegression().fit(Rtr,ztr); hclf=LogisticRegression(max_iter=2500).fit(Rtr,htr); rows.append((name,iid_acc,sh_acc,iid_acc-sh_acc,r2_score(zs,reg.predict(Rs),multioutput="variance_weighted"),accuracy_score(hs,hclf.predict(Rs))))
    scs={m:StandardScaler().fit(Xtr[m]) for m in Xtr}; ctr=np.concatenate([scs[m].transform(Xtr[m]) for m in Xtr],1); ci=np.concatenate([scs[m].transform(Xi[m]) for m in Xi],1); cs=np.concatenate([scs[m].transform(Xs[m]) for m in Xs],1); c=LogisticRegression(max_iter=2500).fit(ctr,ytr); ia=accuracy_score(yi,c.predict(ci)); sa=accuracy_score(ys,c.predict(cs)); rows.append(("Raw supervised logistic",ia,sa,ia-sa,np.nan,np.nan)); clf_e=LogisticRegression(max_iter=2500).fit(models["EIQL"][0],ytr); miss=accuracy_score(ys,clf_e.predict(eiql.transform(Xs,available=["Blood","ECG"])))
    return rows,miss

if __name__=="__main__":
    train=make_split(N_TRAIN,SEED+10,"trainlike"); iid=make_split(N_IID,SEED+20,"trainlike"); shift=make_split(N_SHIFT,SEED+30,"shift"); res,eiql_model=evaluate_one(train,iid,shift); res.to_csv(OUT/"synthetic_medical_results.csv",index=False); print(res.round(4).to_string(index=False))
    bench=[]; nrep=12
    for rep in range(nrep):
        gens,shortcut=build_generators(np.random.default_rng(SEED+1000+rep)); tr=make_split_with_generators(3500,SEED+2000+10*rep,gens,shortcut,"trainlike"); ti=make_split_with_generators(1200,SEED+2001+10*rep,gens,shortcut,"trainlike"); ts=make_split_with_generators(1200,SEED+2002+10*rep,gens,shortcut,"reversed"); rows,miss=evaluate_core(tr,ti,ts)
        for name,ia,sa,drop,zr2,hacc in rows: bench.append({"rep":rep,"method":name,"IID_acc":ia,"REVERSED_SHIFT_acc":sa,"drop":drop,"latent_Z_R2_shift":zr2,"shortcut_h_acc_shift":hacc,"EIQL_missing_MRI_acc":miss if name=="EIQL" else np.nan})
    bench_df=pd.DataFrame(bench); bench_summary=bench_df.groupby("method").agg(IID_acc_mean=("IID_acc","mean"),IID_acc_std=("IID_acc","std"),SHIFT_acc_mean=("REVERSED_SHIFT_acc","mean"),SHIFT_acc_std=("REVERSED_SHIFT_acc","std"),drop_mean=("drop","mean"),latent_Z_R2_mean=("latent_Z_R2_shift","mean"),shortcut_h_acc_mean=("shortcut_h_acc_shift","mean"),missing_MRI_acc_mean=("EIQL_missing_MRI_acc","mean")).reset_index(); bench_df.to_csv(OUT/"synthetic_medical_multiseed_results.csv",index=False); bench_summary.to_csv(OUT/"synthetic_medical_multiseed_summary.csv",index=False); print("\n12 INDEPENDENT SYNTHETIC MEDICAL WORLDS\n",bench_summary.round(4).to_string(index=False))
