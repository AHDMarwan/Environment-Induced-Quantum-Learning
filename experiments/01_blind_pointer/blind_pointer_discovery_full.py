import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
from scipy.spatial.transform import Rotation
from pathlib import Path

SEED = 20260813
rng = np.random.default_rng(SEED)
R_hidden = Rotation.random(random_state=rng).as_matrix()

def unit_from_angles(theta, phi):
    return np.array([
        np.sin(theta)*np.cos(phi),
        np.sin(theta)*np.sin(phi),
        np.cos(theta)
    ])

def bloch_states(alpha_deg, eta=0.0):
    a = np.deg2rad(alpha_deg)
    r0 = np.array([0.0,0.0,1.0])
    r1 = np.array([np.sin(2*a),0.0,np.cos(2*a)])
    shrink = 1.0-eta
    return shrink*(R_hidden@r0), shrink*(R_hidden@r1)

def p_plus(n,r):
    return np.clip((1.0+np.dot(n,r))/2.0,0.0,1.0)

def binary_mi_from_joint(joint):
    joint=np.asarray(joint,dtype=float)
    joint=joint/joint.sum()
    px=joint.sum(axis=1,keepdims=True)
    py=joint.sum(axis=0,keepdims=True)
    denom=px@py
    mask=joint>0
    return float(np.sum(joint[mask]*np.log2(joint[mask]/denom[mask])))

def population_pair_mi(n,r0,r1,prior=0.5):
    joint=np.zeros((2,2))
    for r,px in [(r0,prior),(r1,1-prior)]:
        q=p_plus(n,r)
        probs=np.array([1-q,q])
        joint += px*np.outer(probs,probs)
    return binary_mi_from_joint(joint)

def oracle_metrics(n,r0,r1,prior=0.5):
    q0,q1=p_plus(n,r0),p_plus(n,r1)
    joint=np.array([
        [prior*(1-q0),prior*q0],
        [(1-prior)*(1-q1),(1-prior)*q1]
    ])
    ixz=binary_mi_from_joint(joint)
    acc=max(joint[0,0]+joint[1,1],joint[0,1]+joint[1,0])
    return ixz,acc

def optimize_population(alpha_deg,eta=0.0):
    r0,r1=bloch_states(alpha_deg,eta)
    def obj(v):
        return -population_pair_mi(unit_from_angles(*v),r0,r1)
    res=differential_evolution(
        obj,[(0,np.pi),(0,2*np.pi)],
        seed=SEED+int(alpha_deg*10)+int(eta*1000),
        tol=1e-10,polish=True
    )
    n=unit_from_angles(*res.x)
    ixz,acc=oracle_metrics(n,r0,r1)
    d=r0-r1
    hel=d/np.linalg.norm(d)
    angle=np.rad2deg(np.arccos(np.clip(abs(np.dot(n,hel)),-1,1)))
    return n,-res.fun,ixz,acc,angle

def empirical_pairwise_mi(outcomes):
    m,k=outcomes.shape
    vals=[]
    for i in range(k):
        for j in range(i+1,k):
            joint=np.zeros((2,2))
            np.add.at(joint,(outcomes[:,i],outcomes[:,j]),1)
            vals.append(binary_mi_from_joint(joint))
    return float(np.mean(vals))

def sample_runs(n,r0,r1,m=500,k=4,shuffled=False,rng=None):
    if rng is None:
        rng=np.random.default_rng()
    X=rng.integers(0,2,size=m)
    q0,q1=p_plus(n,r0),p_plus(n,r1)
    q=np.where(X==0,q0,q1)
    outcomes=(rng.random((m,k))<q[:,None]).astype(int)
    if shuffled:
        for j in range(k):
            outcomes[:,j]=outcomes[rng.permutation(m),j]
    return X,outcomes

def random_unit_vectors(ncand,rng):
    v=rng.normal(size=(ncand,3))
    return v/np.linalg.norm(v,axis=1,keepdims=True)

def finite_shot_learn(alpha_deg=90,eta=0.0,m_per_candidate=300,
                      k=4,n_candidates=250,seed=0,shuffled=False):
    rr=np.random.default_rng(seed)
    r0,r1=bloch_states(alpha_deg,eta)
    candidates=random_unit_vectors(n_candidates,rr)
    best_score=-np.inf
    best_n=None
    for n in candidates:
        _,outs=sample_runs(n,r0,r1,m=m_per_candidate,k=k,
                           shuffled=shuffled,rng=rr)
        score=empirical_pairwise_mi(outs)
        if score>best_score:
            best_score=score
            best_n=n.copy()
    ixz,acc=oracle_metrics(best_n,r0,r1)
    d=r0-r1
    hel=d/np.linalg.norm(d)
    angle=np.rad2deg(np.arccos(np.clip(abs(np.dot(best_n,hel)),-1,1)))
    return best_score,ixz,acc,angle

if __name__ == "__main__":
    print("Hidden rotation matrix (unknown to learner):")
    print(R_hidden)

    print("\nPopulation optima")
    for eta in [0.0,0.10,0.25]:
        for alpha in [90,75,60,45,30,15]:
            n,J,ixz,acc,angle=optimize_population(alpha,eta)
            print(alpha,eta,J,ixz,acc,angle,n)

    print("\nFinite-shot perfect-broadcast learner")
    for m in [50,100,300,1000]:
        vals=[]
        for rep in range(20):
            vals.append(finite_shot_learn(
                90,0.0,m,4,250,SEED+1000*m+rep,False))
        a=np.asarray(vals)
        print(m,a.mean(axis=0),a.std(axis=0))

    print("\nShuffle control")
    for shuffled in [False,True]:
        vals=[]
        for rep in range(20):
            vals.append(finite_shot_learn(
                90,0.0,300,4,250,SEED+90000+rep,shuffled))
        a=np.asarray(vals)
        print(shuffled,a.mean(axis=0),a.std(axis=0))
