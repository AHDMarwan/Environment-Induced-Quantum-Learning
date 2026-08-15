# Hardware-informed numerical suite

This suite strengthens the operational/numerical evidence for the current EIQL manuscript without claiming access to real quantum hardware. Every benchmark is finite-shot and produces CSV tables plus a publication-ready PNG figure.

## 09 — Finite-shot Theorem 2 benchmark

`09_finite_shot_theorem2/theorem2_finite_shot.py`

Uses same-event randomized one-qubit Pauli classical-shadow snapshots. It estimates the connected two-fragment operator from paired physical events and compares empirical Hilbert–Schmidt decoder-direction error with the explicit finite-shot bound. The conservative region in which `e_N >= lambda` is recorded as a vacuous bound rather than hidden by clipping.

## 10 — Conditional-correlation model mismatch

`10_conditional_correlation/conditional_correlation_stress.py`

Introduces a controlled traceless two-fragment correlation term that preserves local conditional marginals while violating conditional independence. The sweep reports conditional mutual information, population direction error, the Pinsker/Wedin robustness bound, and finite-shot Pauli-shadow recovery.

## 11 — Multiclass two-view ambiguity versus third-view recovery

`11_multiclass_views/multiclass_two_vs_three.py`

Starts from the exact three-class commuting counterexample in Appendix B: two distinct latent decompositions produce the same two-view distribution but different local MAP decoders. A generic third view is appended and a finite-shot spectral three-view reconstruction is used to recover the decoder up to latent permutation.

## 12 — End-to-end virtual collision experiment

`12_collision_virtual/collision_phase_diagram.py`

A system pointer controls single-qubit collision rotations into five environment ancillas. Each local record is hidden by an independent unknown SU(2) basis. The learner receives only finite-shot Pauli outcomes from a 27-setting orthogonal-array schedule with 2% readout flips. The output is an empirical recovery phase diagram versus collision strength and shot budget.

## GitHub Actions

`.github/workflows/hardware-informed-experiments.yml` runs the four benchmarks independently and uploads each experiment's `outputs/` directory as a workflow artifact. The workflow runs on pull requests touching the suite, on pushes to `main` or the development branch, and can also be started manually with `workflow_dispatch`.

These are hardware-informed numerical experiments, not device-calibrated simulations or hardware demonstrations.
