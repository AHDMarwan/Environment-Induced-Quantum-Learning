# EIQL Research Track

**Last updated:** 2026-08-14  
**Status:** active working theory + simulation project; not peer reviewed.  
**Current framing:** EIQL is a *quantum measurement-learning framework/problem formulation*, not a claim of a new universal machine-learning paradigm.

## 1. Current research question

Given repeated access to environmental quantum fragments \(E_1,\ldots,E_m\), with no access required to the system \(S\), no class labels, and no known pointer/readout basis, learn local decoders/POVMs whose outputs are:

1. rich enough to carry non-trivial information; and
2. redundantly consistent across independently accessible fragments.

Current objective:

\[
D_\rho(\mathbf M)=\max_{i<j}P_\rho(Z_i\neq Z_j),
\qquad
R_\rho(\mathbf M)=\min_j H_\rho(Z_j),
\]

and

\[
\mathcal O^{\mathfrak M}_{\varepsilon,L}(\rho)
=\sup_{\mathbf M\in\mathfrak M^{(L)}}R_\rho(\mathbf M)
\quad\text{s.t.}\quad D_\rho(\mathbf M)\le\varepsilon.
\]

Fragmentwise output permutations are free classical post-processing. The theory identifies **pointer information / decoder behavior on the relevant record states**, not a unique POVM operator on the entire Hilbert space.

---

## 2. What has been completed

### M0 — Concept formation and literature positioning — DONE

The project began from the Quantum-Darwinism / environment-as-witness idea: physics itself can redundantly proliferate selected classical records into the environment. The EIQL question was separated from the established QD question:

- QD: which information becomes redundant/objective?
- EIQL: if the correct environmental decoder is unknown, can it be *learned from redundancy itself*?

Current novelty claim is deliberately narrow: **unknown local measurement/decoder learning from same-event environmental redundancy**.

### M1 — Blind pointer discovery toy model — DONE

File: `experiments/01_blind_pointer/blind_pointer_discovery_full.py`

Setup:
- binary hidden pointer variable;
- multiple conditionally independent quantum records;
- hidden random readout basis;
- learner initially used inter-fragment mutual information as a discovery signal.

Main observations:
- perfect broadcast case recovered the optimal record measurement;
- finite-shot search remained close to the optimal decoder;
- shuffling fragments across physical events destroyed the learned redundancy signal;
- partial/noisy records degraded smoothly.

This experiment motivated the framework but is no longer the primary evidence because the original MI objective differs from the final EIQL objective.

### M2 — Explicit collision dynamics — DONE

File: `experiments/02_collision_model/collision_model_eiql_experiment.py`

Moved from pre-built broadcast records to explicit sequential system-environment interactions.

Observed chain:

\[
H_{SE}\to\text{decoherence/einselection}\to\text{environmental records}\to\text{blind decoder discovery}.
\]

Controls with system drift / scrambled coupling directions reduced redundant recoverability, while stable pointer dynamics supported strong record discovery.

### M3 — Unknown/generalized Hamiltonian stress test — DONE

File: `experiments/03_general_hamiltonian/eiql_general_hamiltonian_stage.py`

Used interaction families

\[
H_{\rm int}=\sum_{a,b=x,y,z}J_{ab}\sigma_a\otimes\sigma_b
\]

with increasingly competing system coupling directions. The learner saw environment data only. The learned redundancy score tracked the amount of approximate pointer structure in the hidden interaction family; strongly multi-axis/scrambled regimes lost the signal.

Important limitation: the Hamiltonian ensemble was controlled rather than an unbiased theorem-level characterization of arbitrary Hamiltonians.

### M4 — Classical sanity checks — DONE / AUXILIARY ONLY

Files:
- `classical_sanity/iris/`
- `classical_sanity/synthetic_medical/`

Purpose: test whether the inductive bias “prefer information supported across multiple independent views” has a sensible classical analogue.

The multimodal synthetic medical benchmark used Blood/MRI/ECG views with an MRI-only shortcut that was reversed at test time. The shared-redundancy representation was more robust than shortcut-prone baselines, but this is **not quantum evidence** and not a quantum-advantage result.

### M5 — Theory V1 → V2 → V2.1 repair cycle — DONE

Current paper source: `paper/EIQL_Submission_Draft.tex`

Major repaired issues:
- output-alphabet qualification in the exact SBS result;
- corrected robust proof using a global error indicator rather than invalid pointwise monotonicity;
- replacement of average disagreement by worst-pair disagreement;
- replacement of one-fragment entropy by minimum fragment entropy;
- explicit fragmentwise output relabelings;
- operational equivalence of decoders on the occupied record states;
- distinction between pointer-information identifiability and physical POVM uniqueness;
- non-vacuity condition when \(H(X)>\log_2L\);
- finite-shot guarantee restricted to pre-specified finite measurement classes;
- correct lower-tail permutation statistic;
- Monte-Carlo frontier correctly labelled as an approximation;
- analytic independent-product baseline;
- explicit Bayes recovery certificate.

