# EIQL V5 major revision

V5 implements the skeptical-referee roadmap before arXiv submission.

- Narrowed title: **Environment-Induced Quantum Learning: Learning Unknown Quantum Measurements from Redundant Environmental Records**.
- Moved the robust-theorem caveat into the abstract and introduction: SBS proximity is an external/model assumption, not something EIQL statistics certify.
- Added an adversarial novelty comparison to quantum common-randomness extraction, physical measurement-device training, self-consistent state/measurement tomography, and classical multiview latent-correlation identifiability.
- Added `experiments/08_correlated_nuisance/`: a deliberate failure case where a shared nuisance independent of the system has one bit of richness and zero disagreement, so the EIQL tie-break selects it over a noisy pointer record.
- Calibrated Proposition 1 at the actual finite-shot operating point. For Q=500, m=4, L=2, n=600, beta=0.05: a_n=0.1016, tau_n=0.1028, c_2(tau_n)=0.4777 bit and the worst-case richness gap is 0.9555 bit. The theorem is valid but practically vacuous at these parameters; V5 states this explicitly.
- Reorganized numerics so the collision model is a theory sanity check, the correlated nuisance case defines the failure boundary, and the independently hidden-decoder Chen architecture is the main external benchmark. Noise and resource comparisons follow.
- Removed the standalone search-convergence figure and consolidated repeated scope disclaimers.

The arXiv-ready V5 PDF/source bundle was built and visually preflighted locally. Binary figure synchronization to the repository is intentionally kept separate from the text/code checkpoint.
