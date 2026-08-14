# Experiments

The experiments are ordered historically. Not every early experiment tests the final EIQL objective.

## `01_blind_pointer`
First proof-of-principle. A hidden pointer basis was recovered by maximizing inter-fragment mutual information. Useful historically, but the MI objective is **not** the final formal EIQL objective.

## `02_collision_model`
Introduces explicit system-environment collision dynamics rather than pre-built broadcast records. Demonstrates the chain from interaction dynamics to decoherence/records to blind decoder discovery.

## `03_general_hamiltonian`
Controlled generalized Hamiltonian stress test. Explores how environment-only learnability degrades as the interaction loses a dominant pointer direction. Retained as exploratory evidence; it also predates the final richness/disagreement objective.

## `04_revised_objective`
Primary theory-matched simulation. Uses

- `R = min_j H(Z_j)`
- `D = max_{i<j} P(Z_i != Z_j)`

and optimizes richness under a disagreement tolerance. Includes independent-product baseline, finite-shot runs, permutation null, and search-convergence diagnostics.

## `05_noisy_nisq`
Density-matrix NISQ-style stress test with local two-qubit depolarization and symmetric readout bit flips. Used to establish a finite operating region rather than claim noise immunity.

## `06_chen2019`
External-architecture benchmark based on the published Chen et al. photonic Quantum-Darwinism interaction settings. Each environment fragment receives an independently hidden local SU(2) basis, turning the published record architecture into an unknown-decoder learning task. Includes multi-start population search, fragment-quality ranking, a fidelity-matched isotropic-noise proxy, and finite-shot statistic search.

## `07_resource_benchmark`
Environment-only EIQL versus tomography/resource baselines on the hidden-decoder task. Introduces a pairwise Pauli-moment/spectral decoder estimator and an orthogonal-array measurement schedule. Compares EIQL with a stronger task-specific baseline that has direct access to the system qubit, and separately reports full Pauli-QST setting scaling. Includes equal-copy, readout-noise, independent-fragment-null, and measurement-setting-scaling results.

Important caveat: this benchmark is still simulation. It supports decoder recovery without direct system access or full-state reconstruction; it does not establish universal resource superiority over tomography.

## Evidence hierarchy

For current manuscript claims, weight the experiments approximately as follows:

1. `04_revised_objective` — direct theory/objective consistency;
2. `06_chen2019` — external published-architecture benchmark;
3. `07_resource_benchmark` — task-specific decoder/resource benchmark and practical moment estimator;
4. `05_noisy_nisq` — robustness under a simple hardware-noise model;
5. `01`–`03` — historical development / stress-test context.

None of these is yet a real EIQL hardware run.
