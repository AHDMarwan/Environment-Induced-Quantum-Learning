# EIQL Research Track

**Last updated:** 2026-08-14  
**Status:** active working theory + simulation project; not peer reviewed.  
**Current framing:** EIQL is a *quantum measurement-learning framework/problem formulation*, not a claim of a new universal machine-learning paradigm.

## 1. Current research question

Given repeated access to environmental quantum fragments `E_1,...,E_m`, with no access required to the system `S`, no class labels, and no known pointer/readout basis, learn local decoders/POVMs whose outputs are both informative and redundantly consistent across independently accessible fragments.

Current objective:

```text
D_rho(M) = max_{i<j} P_rho(Z_i != Z_j)
R_rho(M) = min_j H_rho(Z_j)
```

and maximize `R_rho` over the admissible hardware-constrained decoder class subject to `D_rho <= epsilon`. Fragmentwise output permutations are free classical post-processing.

The theory identifies **pointer information / decoder behavior on the occupied environmental record states**, not a unique POVM operator on the entire Hilbert space.

---

## 2. Completed milestones

### M0 — Concept formation and literature positioning — DONE

The EIQL question was separated from the established Quantum-Darwinism question:

- QD: which information becomes redundant/objective in the environment?
- EIQL: if the correct environmental decoder is unknown, can it be *learned from redundancy itself*?

Current novelty claim is deliberately narrow: **unknown local measurement/decoder learning from same-event environmental redundancy**.

### M1 — Blind pointer discovery toy model — DONE

File: `experiments/01_blind_pointer/blind_pointer_discovery_full.py`

Binary hidden pointer variable, conditionally independent quantum records, hidden readout basis, and an early inter-fragment mutual-information discovery objective. Perfect broadcast records were recoverable; shuffling fragments across events destroyed the redundancy signal.

Historical only: the MI objective predates the final richness/disagreement formulation.

### M2 — Explicit collision dynamics — DONE

File: `experiments/02_collision_model/collision_model_eiql_experiment.py`

Moved from pre-built records to explicit system-environment collisions. Stable pointer dynamics supported blind decoder discovery; system drift and scrambled couplings degraded redundant recoverability.

### M3 — Generalized Hamiltonian stress test — DONE

File: `experiments/03_general_hamiltonian/eiql_general_hamiltonian_stage.py`

Explored interaction families of the form

```text
H_int = sum_{a,b=x,y,z} J_ab sigma_a tensor sigma_b
```

with increasingly competing system coupling directions. Environment-only learnability fell as the hidden interaction lost a dominant pointer direction.

Historical/exploratory: this also predates the final EIQL objective.

### M4 — Classical sanity checks — DONE / AUXILIARY ONLY

Files:

- `classical_sanity/iris/`
- `classical_sanity/synthetic_medical/`

Purpose: test whether the inductive bias “prefer information supported across multiple independent views” has a sensible classical analogue. These experiments are **not quantum evidence** and do not establish quantum advantage.

### M5 — Theory V1 -> V2 -> V2.1 repair cycle — DONE

Current manuscript status: `paper/README.md`.

Major repaired issues:

- output-alphabet qualification in the exact SBS result;
- corrected robust proof using a global error indicator;
- worst-pair disagreement instead of average disagreement;
- minimum-fragment entropy instead of a one-fragment richness score;
- fragmentwise output relabelings;
- operational equivalence of decoders on occupied record states;
- pointer-information identifiability rather than global POVM uniqueness;
- alphabet non-vacuity condition;
- finite-shot guarantee restricted to pre-specified finite measurement classes;
- correct lower-tail permutation statistic;
- Monte-Carlo frontier labelled as an approximation;
- analytic independent-product baseline;
- explicit Bayes recovery certificate.

Current theoretical components:

1. exact SBS pointer-information structural theorem;
2. robust theorem near an SBS reference state;
3. Bayes-recovery corollary, explicit but generally loose;
4. finite-class finite-shot proposition;
5. independent-product null lemma.

Positive internal referee-style reviews are working feedback, **not peer review**.

### M6 — Revised EIQL simulation matching the formal objective — DONE

File: `experiments/04_revised_objective/eiql_v21_simulation.py`

Uses the final theory-matched objective:

```text
R = min_j H(Z_j)
D = max_{i<j} P(Z_i != Z_j)
```