Current theoretical components:
1. exact SBS pointer-information structural theorem;
2. robust theorem near an SBS reference state;
3. Bayes-recovery corollary (explicit but generally loose);
4. finite-class finite-shot proposition;
5. independent-product null lemma.

**Important:** positive informal referee-style reviews in the project notes are not peer review and must not be represented as such.

### M6 — Revised EIQL simulation matching the formal objective — DONE

File: `experiments/04_revised_objective/eiql_v21_simulation.py`

System: one system qubit + four environmental qubits.

Learner objective matches the theory:
- maximize minimum fragment entropy;
- constrain worst-pair disagreement;
- lexicographic tie-break by lower disagreement among near-max-richness solutions.

Key results:
- stable perfect dynamics produced near-one-bit richness with near-zero worst-pair disagreement;
- shuffled/permutation null produced disagreement near 0.5;
- no-collision independent records lie on the analytic baseline rather than the Darwinian high-richness/low-disagreement region;
- scrambled dynamics often became infeasible at stringent \(\varepsilon\).

Analytic independent binary baseline:

\[
R_{\rm ind}(\varepsilon)=h_2\!\left(\frac{1-\sqrt{1-2\varepsilon}}{2}\right).
\]

This graph is currently one of the clearest pedagogical summaries of EIQL.

### M7 — Finite-shot and search-convergence diagnostics — DONE

Files in `experiments/04_revised_objective/`.

Completed:
- finite-shot repeated runs;
- lower-tail permutation test;
- random-axis search convergence study;
- Monte-Carlo frontier rather than falsely claiming an exact continuous optimum.

### M8 — NISQ-style noise stress test — DONE

File: `experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py`

Noise model:
- local two-qubit depolarization after collisions;
- symmetric readout bit flips.

Across 12 independently hidden-basis worlds:
- clean: disagreement ≈ 0.00013;
- mild \((p_2=0.005,q=0.01)\): ≈ 0.0295;
- moderate \((p_2=0.01,q=0.02)\): ≈ 0.0576;
- readout-heavy \((p_2=0.002,q=0.05)\): ≈ 0.0983, still feasible at \(\varepsilon=0.10\);
- stronger combined noise \((p_2=0.02,q=0.05)\): ≈ 0.1268, correctly becoming infeasible.

Interpretation: EIQL has a finite operating region under this simple NISQ noise model; it is not noise-immune.

### M9 — Benchmark based on Chen et al. (2019) photonic QD architecture — DONE

File: `experiments/06_chen2019/eiql_chen2019_benchmark.py`

This is currently the strongest external-architecture simulation.

Published interaction settings were modeled as:
- A: five strong records \((180^\circ,180^\circ,180^\circ,180^\circ,180^\circ)\);
- B: three strong + two weak records \((180^\circ,180^\circ,180^\circ,72^\circ,100^\circ)\).

EIQL extension:
- independently hide each environmental record basis with a local random SU(2);
- do not reveal system labels, pointer variable, or hidden bases;
- learn separate local decoders from environment-only redundancy.

Multi-start population results over 12 independently hidden-basis worlds:
- A ideal learned worst-pair disagreement: **0.00193** (oracle physical floor 0);
- B ideal: **0.27689**, close to oracle physical floor **0.27487**;
- fidelity-matched isotropic-noise proxies remain close to their corresponding physical floors.

Record-quality discovery:
- in B, the best three-fragment subset was photons **2,3,4** in **12/12** population hidden-basis worlds;
- in a finite-shot statistic-search benchmark, the same subset was selected in **10/10** worlds.

This demonstrates a stronger behavior than merely recovering one basis: EIQL can identify which environmental fragments carry reliable records.

Caveat: this is a simulation based on the published architecture, not a reanalysis of raw laboratory events. The added independent hidden SU(2) rotations define the EIQL unknown-decoder task and are not part of the original experiment.

### M10 — Experimental-QD papers mapped to EIQL — DONE

Key experimental motivations reviewed:
- Chen et al. (2019), photonic simulator;
- Saini & Behera (2020/2021 preprint), IBM hardware and tomography scaling/noise;
- Zhu et al. (2025), superconducting-circuit observation of QD and inexpensive designed local witnesses;
- Jess Riedel's experimental-QD FAQ as a methodological critique of overly engineered confirmation experiments.

Current distinction:
- these works create/witness/analyze Darwinian records using known models, known pointer structure, designed observables, or tomography;
- EIQL treats the **environmental decoder as unknown and learned from fragment agreement**.

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

### We should NOT currently claim

- a new universal learning paradigm;
- quantum advantage;
- unique recovery of a POVM operator;
- a theorem for arbitrary states with no nearby SBS reference;
- hardware superiority over tomography without a direct resource benchmark;
- robustness to arbitrary correlated/non-Markovian environments;
- that the Chen/Saini/Zhu laboratory experiments already performed EIQL.

---

## 4. Main unresolved weaknesses

