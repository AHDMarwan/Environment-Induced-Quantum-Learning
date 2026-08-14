# EIQL Research Track

**Last updated:** 2026-08-14  
**Status:** Version 3 first-paper scope frozen at **theory + simulation**; not peer reviewed.  
**Current framing:** quantum measurement-learning framework/problem formulation, not a new universal machine-learning paradigm.

## Research question

Given repeated access to independently accessible quantum environment fragments from the same physical process, with no pointer labels and no prescribed decoder, learn local measurements whose outcomes are both rich and mutually consistent.

Current objective:

\[
D_\rho(\mathbf M)=\max_{i<j}P_\rho(Z_i\neq Z_j),
\qquad
R_\rho(\mathbf M)=\min_j H_\rho(Z_j),
\]

with learning objective

\[
\mathcal O^{\mathfrak M}_{\varepsilon,L}(\rho)
=\sup_{\mathbf M\in\mathfrak M^{(L)}}R_\rho(\mathbf M)
\quad\text{s.t.}\quad D_\rho(\mathbf M)\le\varepsilon.
\]

Fragmentwise output permutations are free. The theory identifies pointer information / decoder behavior on the occupied record states, not a unique POVM operator on the entire Hilbert space.

## Completed milestones

### M0 - Positioning and problem definition - DONE

Separated the EIQL question from established Quantum Darwinism:

- QD/SBS: how redundant objective records arise and what observers can infer;
- EIQL: when the correct environmental decoder is unknown, can redundancy itself train the decoder?

The novelty claim was narrowed from “new learning paradigm” to **new quantum learning framework/problem formulation**.

### M1-M3 - Early exploratory simulations - DONE / HISTORICAL

- blind pointer discovery with inter-fragment mutual information;
- explicit system-environment collision dynamics;
- generalized Hamiltonian stress tests.

These motivated the framework but predate the final richness/disagreement objective and are not the primary theorem evidence.

### M4 - Classical multiview sanity checks - DONE / AUXILIARY

Iris and synthetic Blood/MRI/ECG tests were used only to test whether a redundancy/shared-information inductive bias behaves sensibly in classical multiview data. They are not quantum evidence and do not support a quantum-advantage claim.

### M5 - Theory V1 -> V2 -> V2.1 repair cycle - DONE

Current theoretical core:

1. exact SBS pointer-information structural theorem;
2. alphabet-aware optimum and coarse-graining qualification;
3. operational decoder equivalence and free output relabelings;
4. robust near-SBS theorem using a global error indicator;
5. explicit, generally loose Bayes-recovery certificate;
6. finite-shot proposition for a pre-specified finite candidate class;
7. analytic independent-product binary null ceiling.

The central theorem language is **pointer-information identifiability under learned local decoders**, not measurement/POVM uniqueness.

### M6-M7 - Theory-matched five-qubit EIQL simulation - DONE

Primary script: `experiments/04_revised_objective/eiql_v21_simulation.py`.

At `epsilon=0.10`, stable-perfect and drift cases remain rich and feasible; no-collision follows the independent-product baseline; stable-partial and scrambled-system are infeasible in the tested tied-axis class. A lower-tail permutation null gives corrected Monte-Carlo `p=1/1001` for the representative stable-perfect learned decoder. Search-convergence diagnostics explicitly label the continuous frontier as a Monte-Carlo approximation.

### M8 - NISQ-style noise stress test - DONE

Primary script: `experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py`.

Across 12 hidden-basis worlds, representative mean disagreements were approximately:

- clean: `0.00013`;
- mild `(p2=0.005, q=0.01)`: `0.02951`;
- moderate `(p2=0.01, q=0.02)`: `0.05764`;
- readout-heavy `(p2=0.002, q=0.05)`: `0.09834`;
- stronger combined noise `(p2=0.02, q=0.05)`: `0.12676`, infeasible at `epsilon=0.10`.

Claim: finite operating region under this simplified local noise model, not noise immunity.

### M9 - Chen et al. external-architecture benchmark - DONE

Primary script: `experiments/06_chen2019/eiql_chen2019_benchmark.py`.

Published record strengths were modeled as

- A: `(180,180,180,180,180)` degrees;
- B: `(180,180,180,72,100)` degrees.

EIQL independently hides every environmental record basis with a local random SU(2), does not reveal system labels/pointer values/hidden bases, and learns separate local decoders from environment redundancy.

Population results over 12 hidden-basis worlds:

- A ideal: learned worst disagreement `0.00193`, oracle floor `0`;
- B ideal: learned worst disagreement `0.27689`, oracle floor `0.27487`;
- best three-fragment subset in B: photons `2,3,4` in `12/12` population worlds and `10/10` finite-shot worlds.

This is a simulation based on a published experimental architecture, not a reanalysis of raw laboratory data.

### M10 - Experimental-QD literature mapped to EIQL - DONE

Explicitly compared EIQL with:

- Chen et al. photonic Quantum Darwinism;
- Saini-Behera IBM Quantum-Darwinism circuits/tomography;
- Chisholm et al. objectivity witnessing;
- Zhu et al. superconducting Quantum Darwinism and designed local witnesses;
- Fu on uniqueness of redundant imprints;
- Touil-Yan-Zurek on observer consensus;
- Cheng-Hsieh-Yeh on learning an externally specified unknown quantum measurement;
- Sadoune et al. on unsupervised observable discovery;
- Jaderberg et al. on quantum self-supervised learning.

