# Experiments

Experiments are ordered historically. Early experiments do not all test the final EIQL identifiability claims.

## `01_blind_pointer`
Historical proof of principle using inter-fragment mutual information. Useful for development history, not primary evidence for the final theorem/objective.

## `02_collision_model`
Introduces explicit system-environment collision dynamics rather than pre-built records.

## `03_general_hamiltonian`
Controlled generalized-Hamiltonian stress test. Exploratory and predates the final richness/disagreement objective.

## `04_revised_objective`
Primary simulation for the earlier agreement-richness EIQL objective. Uses `R = min_j H(Z_j)` and `D = max_{i<j} P(Z_i != Z_j)`. Includes the independent-product baseline, finite-shot runs, permutation null, and search-convergence diagnostics.

## `05_noisy_nisq`
Density-matrix stress test with local two-qubit depolarization and symmetric readout flips. Supports a finite operating region, not noise immunity.

## `06_chen2019`
External-architecture benchmark based on the published Chen et al. photonic Quantum-Darwinism interaction settings. Every environment record receives an independently hidden local SU(2) basis, converting the published record architecture into an unknown-decoder task. Includes record-quality/subset discovery and finite-shot diagnostics.

## `07_resource_benchmark`
Environment-only pair-moment/spectral decoder benchmark. Compares EIQL with a stronger system-assisted task-specific correlation estimator at equal copy budget and with full Pauli tomography in distinct measurement-setting count. The comparison is access-model specific and is not a universal tomography-superiority claim.

## `08_correlated_nuisance`
Negative control for the earlier agreement-richness objective. A perfectly redundant nuisance record can dominate a system-linked record, demonstrating why passive agreement/richness does not self-certify system semantics.

## `09_finite_shot_theorem2`
Theory-matched finite-shot benchmark for the current identifiability paper. Uses same-event randomized local Pauli-shadow snapshots to estimate the binary connected two-fragment operator. The tightened analysis fits the empirical log-log scaling and tests the contrast-rescaled quantity `c^2 sqrt(N) sin(angle)` while keeping the explicit theorem bound separate as a conservative worst-case guarantee.

## `10_conditional_correlation`
Controlled model-mismatch benchmark for residual conditional inter-fragment correlations. A traceless bipartite perturbation preserves both local conditional marginals while increasing `I(E_i:E_j|X)`. Population and finite-shot decoder-direction errors are compared with the square-root conditional-mutual-information structure entering the Pinsker/Wedin robustness analysis.

## `11_multiclass_views`
Finite-shot realization of the current paper's multiclass view hierarchy. The exact Appendix-B two-view counterexample is paired with a representative well-conditioned third view. The spectral reconstruction uses observable moments only; oracle permutation matching is isolated after recovery and is used strictly for evaluation.

## `12_collision_virtual`
End-to-end hardware-informed virtual experiment for the current paper. A six-qubit global state is generated from explicit sequential controlled-`R_y` system-environment collisions. Each of five environment fragments receives an independently hidden local `SU(2)` basis. EIQL then uses finite environment-only Pauli counts from a 27-setting orthogonal-array schedule with symmetric readout flips. The primary metric requires **all five** recovered decoder axes to lie within 5 degrees of their oracle Helstrom directions.

## Evidence hierarchy for the current identifiability manuscript

The most direct numerical evidence for the current manuscript is:

1. `11_multiclass_views` — exact two-view nonidentifiability and finite-shot third-view recovery;
2. `09_finite_shot_theorem2` — direct finite-shot scaling of the binary connected-operator decoder;
3. `10_conditional_correlation` — controlled robustness test beyond conditional independence;
4. `12_collision_virtual` — explicit microscopic collision dynamics with hidden local bases, finite measurement budgets, and readout noise;
5. `06_chen2019` — externally motivated published Quantum-Darwinism architecture with hidden local readouts;
6. `07_resource_benchmark` — environment-only implementation and access/resource tradeoff;
7. `05_noisy_nisq` and `08_correlated_nuisance` — robustness/negative controls;
8. `01`-`04` — development history and evidence for earlier EIQL formulations.

The repository contains no real-hardware EIQL run. Hardware validation remains future work. The new suite is best described as **theory-matched, finite-shot, hardware-informed simulation evidence**, not experimental hardware validation.
