# Environment-Induced Quantum Learning (EIQL)

EIQL is a **quantum measurement-learning framework** for self-supervised discovery of local decoders from redundant quantum environmental records.

The central question is:

> Given repeated access to quantum environment fragments, with no pointer labels and no prescribed readout basis, can a learner discover physically implementable local measurements whose outputs are simultaneously informative and mutually consistent?

For fragment outputs \(Z_1,\ldots,Z_m\), the current objective uses

- worst-pair disagreement: \(D=\max_{i<j}P(Z_i\neq Z_j)\);
- redundant richness: \(R=\min_j H(Z_j)\).

The learner maximizes \(R\) subject to \(D\le\varepsilon\), with fragmentwise output relabelings treated as free classical post-processing.

## Current status: Version 3 frozen scope

The first-paper scope is now **theory + simulation**. A real-hardware experiment is useful future validation but is not required for the claims in Version 3.

Current theory includes an exact SBS pointer-information structural theorem, a robust theorem near SBS, a simple Bayes-recovery certificate, a finite-shot guarantee for a pre-specified finite decoder class, and an analytic independent-product null baseline.

Current numerical evidence includes the theory-matched five-qubit collision benchmark, permutation and finite-shot diagnostics, NISQ-style noise stress tests, an external-architecture benchmark based on Chen et al. (2019), and an environment-only resource benchmark against a system-assisted correlation estimator and full Pauli tomography in measurement-setting count.

No quantum advantage, universal tomography superiority, unique POVM recovery, or hardware demonstration is claimed.

## Current manuscript

- [Version 3 LaTeX](paper/EIQL_v3.tex)
- [Manuscript notes](paper/README.md)
- [Research track](TRACK.md)
- [Canonical numerical results](RESULTS.md)

Version 3 title:

**Environment-Induced Quantum Learning (EIQL): Self-Supervised Measurement Discovery from Redundant Quantum Records**

## Repository layout

```text
paper/                         Version 3 manuscript + generated-figure references
experiments/
  01_blind_pointer/            historical blind-pointer exploration
  02_collision_model/          explicit S-E collision dynamics
  03_general_hamiltonian/      generalized Hamiltonian stress test
  04_revised_objective/        primary theory-matched EIQL objective
  05_noisy_nisq/               depolarization + readout-noise stress test
  06_chen2019/                 published photonic-QD architecture benchmark
  07_resource_benchmark/       EIQL vs tomography/system-assisted resources
classical_sanity/              auxiliary classical multiview sanity checks
docs/                          literature-positioning notes
```

## Strongest numerical results

On the Chen et al. mixed-quality record architecture, the learned worst-pair disagreement was approximately **0.27689**, close to the physical oracle floor **0.27487**. EIQL selected the three ideal records in **12/12** population hidden-basis worlds and **10/10** finite-shot worlds.

In the resource benchmark at 6912 copies per method, environment-only EIQL recovered decoder axes with mean errors **1.63 deg** (strong records) and **2.08 deg** (mixed records), compared with **2.32 deg** and **2.65 deg** for the stronger system-assisted correlation baseline in the same simulated task. For five environment fragments, the pair-moment design uses 27 distinct Pauli settings, versus 9 for the system-assisted task-specific baseline and 729 for full six-qubit Pauli tomography. This is a structured-task comparison, not a universal sample-complexity advantage claim.

## Scope of the novelty claim

EIQL does not claim to introduce Quantum Darwinism, redundant environmental records, pointer observables, observer consensus, local witnesses of Darwinism, classical multiview agreement, or quantum self-supervision.

The proposed contribution is narrower:

> **Redundancy across independently accessible quantum environmental fragments is used as the self-supervised training signal for discovering an initially unknown local measurement/decoder.**

The representation is physically instantiated by a quantum measurement rather than supplied as an already classical feature vector.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python experiments/04_revised_objective/eiql_v21_simulation.py
python experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py
python experiments/06_chen2019/eiql_chen2019_benchmark.py
python experiments/07_resource_benchmark/eiql_vs_tomography_resource_benchmark.py
```

The scripts are research prototypes with fixed seeds where appropriate, not a packaged library.

## License

See [LICENSE](LICENSE).
