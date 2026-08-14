# EIQL manuscript status

The manuscript has gone through three internal working stages:

1. **V1 theory note** — initial formalization of EIQL and SBS-based identifiability;
2. **V2 / V2.1 repair cycle** — corrected alphabet assumptions, robust proof, symmetric objective, decoder relabelings/equivalence, finite-shot proposition, independent-product baseline, and statistical diagnostics;
3. **Submission-draft stage** — tightened framing as a *quantum measurement-learning framework*, added NISQ-style noise stress tests, and separated established Quantum-Darwinism physics from the proposed unknown-decoder learning contribution.

## Current manuscript spine

1. research question and scope;
2. quantum-fragment / hardware-constrained decoder setting;
3. EIQL richness-disagreement objective;
4. exact SBS pointer-information structural theorem;
5. robust theorem near SBS;
6. Bayes-recovery corollary;
7. finite-shot result for a pre-specified finite candidate class;
8. analytic independent-product null ceiling;
9. theory-matched five-qubit collision simulation;
10. NISQ-style noise stress test;
11. prior-art positioning and limitations;
12. proposed external-architecture / hardware tests.

## Current central wording

EIQL is **not** claimed to be a new universal machine-learning paradigm. The current defensible positioning is:

> **EIQL is a quantum measurement-learning framework in which redundancy across independently accessible environmental fragments supplies the self-supervised signal for discovering an initially unknown local decoder.**

The framework aims to identify pointer information / decoder behavior on relevant record states, not a unique POVM operator on the full Hilbert space.

## Important limitations to preserve in the manuscript

- robust theorem currently assumes proximity to an SBS reference state;
- finite-shot proposition certifies a fixed finite measurement candidate class, not arbitrary adaptive search;
- current hardware evidence is simulated rather than an actual EIQL run on a processor;
- no quantum advantage is claimed;
- classical multiview/common-information methods are related and must be discussed explicitly;
- experimental QD papers already demonstrate redundant records and designed local witnesses; EIQL's distinction is **learned unknown decoders**.

## Typeset working artifact

A full LaTeX/PDF working draft was produced during the development session. It is being kept out of the repository at this checkpoint while figures/citations and the new Chen-architecture benchmark are consolidated into one clean submission version. The next manuscript sync should add the final source together with generated figures through a reproducible build target rather than archive several obsolete PDFs.

See [`../TRACK.md`](../TRACK.md) for the research log and [`../RESULTS.md`](../RESULTS.md) for canonical numerical results.
