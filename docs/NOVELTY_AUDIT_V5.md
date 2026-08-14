# EIQL V5 novelty audit

This audit targets the most serious novelty risk: whether the combination of unknown quantum measurements, unlabeled correlations, common-information extraction, and environmental redundancy already exists under different terminology.

## Closest prior-art families

- **Quantum Darwinism / SBS / redundant observables:** established physical prior art. EIQL does not claim redundancy or pointer selection as new.
- **Unknown quantum measurements:** Cheng, Hsieh, and Yeh study statistical learnability/sample complexity for an externally specified unknown target measurement (arXiv:1501.00559).
- **Training a physical measurement device on unknown states:** Concha et al. optimize a physical POVM, but use classically communicated state labels during training (arXiv:2111.13568; Scientific Reports 13, 7460, 2023).
- **Self-consistent state/measurement tomography:** Stephens et al. and Cattaneo et al. jointly infer states and POVMs using known transformations, informational completeness, or a joint forward model (arXiv:2107.00121; arXiv:2212.10262).
- **Quantum common-randomness extraction:** Devetak and Winter optimize measurements on quantum correlations to distill shared classical randomness, generally with one-way communication (arXiv:quant-ph/0304196). This is the closest information-theoretic neighbor found.
- **Correlation-based multiview identifiability:** Lyu et al. prove shared-latent recovery from correlation-maximizing classical views under generative assumptions (arXiv:2106.07115). This establishes that cross-view agreement/correlation as self-supervision is not new.

## Scoped novelty claim

The search did not identify a work combining all of the following in one formulation:

1. initially unknown local measurements on environmental fragments;
2. no pointer labels and no direct system access during training;
3. same-event inter-fragment redundancy as the supervisory signal;
4. explicit hardware-constrained agreement-richness optimization; and
5. pointer-information guarantees conditional on SBS-type structure.

The defensible wording is therefore: **to our knowledge, this combination has not been formulated and analyzed in this form.** This is not an exhaustive proof of novelty.

## Important boundary

V5 adds a correlated-nuisance counterexample. A shared nuisance variable independent of the system can achieve maximal richness and lower disagreement than the noisy pointer record. Therefore EIQL statistics alone are not an SBS witness; the structural assumption in the robust theorem is essential.
