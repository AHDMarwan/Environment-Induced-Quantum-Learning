# Canonical numerical results

This file records the headline numbers produced during the current EIQL development cycle. They are simulation results unless explicitly stated otherwise. They are not experimental hardware results and are not evidence of quantum advantage.

## 1. Revised EIQL objective — 5-qubit collision model

Objective:

- richness: `min_j H(Z_j)`
- disagreement: `max_{i<j} P(Z_i != Z_j)`

At `epsilon = 0.10`, 20 finite-shot searches per case:

| Case | Feasible rate | Mean min entropy | Mean max disagreement | Mean axis error |
|---|---:|---:|---:|---:|
| stable-perfect | 1.00 | 1.0000 bit | 0.00194 | 3.30 deg |
| drift-15deg | 1.00 | 1.0000 bit | 0.04732 | 7.16 deg |
| no-collision | 1.00 | 0.2521 bit | 0.08089 | 23.69 deg |
| stable-partial | 0.00 | — | — | — |
| scrambled-system | 0.00 | — | — | — |

Permutation control for a stable-perfect learned decoder:

- observed max disagreement: `0.0026667`
- null mean: `0.511554`
- null SD: `0.005971`
- lower-tail permutation count: `0/1000`
- corrected Monte-Carlo p-value: `1/1001 = 0.000999`

The no-collision independent binary reference is captured analytically by

`R_ind(epsilon) = h2((1 - sqrt(1 - 2 epsilon))/2)`.

## 2. NISQ-style noise stress test

Twelve independently hidden-basis worlds per representative setting:

| Setting | two-qubit depolarization p2 | readout flip q | Feasible fraction | Mean disagreement | Mean axis error |
|---|---:|---:|---:|---:|---:|
| clean | 0 | 0 | 1.0 | 0.000130 | 0.82 deg |
| mild | 0.005 | 0.01 | 1.0 | 0.02951 | 0.96 deg |
| moderate | 0.01 | 0.02 | 1.0 | 0.05764 | 1.28 deg |
| readout-heavy | 0.002 | 0.05 | 1.0 | 0.09834 | 0.90 deg |
| beyond-eps | 0.02 | 0.05 | 0.0 | 0.12676 | — |

Interpretation: under this simplified noise model EIQL has a finite operating region; it is not noise-immune.

## 3. Generalized/unknown Hamiltonian stress test

A controlled interaction family was constructed with increasingly competing coupling directions. The learner used environmental statistics only.

Validated 25th-percentile inter-fragment redundancy score:

| competition parameter eps | pointer fraction | validated q25 redundancy (bits) |
|---:|---:|---:|
| 0.0 | 1.0000 | 0.96276 |
| 0.1 | 0.9853 | 0.77446 |
| 0.2 | 0.9438 | 0.53302 |
| 0.4 | 0.8075 | 0.13090 |
| 0.7 | 0.5780 | 0.00660 |
| 1.0 | 0.4016 | 0.000298 |

This was an earlier MI-based exploration and is retained as a stress-test history, not as direct evidence for the final consensus-richness theorem.

## 4. Chen et al. (2019) architecture benchmark

Published record strengths were modeled as:

- setting A: `(180, 180, 180, 180, 180)` degrees
- setting B: `(180, 180, 180, 72, 100)` degrees

EIQL addition: every environment fragment was independently hidden by a local random SU(2), and the learner was not given the system label, pointer value, or decoder basis.

### Multi-start population benchmark — 12 independently hidden-basis worlds

| Setting | Mean min entropy | Learned worst-pair disagreement | Mean axis error |
|---|---:|---:|---:|
| A ideal | 1.0000 | 0.001930 | 2.44 deg |
| B ideal | 0.99910 | 0.276892 | 18.54 deg |
| A fidelity proxy | 1.0000 | 0.079873 | 4.79 deg |
| B fidelity proxy | 0.99915 | 0.356235 | 21.56 deg |

Oracle physical disagreement floors used only for post-training evaluation:

- A ideal: approximately `0`
- B ideal: approximately `0.274865`
- A fidelity proxy: approximately `0.071619`
- B fidelity proxy: approximately `0.342792`

### Fragment-quality discovery