Stable perfect dynamics produced near-one-bit richness with near-zero worst-pair disagreement. No-collision independent records followed the analytic null ceiling. Scrambled dynamics became infeasible at stringent epsilon. Lower-tail permutation and search-convergence diagnostics were added.

### M7 — Finite-shot and search-convergence diagnostics — DONE

Files in `experiments/04_revised_objective/`.

Completed:

- repeated finite-shot searches;
- lower-tail permutation test;
- random-axis search convergence;
- Monte-Carlo frontier study.

### M8 — NISQ-style noise stress test — DONE

File: `experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py`

Noise model:

- local two-qubit depolarization after collisions;
- symmetric readout bit flips.

Across 12 independently hidden-basis worlds, representative mean disagreements were approximately:

- clean: `0.00013`;
- mild `(p2=0.005, q=0.01)`: `0.02951`;
- moderate `(p2=0.01, q=0.02)`: `0.05764`;
- readout-heavy `(p2=0.002, q=0.05)`: `0.09834`;
- stronger combined noise `(p2=0.02, q=0.05)`: `0.12676`, infeasible at `epsilon=0.10`.

Interpretation: finite operating region under this simplified noise model; no noise-immunity claim.

### M9 — Chen et al. (2019) external-architecture benchmark — DONE

File: `experiments/06_chen2019/eiql_chen2019_benchmark.py`

Published record strengths were modeled as:

- A: `(180,180,180,180,180)` degrees;
- B: `(180,180,180,72,100)` degrees.

EIQL extension:

- independently hide each environmental record basis with a local random SU(2);
- do not reveal system labels, pointer variable, or hidden bases;
- learn separate local decoders from environment-only redundancy.

Population benchmark over 12 hidden-basis worlds:

- A ideal learned worst-pair disagreement: `0.00193`, oracle floor `0`;
- B ideal: `0.27689`, oracle floor `0.27487`;
- in B, photons `2,3,4` were selected as the best three-fragment subset in `12/12` population worlds and `10/10` finite-shot worlds.

Caveat: simulation based on the published architecture, not reanalysis of raw laboratory events.

### M10 — Experimental-QD literature mapped to EIQL — DONE

Key experimental motivations reviewed:

- Chen et al. (2019), photonic simulator;
- Saini & Behera, IBM hardware and tomography scaling/noise;
- Zhu et al. (2025), superconducting-circuit QD and inexpensive designed local witnesses;
- Jess Riedel's experimental-QD FAQ as a methodological critique of engineered confirmation experiments.

Current distinction:

- prior QD experiments create/witness/analyze Darwinian records using known models, known pointer structure, designed observables, or tomography;
- EIQL treats the **environmental decoder as unknown and learned from fragment redundancy**.

### M11 — EIQL vs tomography/resource benchmark — DONE IN SIMULATION

File: `experiments/07_resource_benchmark/eiql_vs_tomography_resource_benchmark.py`

This experiment introduced a practical environment-only **pair-moment/spectral decoder estimator**. For equal-prior binary conditionally independent qubit records, the centered Pauli cross-correlation satisfies

```text
C_ij = (1/4) (r_i0 - r_i1) (r_j0 - r_j1)^T,
```

so local decoder directions can be estimated from leading singular/eigen directions, up to free output relabeling. This structural observation must still be checked carefully against prior covariance/spectral measurement-learning literature before being presented as novel.

The environment-only measurement design uses an orthogonal-array Pauli schedule so every fragment pair receives all nine ordered Pauli-basis pairs.

For five environment fragments plus one system qubit:

- EIQL environment-only pair-moment design: `27` settings;
- task-specific S-assisted correlation baseline: `9` settings;
- full six-qubit Pauli QST: `729` settings.

The S-assisted baseline is intentionally stronger and prevents an unfair “EIQL versus only full tomography” comparison.

Equal-total-copy benchmark over 40 independently hidden-basis worlds, at `6912` copies per method:

| Setting | EIQL axis error | S-assisted axis error | EIQL worst D | S-assisted worst D |
|---|---:|---:|---:|---:|
| Chen A strong | 1.63254 deg | 2.32299 deg | 0.000922 | 0.001940 |
| Chen B mixed | 2.07923 deg | 2.65059 deg | 0.275359 | 0.275919 |

