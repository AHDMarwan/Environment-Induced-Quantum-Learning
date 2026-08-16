# Current PRX Quantum manuscript

This directory contains the current manuscript

**Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**

by **Marwan AIT HADDOU**.

## Author

- Marwan AIT HADDOU
- Independent Researcher, Morocco
- Email: aithaddou.marwan@outlook.com
- ORCID: https://orcid.org/0009-0008-1734-1721

## Canonical source

- `EIQL_PRXQ_final.tex` — complete manuscript source.
- `parts/part01.tex` ... `parts/part10.tex` — modular source included by the canonical file.

The compiled submission PDF and complete source bundle, including all figure PDFs, are distributed with the corresponding GitHub release.

## Manuscript structure

The paper follows the final submission-oriented organization:

1. Introduction
2. Related Work
3. Theory
4. Experiments and Analysis
5. Discussion
6. Conclusion
7. Data Availability
8. References
9. Appendices

The numerical validation is simulation-only and is presented as theorem-matched and hardware-informed evidence, not hardware validation.

## Reproducibility code

The principal experiments associated with the current manuscript are:

- `../../experiments/09_finite_shot_theorem2/theorem2_finite_shot.py`
- `../../experiments/10_conditional_correlation/conditional_correlation_stress.py`
- `../../experiments/11_multiclass_views/multiclass_two_vs_three.py`
- `../../experiments/12_collision_virtual/collision_phase_diagram.py`

The GitHub Actions workflow is `../../.github/workflows/hardware-informed-experiments.yml`.
