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

## Evidence hierarchy

For current manuscript claims, weight the experiments approximately as follows:

1. `04_revised_objective` — direct theory/objective consistency;
2. `05_noisy_nisq` — robustness under a simple hardware-noise model;
3. `06_chen2019` — external published-architecture benchmark;
4. `01`–`03` — historical development / stress-test context.

None of these is yet a real EIQL hardware run.
