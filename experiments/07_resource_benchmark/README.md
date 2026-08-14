# EIQL vs tomography/resource benchmark

This experiment compares an **environment-only EIQL decoder estimator** with two tomography references on the same hidden-decoder task:

- a task-specific **system-assisted correlation baseline** with direct access to the system qubit S;
- full Pauli quantum-state tomography (QST), used only for measurement-setting scaling.

The benchmark is based on Chen-like binary environmental records with independently hidden local SU(2) bases. The learner is not given the hidden pointer value or decoder basis.

## Core estimator

For binary conditionally independent qubit records with equal hidden-branch prior, the centered Pauli cross-correlation matrix between fragments i and j factorizes as

```text
C_ij = (1/4) (r_i0 - r_i1) (r_j0 - r_j1)^T.
```

Hence each local record direction can be estimated from the leading eigendirection/singular direction of pairwise environmental correlations, up to the free output sign/relabeling. The script aggregates these pairwise moments across all fragments.

This factorization should be treated as a task-specific structural observation until its novelty relative to existing covariance/spectral measurement-learning methods is checked thoroughly.

## Measurement schedule

EIQL uses an orthogonal-array Pauli schedule. Every pair of fragments sees all 9 ordered Pauli-basis pairs equally often.

For five environment fragments:

- EIQL environment-only pair-moment design: **27 distinct settings**;
- task-specific S-assisted pair tomography: **9 distinct settings**;
- full six-qubit Pauli QST: **729 distinct settings**.

The 9-setting S-assisted baseline is deliberately included so the resource claim is not overstated: EIQL avoids direct S access and full-state reconstruction, but it is not automatically cheaper than every task-specific tomography strategy.

## Equal-total-copy benchmark

Forty independently hidden-basis worlds were simulated for each copy budget. At 6912 total copies:

| Setting | EIQL axis error | S-assisted axis error | EIQL worst D | S-assisted worst D |
|---|---:|---:|---:|---:|
| Chen A, strong records | 1.63 deg | 2.32 deg | 0.00092 | 0.00194 |
| Chen B, mixed records | 2.08 deg | 2.65 deg | 0.27536 | 0.27592 |

For Chen B the oracle physical worst-pair disagreement floor is approximately 0.27487, so both approaches approach the record-quality limit.

## Readout-noise stress

At 256 shots per EIQL setting over 30 hidden-basis worlds:

| Setting | readout q | EIQL axis error | observed D | oracle observed floor |
|---|---:|---:|---:|---:|
| A strong | 0.00 | 1.61 deg | 0.00092 | 0.00000 |
| A strong | 0.02 | 1.94 deg | 0.04038 | 0.03920 |
| A strong | 0.05 | 2.06 deg | 0.09612 | 0.09500 |
| B mixed | 0.00 | 2.14 deg | 0.27553 | 0.27487 |
| B mixed | 0.05 | 2.68 deg | 0.31835 | 0.31764 |

## Independent-fragment null

At 256 shots/setting over 60 worlds:

- same-event record pair signal: approximately **0.9993**;
- independent-fragment null pair signal: approximately **0.0908**;
- learned same-event worst disagreement: approximately **0.0010**;
- balanced independent-fragment population disagreement: **0.5**.

## Committed files

- `eiql_vs_tomography_resource_benchmark.py` — standalone benchmark script; rerunning it regenerates raw run tables and both figures
- `eiql_vs_tomography_summary.csv` — equal-copy canonical summary
- `eiql_vs_tomography_noise_summary.csv` — readout-noise canonical summary
- `eiql_vs_tomography_null.csv` — null-control runs
- `eiql_vs_tomography_scaling.csv` — measurement-setting scaling table

The larger raw run tables and PNG figures are reproducible outputs of the script and are intentionally not required as canonical repository artifacts.

## Interpretation limits

This is a simulation, not a hardware result. Full QST is not the fairest possible baseline for the narrow decoder-identification task, so the repository reports the stronger 9-setting S-assisted baseline as well. The result supports the claim that EIQL can recover hidden environmental decoder directions without direct system access or full state reconstruction; it does **not** establish quantum advantage or universal resource superiority over tomography.
