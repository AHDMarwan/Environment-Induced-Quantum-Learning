# Environment-Induced Quantum Learning (EIQL)

EIQL is a **quantum measurement-learning framework** for self-supervised discovery of a local decoder from redundant quantum environmental records.

The central operational question is:

> Given repeated access to quantum environment fragments, but no pointer labels and no prescribed readout basis, can a learner discover local measurements whose outputs are simultaneously informative and mutually consistent?

The current EIQL objective uses two quantities for fragment outputs \(Z_1,\ldots,Z_m\):

- **worst-pair disagreement**: \(D=\max_{i<j}P(Z_i\neq Z_j)\)
- **redundant richness**: \(R=\min_j H(Z_j)\)

The hardware-constrained learning problem is to maximize \(R\) subject to \(D\le\varepsilon\), with fragmentwise output relabelings treated as free classical post-processing.

## Status

Active research manuscript; **not peer reviewed and no quantum advantage is claimed**.

Current theory includes:

- an exact SBS structural lemma for pointer-information recovery;
- a robust identifiability theorem near an SBS reference state;
- a simple Bayes-recovery corollary;
- a finite-shot guarantee for a pre-specified finite measurement class;
- an analytic independent-product null baseline.

Current experiments include toy broadcast models, explicit collision dynamics, generalized unknown Hamiltonians, a revised 5-qubit EIQL objective benchmark, NISQ-style noise stress tests, and a benchmark based on the published Chen et al. six-photon Quantum-Darwinism architecture with hidden local decoder bases.

See **[TRACK.md](TRACK.md)** for the complete research log, current claims, numerical milestones, limitations, and next experiments.

## Repository layout

```text
paper/                         current manuscript and archived theory source
experiments/
  01_blind_pointer/            first redundancy-only decoder discovery
  02_collision_model/          explicit S-E collision dynamics
  03_general_hamiltonian/      unknown/generalized Hamiltonian stress test
  04_revised_objective/        consensus-richness objective matching theory
  05_noisy_nisq/               depolarizing + readout-noise stress test
  06_chen2019/                 published photonic-QD architecture benchmark
classical_sanity/
  iris/                        classical multiview sanity check
  synthetic_medical/           multimodal synthetic-data robustness check
docs/                          literature positioning and notes
```

Large raw synthetic datasets are intentionally not versioned; they are reproducible from the included generation scripts. Summary CSVs are versioned.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python experiments/04_revised_objective/eiql_v21_simulation.py
python experiments/05_noisy_nisq/eiql_noisy_nisq_simulation.py
python experiments/06_chen2019/eiql_chen2019_benchmark.py
```

The scripts use fixed seeds for reproducibility. They are research prototypes rather than a packaged library.

## Current strongest external-architecture result

Using the interaction structure of Chen et al. (2019), the benchmark independently hides the local basis of every environment record. EIQL is given neither the system variable nor the pointer labels.

In the ideal five-record setting, multi-start EIQL obtained a mean worst-pair disagreement of approximately **0.00193** across 12 independently hidden-basis worlds. In the heterogeneous setting, the learned disagreement (**0.27689**) was close to the physical oracle floor (**0.27487**). When asked to select the best three environment records, EIQL selected the three perfect records in **12/12** population runs and **10/10** finite-shot hidden-basis worlds.

These are simulations based on a published architecture, not a rerun of the original laboratory data.

## Scope of the novelty claim

EIQL does **not** claim to introduce Quantum Darwinism, redundant environmental records, pointer observables, observer consensus, local witnesses of Darwinism, classical multiview agreement, or generic quantum self-supervised learning.

The proposed contribution is narrower:

> **Redundancy across independently accessible quantum environmental fragments is used as the self-supervised training signal for discovering an initially unknown local measurement/decoder.**

The representation is physically instantiated by a quantum measurement rather than supplied as pre-existing classical features.

## License

See [LICENSE](LICENSE).
