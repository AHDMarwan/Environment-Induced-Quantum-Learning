# PRX Quantum manuscript checkpoint — 2026-08-16

## Canonical manuscript

Title: **Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**

Author metadata:

- **Marwan AIT HADDOU**
- Independent Researcher, Morocco
- Email: aithaddou.marwan@outlook.com
- ORCID: https://orcid.org/0009-0008-1734-1721

Current editable source:

- `paper/current/EIQL_PRXQ_final.tex`
- `paper/current/parts/part01.tex` through `part10.tex`

The final compiled PDF and complete source archive with figure PDFs are distributed as GitHub release assets for this checkpoint.

## Final organization

1. Introduction
2. Related Work
3. Theory
4. Experiments and Analysis
5. Discussion
6. Conclusion
7. Data Availability
8. References
9. Appendices

The manuscript contains no TODO/TBD placeholders and the author metadata has been updated throughout the current source.

## Numerical evidence

The principal current experiments are:

- Experiment 09: finite-shot verification of the binary recovery theorem.
- Experiment 10: controlled conditional-correlation/model-mismatch stress test.
- Experiment 11: multiclass two-view ambiguity versus three-view recovery.
- Experiment 12: microscopic collision-model phase diagram with restricted Pauli measurements and 2% symmetric readout noise.

The numerical evidence is simulation-only and should be described as theorem-matched or hardware-informed simulation, not experimental hardware validation.

## Reproducibility

The scripts are under `experiments/09_finite_shot_theorem2/` through `experiments/12_collision_virtual/`. The workflow `.github/workflows/hardware-informed-experiments.yml` executes the suite in GitHub Actions.

## Review status

`paper/PRE_SUBMISSION_REFEREE_STYLE_REVIEW_2026-08-16.md` records the final internal referee-style assessment. It recommends minor revision / publish after clarification and is explicitly labeled as a pre-submission assessment rather than an official journal referee report.

## Version policy

Older files such as `paper/EIQL_v3.tex`, the earlier modular section tree, and the 2026-08-15 checkpoint are retained for development history. The canonical manuscript for submission work is `paper/current/`.