Current distinction: **designed/known witness or target measurement vs a decoder learned from same-event environmental redundancy**.

### M11 - EIQL vs tomography/resource benchmark - DONE IN SIMULATION

Primary script: `experiments/07_resource_benchmark/eiql_vs_tomography_resource_benchmark.py`.

For balanced binary conditionally independent qubit records, the centered Pauli cross-correlation factorizes as

\[
C_{ij}=\frac14(\mathbf r_{i0}-\mathbf r_{i1})(\mathbf r_{j0}-\mathbf r_{j1})^T,
\]

which yields a task-specific pair-moment/spectral decoder estimator. The factorization is used as an implementation identity, not claimed as a novel general theorem.

For five environment fragments:

- environment-only EIQL pair-moment design: `27` settings;
- system-assisted task-specific correlation baseline: `9` settings;
- full six-qubit Pauli QST: `729` settings.

Equal-copy benchmark over 40 hidden-basis worlds at `6912` copies per method:

| Setting | EIQL axis error | S-assisted axis error | EIQL worst D | S-assisted worst D |
|---|---:|---:|---:|---:|
| Chen A strong | 1.63 deg | 2.32 deg | 0.00092 | 0.00194 |
| Chen B mixed | 2.08 deg | 2.65 deg | 0.27536 | 0.27592 |

This does not establish universal resource superiority; the system-assisted baseline uses fewer settings and has a different access model.

### M12 - Version 3 manuscript - DONE

Current manuscript source: `paper/EIQL_v3.tex`. A 30-page PDF was compiled and visually preflighted at this checkpoint; generated PDFs are kept as release/build artifacts rather than the canonical source file in the repository.

Version 3 adds the Chen benchmark, the resource benchmark, classical/multiview and quantum-self-supervision framing, explicit experimental-QD comparisons, and freezes the first-paper scope at theory + simulation.

## Claims currently defensible

- EIQL is a coherent quantum measurement-learning framework/problem formulation.
- The supervision signal is redundancy across independently accessible fragments produced by the same physical event.
- Under exact SBS assumptions, exact rich agreement identifies deterministic pointer coarse-grainings; with enough alphabet/hardware expressivity the pointer information is recovered up to relabeling.
- Near SBS, richness + agreement imply a quantitative residual-pointer-uncertainty guarantee.
- A pre-specified finite candidate class admits a conservative finite-shot guarantee.
- The theory-matched, Chen-architecture, noise, null, and resource simulations behave consistently with the intended operational interpretation.

## Claims explicitly not made

- new universal machine-learning paradigm;
- quantum advantage;
- unique recovery of a physical POVM operator;
- arbitrary-state/SBS-free theorem;
- universal superiority over tomography;
- real-hardware EIQL demonstration;
- robustness to arbitrary correlated/non-Markovian hardware noise.

## Main remaining weaknesses

1. Robust theorem assumes proximity to a useful SBS reference state.
2. Continuous/adaptive decoder search is not covered by the finite-class theorem.
3. General correlated fragments remain outside the clean theorem.
4. Resource benchmark is structured and simulated; general copy/setting/runtime complexity is open.
5. No real-hardware EIQL result; this is now future work, not a Version 3 requirement.
6. External novelty scrutiny is still required because neighboring terminology spans QD, measurement learning, common randomness, sensing, and self-supervised QML.

## What remains before submission

### P0 - Manuscript and reproducibility cleanup

- [x] freeze Version 3 theory + simulation scope;
- [x] include Chen external-architecture benchmark;
- [x] include resource/tomography benchmark;
- [x] update novelty framing to “quantum measurement-learning framework”;
- [ ] run every canonical script from a clean environment and verify headline CSV values;
- [ ] add a single reproducibility command/Makefile for manuscript figures;
- [ ] audit all citations/claims line-by-line;
- [ ] remove obsolete scratch artifacts from the repository.

### P1 - External technical review

- [ ] one Quantum-Darwinism/open-systems expert;
- [ ] one quantum-learning/statistical-learning expert;
- [ ] ask specifically whether unknown-local-decoder learning from redundancy exists under another name;
- [ ] revise only in response to concrete technical issues.

### P2 - Submission preparation

- [ ] select venue after external review;
- [ ] adapt style/length to venue;
- [ ] prepare final abstract, cover letter, data/code statement, and reproducibility instructions.

### Future work, not required for Version 3

- real-hardware EIQL proof of principle;
- SBS-free reverse theorem: operational rich agreement -> approximate broadcast/objective-record structure;
- correlated/non-Markovian fragment theory;
- continuous/adaptive POVM-learning guarantees;
- L-ary/non-identical independent null ceilings;
- general resource scaling with fragment dimension/count and access model.

## Falsification criteria

EIQL should be substantially weakened if prior work is found with the same unknown-decoder-from-redundancy problem and comparable guarantees; if realistic null/non-Darwinian states generically reproduce the high-richness/low-disagreement region; if decoder search is consistently impractical relative to narrower alternatives; or if learned outputs fail to track pointer information even in regimes satisfying the theorem assumptions.
