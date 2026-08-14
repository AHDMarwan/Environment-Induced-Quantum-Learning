# Experiments

Experiments are ordered historically. Early experiments do not all test the final EIQL objective.

## `01_blind_pointer`
Historical proof of principle using inter-fragment mutual information. Useful for development history, not primary evidence for the final theorem/objective.

## `02_collision_model`
Introduces explicit system-environment collision dynamics rather than pre-built records.

## `03_general_hamiltonian`
Controlled generalized-Hamiltonian stress test. Exploratory and predates the final richness/disagreement objective.

## `04_revised_objective`
Primary theory-matched simulation. Uses `R = min_j H(Z_j)` and `D = max_{i<j} P(Z_i != Z_j)`. Includes the independent-product baseline, finite-shot runs, permutation null, and search-convergence diagnostics.

## `05_noisy_nisq`
Density-matrix stress test with local two-qubit depolarization and symmetric readout flips. Supports a finite operating region, not noise immunity.

## `06_chen2019`
External-architecture benchmark based on the published Chen et al. photonic Quantum-Darwinism interaction settings. Every environment record receives an independently hidden local SU(2) basis, converting the published record architecture into an unknown-decoder task. Includes record-quality/subset discovery and finite-shot diagnostics.

## `07_resource_benchmark`
Environment-only pair-moment/spectral decoder benchmark. Compares EIQL with a stronger system-assisted task-specific correlation estimator at equal copy budget and with full Pauli tomography in distinct measurement-setting count. The comparison is access-model specific and is not a universal tomography-superiority claim.

## Evidence hierarchy for Version 3

1. `04_revised_objective` - direct theory/objective consistency;
2. `06_chen2019` - published external-architecture unknown-decoder benchmark;
3. `07_resource_benchmark` - practical decoder implementation and resource comparison;
4. `05_noisy_nisq` - robustness under a simple local hardware-noise model;
5. `01`-`03` - historical development / exploratory stress tests.

Version 3 contains no real-hardware EIQL run. Hardware validation is future work, not a requirement for the first-paper scope.