1. **Nearby-SBS assumption.** The robust theorem assumes a suitable SBS reference state exists nearby. EIQL does not yet infer the existence of an approximate broadcast structure directly from operational data.
2. **No actual hardware EIQL run yet.** Current NISQ and published-architecture results are simulations.
3. **Continuous/adaptive search theory.** Finite-shot theorem covers pre-specified finite candidate sets. Adaptive Bayesian/gradient/continuous POVM searches need separate generalization/sample-complexity analysis.
4. **Resource comparison not yet measured.** We have motivation that QST scales as \(3^n\) settings in common Pauli tomography, but no direct apples-to-apples EIQL vs tomography copy/settings benchmark on the same task.
5. **Correlated fragments.** Current clean theorem uses SBS-style conditional independence/product records.
6. **General null ceilings.** Analytic null is currently binary i.i.d. independent-product; an \(L\)-ary and non-identically-distributed independent null ceiling remains open.
7. **External novelty check.** Literature search should continue around common-randomness extraction, quantum sensing/measurement design, unknown-measurement learning, self-supervised QML, and unsupervised observable discovery.

---

## 5. What we should do next

### P0 — Make the repository/manuscript reproducible

- [x] organize scripts, summaries, and current manuscript;
- [x] record the research track;
- [ ] remove remaining notebook-history artifacts / unused code from scripts;
- [ ] add lightweight regression tests for exact identities and reported summary values;
- [ ] replace absolute figure paths in the manuscript with repository-relative paths;
- [ ] add a single command/Makefile that regenerates all manuscript figures.

### P1 — Real hardware EIQL demonstration — HIGHEST PRIORITY

Target experiment:

1. prepare a small QD/collision circuit on currently available superconducting hardware;
2. use one system qubit and 3–5 environment qubits;
3. apply independent hidden local readout rotations to the environment qubits;
4. give the learner only environment outcomes;
5. search a calibrated finite local measurement family;
6. optimize EIQL richness under worst-pair disagreement;
7. reveal the engineered pointer/record basis only for evaluation;
8. run permutation/no-collision/scrambled controls.

Success criteria:
- learned decoder significantly beats the independent/permutation null;
- recovered decoder behavior is close to the hidden record decoder up to operational equivalence/relabeling;
- signal degrades predictably under weaker records/noise.

### P1 — Direct EIQL vs tomography resource benchmark

On the same hardware/state family measure:
- number of distinct measurement settings;
- total shots/copies;
- wall-clock execution time;
- reconstruction/optimization compute time;
- decoder/pointer recovery quality;
- robustness to readout/gate noise.

The goal is not to assume EIQL is cheaper, but to determine when it is cheaper for the narrower task of decoder discovery.

### P1 — External expert feedback

- [ ] send the current manuscript to at least one Quantum-Darwinism/open-systems expert;
- [ ] send to one quantum-learning/statistical-learning expert;
- [ ] specifically ask whether the unknown-decoder-from-redundancy problem already exists under another name.

### P2 — Submission tightening

- [ ] update title/rhetoric consistently to “quantum measurement-learning framework”;
- [ ] add explicit comparison to Zhu et al. (2025), Chen et al. (2019), and Saini–Behera;
- [ ] emphasize designed-witness vs learned-decoder distinction;
- [ ] keep Bayes error certificate labelled as general but potentially loose;
- [ ] move ambitious reverse-direction conjectures to Outlook.

### P3 — Follow-up theory, not required for the first paper

- [ ] **SBS-free reverse theorem:** observed rich multi-fragment agreement ⇒ approximate latent broadcast/objective-record structure;
- [ ] correlated/non-Markovian fragment theory;
- [ ] continuous POVM learning via covering numbers/PAC-style bounds;
- [ ] adaptive sequential measurement-search guarantees;
- [ ] \(L\)-ary/non-identical independent null ceiling;
- [ ] scaling with fragment number/dimension.

---

## 6. Falsification criteria

EIQL should be considered weakened or falsified as a useful formulation if one or more of the following occurs:

- a classical/quantum prior work is found that already formulates the same unknown-local-decoder problem with redundancy as supervision and comparable guarantees;
- on realistic hardware, the learned decoder cannot be separated from permutation/independent nulls at useful shot budgets;
- decoder search consistently costs as much as or more than full tomography for the target task, with no compensating robustness/interpretability benefit;
- high EIQL scores occur generically in non-Darwinian states/independent records beyond the analytic/null controls;
- the learned output fails to track the intended pointer information even in regimes satisfying the theorem assumptions.

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
classical_sanity/synthetic_medical/synthetic_medical_eiql_experiment.py
```

The raw generated synthetic medical tables are deliberately not committed because they are large and reproducible. Summary tables are kept.

---

## 8. Current paper hierarchy

The intended first paper should stay tight:

1. research question / positioning;
2. EIQL decoder class and objective;
3. exact SBS structural lemma;
4. robust pointer-information theorem;
5. finite-shot fixed-class proposition;
6. independent null baseline;
7. revised collision-model experiment;
8. noisy-NISQ stress test;
9. external-architecture benchmark / hardware proposal;
10. limitations and falsification criteria.

Do not expand the first paper into all possible future theory. The highest-value missing evidence is now **a real hardware unknown-decoder experiment**.
