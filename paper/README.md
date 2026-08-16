# Current EIQL manuscript

The canonical manuscript is now:

**Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**

by **Marwan AIT HADDOU**, Independent Researcher, Morocco.

## Canonical source

Use [`current/EIQL_PRXQ_final.tex`](current/EIQL_PRXQ_final.tex) and the modular files in [`current/parts/`](current/parts/). The current paper is organized as:

1. Introduction
2. Related Work
3. Theory
4. Numerical Experiments and Analysis
5. Discussion
6. Conclusion
7. Data Availability
8. References
9. Appendices

The final editorial pass deliberately keeps the scientific scope fixed. It reduces duplication between the Introduction and Related Work, adds a short Theory roadmap, makes the simulation-only character of Section IV explicit in its title, and sharpens the Conclusion around three headline contributions: the unknown-readout identifiability hierarchy, redundancy as an inverse-conditioning resource, and the passive-versus-interventional semantic boundary.

## Build

With the figure assets present in `current/figures/`:

```bash
cd paper/current
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
```

The compiled manuscript is 19 pages in the current REVTeX two-column layout.

## Scope and claim discipline

The paper is theoretical with simulation-based operational stress tests. It does not claim hardware validation, generic efficient multiclass tensor recovery, robustness to arbitrary correlated noise, or a universal tomography/sample-complexity advantage.

The theory-matched code is in experiments 09-12 at the repository root. The older `EIQL_v3.tex` manuscript and the older `sections/` directory are retained only as historical provenance.
