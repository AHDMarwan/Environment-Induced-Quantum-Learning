# Environment-Induced Quantum Learning (EIQL)

This repository contains the manuscript and reproducibility code for:

**Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**

Author: **Marwan AIT HADDOU**  
Affiliation: **Independent Researcher, Morocco**  
Email: `aithaddou.marwan@outlook.com`  
ORCID: [0009-0008-1734-1721](https://orcid.org/0009-0008-1734-1721)

## Current manuscript

The canonical submission-oriented source is under [`paper/current/`](paper/current/). Its journal structure is:

**Introduction -> Related Work -> Theory -> Numerical Experiments and Analysis -> Discussion -> Conclusion -> Data Availability -> References -> Appendices.**

The paper studies three distinct inverse targets downstream of Quantum Darwinism: decoder identification, latent-ensemble identification, and semantic identification. The central contributions are an unknown-readout identifiability hierarchy, redundancy as an inverse-conditioning resource, and the passive-versus-interventional boundary for system-specific semantics.

All numerical validation is simulation-only. No hardware-validation claim is made.

## Theory-matched numerical suite

The experiments most directly tied to the current manuscript are:

- [`experiments/09_finite_shot_theorem2/`](experiments/09_finite_shot_theorem2/) - finite-shot binary decoder recovery and Theorem 2 scaling;
- [`experiments/10_conditional_correlation/`](experiments/10_conditional_correlation/) - controlled conditional-correlation/model-mismatch stress test;
- [`experiments/11_multiclass_views/`](experiments/11_multiclass_views/) - exact two-view ambiguity and finite-shot three-view recovery;
- [`experiments/12_collision_virtual/`](experiments/12_collision_virtual/) - microscopic system-environment collision-model recovery phase diagram.

Earlier experiments remain in the repository as research history and secondary benchmarks, including the Chen-derived architecture and resource-comparison studies.

## Reproducibility

Install the Python dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The hardware-informed suite is also exercised by the repository's GitHub Actions workflow. Numerical outputs should be interpreted within the structural assumptions stated in the manuscript; the repository does not claim generic tensor-recovery efficiency, device-calibrated noise robustness, or a universal tomography/sample-complexity advantage.

## Manuscript build

The modular LaTeX entry point is:

```text
paper/current/EIQL_PRXQ_final.tex
```

After the figure assets are present in `paper/current/figures/`, compile with three LaTeX passes:

```bash
cd paper/current
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
```

## Historical material

`paper/EIQL_v3.tex`, the older modular sections, and experiments 01-08 are retained for provenance. They are not the canonical source for the current identifiability manuscript.

## License

See [LICENSE](LICENSE).