In setting B, EIQL was asked to rank all three-environment-fragment subsets.

- best subset in population search: photons `2,3,4` in `12/12` hidden-basis worlds
- best subset in finite-shot statistic search at 700 shots/statistic: photons `2,3,4` in `10/10` worlds

These are exactly the three perfect records in the published interaction setting. The learner was not given that fact during optimization.

### Finite-shot search

At 700 shots per estimated statistic:

- A ideal: mean validated disagreement `0.01791`
- B ideal: mean validated disagreement `0.28420`

## 5. EIQL vs tomography/resource benchmark

File: `experiments/07_resource_benchmark/eiql_vs_tomography_resource_benchmark.py`

This benchmark uses the same hidden-decoder record family but replaces brute-force decoder search with an environment-only pair-moment/spectral estimator. It compares EIQL with a deliberately stronger task-specific baseline that has direct access to the system qubit, while full Pauli QST is used separately for settings-scaling context.

### Equal-total-copy comparison — 40 hidden-basis worlds

At 6912 total copies per method:

| Setting | EIQL axis error | S-assisted axis error | EIQL worst disagreement | S-assisted worst disagreement |
|---|---:|---:|---:|---:|
| Chen A strong | 1.63254 deg | 2.32299 deg | 0.000922 | 0.001940 |
| Chen B mixed | 2.07923 deg | 2.65059 deg | 0.275359 | 0.275919 |

For Chen B, the oracle physical worst-pair disagreement floor is approximately `0.274865`.

### Readout-noise stress — 256 shots per EIQL setting, 30 worlds

| Setting | readout q | Mean axis error | Mean observed D | Oracle observed floor |
|---|---:|---:|---:|---:|
| A strong | 0.00 | 1.60817 deg | 0.000920 | 0.000000 |
| A strong | 0.02 | 1.94140 deg | 0.040383 | 0.039200 |
| A strong | 0.05 | 2.05516 deg | 0.096124 | 0.095000 |
| B mixed | 0.00 | 2.13605 deg | 0.275533 | 0.274865 |
| B mixed | 0.02 | 2.33334 deg | 0.293201 | 0.292516 |
| B mixed | 0.05 | 2.68128 deg | 0.318352 | 0.317641 |

### Independent-fragment null — 60 worlds

- same-event pair signal mean: `0.99931`
- independent-fragment null pair signal mean: `0.09082`
- same-event learned worst disagreement mean: `0.00097`
- balanced independent-fragment population disagreement: `0.5`

### Measurement-setting scaling

For five environment fragments plus one system qubit:

- EIQL environment-only pair-moment design: `27` settings
- task-specific S-assisted pair tomography: `9` settings
- full six-qubit Pauli QST: `729` settings

The important caveat is that EIQL is **not** claimed to beat every tomography strategy. The stronger 9-setting S-assisted baseline shows that full QST is not the fairest comparator for this narrow task. The current result supports recovery without direct system access or full-state reconstruction, not universal resource superiority.

## 6. Classical multiview sanity check — synthetic medical data

Auxiliary only; this is not quantum evidence.

Twelve independently generated Blood/MRI/ECG worlds with a train-time MRI shortcut reversed at test time:

| Method | IID accuracy | shifted accuracy | mean drop |
|---|---:|---:|---:|
| EIQL-inspired shared representation | 0.97146 | 0.96403 | 0.00743 |
| Concat PCA | 0.98285 | 0.96292 | 0.01993 |
| MRI PCA | 0.98326 | 0.93278 | 0.05049 |
| raw supervised logistic | 0.98451 | 0.91181 | 0.07271 |

EIQL-inspired shifted accuracy with MRI removed at test time: `0.953125`.

The point of this experiment was robustness of a shared-information inductive bias, not superiority over classical multiview methods.

## 7. Iris sanity check

Across 100 stratified train/test splits:

- EIQL-inspired shared latent 1D: `0.7992 ± 0.0516`
- EIQL-inspired shared latent 2D: `0.8296 ± 0.0413`
- KMeans on all four features: `0.8260 ± 0.0412`
- supervised logistic regression reference: `0.9562 ± 0.0244`

Again, this is a classical sanity check only.