For Chen B, the oracle physical worst-pair disagreement floor is approximately `0.274865`.

Readout-noise stress at 256 shots per EIQL setting showed, for example, that the A-strong case at `q=0.05` retained mean axis error `2.055 deg` and observed disagreement `0.09612` against a noise-imposed oracle floor `0.095`.

Independent-fragment null over 60 worlds:

- same-event pair signal mean: `0.99931`;
- independent-fragment null pair signal mean: `0.09082`;
- same-event learned worst disagreement mean: `0.00097`;
- balanced independent-fragment population disagreement: `0.5`.

Interpretation: EIQL can recover hidden environmental decoder directions without direct system access or full-state reconstruction in this model. This does **not** establish universal resource superiority over tomography.

---

## 3. Current claims we can defend

### We can currently claim

- EIQL is a coherent **quantum measurement-learning framework/problem formulation**.
- Its supervision signal is redundancy across independently accessible environmental fragments generated by the same physical event.
- Under explicit SBS assumptions, exact rich agreement identifies pointer information up to admissible coarse-graining/relabeling.
- Near SBS, the current theorem gives an information-theoretic residual-uncertainty guarantee under stated assumptions.
- A fixed finite candidate measurement family admits a conservative finite-shot guarantee.
- The revised simulations test the same richness/disagreement objective used in the theory.
- Published QD architectures provide realistic target experiments for unknown-decoder learning.
- In the binary qubit-record benchmark, environment-only pair moments can recover hidden decoder directions with finite-shot and readout-noise performance close to the corresponding physical disagreement floors.
- The resource benchmark now includes a stronger S-assisted task-specific comparator rather than relying only on full QST.

### We should NOT currently claim

- a new universal learning paradigm;
- quantum advantage;
- unique recovery of a POVM operator;
- a theorem for arbitrary states with no nearby SBS reference;
- hardware superiority over tomography;
- universal sample/settings superiority over task-specific tomography;
- robustness to arbitrary correlated/non-Markovian environments;
- that the Chen/Saini/Zhu laboratory experiments already performed EIQL;
- novelty of the pair-covariance spectral factorization until the dedicated literature check is complete.

---

## 4. Main unresolved weaknesses

1. **Nearby-SBS assumption.** The robust theorem assumes a suitable SBS reference state exists nearby. EIQL does not yet infer approximate broadcast structure directly from operational data.
2. **No actual hardware EIQL run yet.** Current NISQ, external-architecture, and resource results are simulations.
3. **Continuous/adaptive search theory.** The finite-shot theorem covers pre-specified finite candidate sets; adaptive or continuous POVM searches need separate generalization/sample-complexity analysis.
4. **Hardware resource comparison not yet measured.** A simulation comparison now exists, but distinct settings, shots, QPU time, wall-clock time, and noise robustness still need to be measured on the same real device/task.
5. **Correlated fragments.** The clean theorem uses SBS-style conditional independence/product records.
6. **General null ceilings.** The analytic null is currently binary i.i.d. independent-product; an L-ary/non-identically-distributed null ceiling remains open.
7. **External novelty check.** Literature search must continue around common-randomness extraction, quantum sensing/measurement design, unknown-measurement learning, self-supervised QML, unsupervised observable discovery, and covariance/spectral decoder estimation.

---

## 5. What remains

### P0 — Repository/manuscript reproducibility

- [x] organize scripts and summaries;
- [x] record the research track;
- [x] add the simulation resource benchmark and canonical summary tables;
- [ ] remove remaining notebook-history artifacts / unused code from older scripts;
- [ ] add regression tests for exact identities and reported summary values;
- [ ] replace remaining absolute figure paths in the manuscript with repository-relative paths;
- [ ] add a single command/Makefile that regenerates manuscript figures.

### P1 — Real hardware EIQL demonstration — HIGHEST PRIORITY

Target experiment:

1. prepare a small QD/collision circuit on currently available superconducting hardware;
2. use one system qubit and 3–5 environment qubits;
3. apply independently hidden local readout rotations to environment qubits;
4. give the learner only environment outcomes;
5. use a calibrated finite local measurement family or the pair-moment design;
6. learn environmental decoder behavior from redundancy;
7. reveal the engineered pointer/record basis only for evaluation;
8. include permutation/no-collision/scrambled controls.

Success criteria:

- decoder signal significantly exceeds independent/permutation nulls;
- learned decoder behavior is close to the hidden record decoder up to operational equivalence/relabeling;
- signal degrades predictably under weaker records/noise.

### P1 — Hardware EIQL vs tomography/resource measurement

The simulation benchmark is complete. On the same real hardware/state family, still measure:

- distinct measurement settings;
- total shots/copies;
- QPU execution time;
- wall-clock time;
- classical reconstruction/optimization time;
- decoder/pointer recovery quality;
- robustness to readout/gate noise.

The goal is to measure where EIQL is advantageous for the narrower decoder-discovery task, not to assume it is always cheaper.

### P1 — Dedicated novelty/literature check for the moment estimator

- [ ] search covariance/spectral multi-view estimation, quantum measurement learning, quantum sensing, classical shadows, tensor/moment methods, and common-randomness extraction;
- [ ] determine whether the rank-one cross-correlation factorization and orthogonal-array decoder protocol are known under another name;
- [ ] if known, present them as an implementation technique rather than a novelty claim.

### P1 — External expert feedback

- [ ] send the manuscript to at least one Quantum-Darwinism/open-systems expert;
- [ ] send it to one quantum-learning/statistical-learning expert;
- [ ] explicitly ask whether the unknown-decoder-from-redundancy task already exists under another name.

### P2 — Submission tightening

- [ ] update title/rhetoric consistently to “quantum measurement-learning framework”;
- [ ] integrate Chen, Zhu, and Saini–Behera comparisons;
- [ ] integrate the resource benchmark without overclaiming full-QST superiority;
- [ ] emphasize designed-witness versus learned-decoder distinction;
- [ ] keep the Bayes certificate labelled general but potentially loose;
- [ ] move ambitious reverse-direction conjectures to Outlook.

### P3 — Follow-up theory, not required for the first paper

- [ ] SBS-free reverse theorem: observed rich multi-fragment agreement implies approximate latent broadcast/objective-record structure;
- [ ] correlated/non-Markovian fragment theory;
- [ ] continuous POVM learning via covering numbers/PAC-style bounds;
- [ ] adaptive sequential measurement-search guarantees;
- [ ] L-ary/non-identical independent null ceiling;
- [ ] scaling with fragment number and dimension.

---

## 6. Falsification criteria

EIQL should be considered weakened as a useful formulation if one or more of the following occurs:

- prior work is found that already formulates the same unknown-local-decoder problem with redundancy as supervision and comparable guarantees;
- on realistic hardware, the learned decoder cannot be separated from permutation/independent nulls at useful shot budgets;
- decoder learning consistently costs as much as or more than appropriate task-specific tomography with no compensating robustness, access, or interpretability benefit;
- high EIQL scores occur generically in non-Darwinian/independent states beyond the stated null controls;
- learned outputs fail to track pointer information even in regimes satisfying the theorem assumptions.

---

## 7. Reproducibility map

Primary scripts:

```text
experiments/01_blind_pointer/blind_pointer_discovery_full.py
experiments/02_collision_model/collision_model_eiql_experiment.py
experiments/03_general_hamiltonian/eiql_general_hamiltonian_stage.py
experiments/04_revised_objective/eiql_v21_simulation.py
experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py
experiments/06_chen2019/eiql_chen2019_benchmark.py
experiments/07_resource_benchmark/eiql_vs_tomography_resource_benchmark.py
classical_sanity/synthetic_medical/synthetic_medical_eiql_experiment.py
```

Large reproducible raw tables and figures do not need to be canonical repository artifacts when the script regenerates them; compact summary tables are kept.

---

## 8. Current first-paper hierarchy

The intended first paper should stay tight:

1. research question / positioning;
2. EIQL decoder class and objective;
3. exact SBS structural result;
4. robust pointer-information theorem;
5. finite-shot fixed-class proposition;
6. independent null baseline;
7. revised collision-model experiment;
8. NISQ-style noise stress test;
9. Chen external-architecture benchmark;
10. environment-only decoder/resource benchmark;
11. limitations and falsification criteria.

Do not expand the first paper into all possible future theory. The highest-value missing evidence is now **a real hardware unknown-decoder experiment**, plus the dedicated novelty check for the pair-moment estimator.
