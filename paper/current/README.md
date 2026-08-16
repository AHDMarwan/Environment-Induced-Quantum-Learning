# PRX Quantum manuscript - current source

Canonical title: **Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**

Author: **Marwan AIT HADDOU**  
Affiliation: **Independent Researcher, Morocco**  
Email: `aithaddou.marwan@outlook.com`  
ORCID: [0009-0008-1734-1721](https://orcid.org/0009-0008-1734-1721)

## Files tracked here

- `EIQL_PRXQ_final.tex` - REVTeX entry point.
- `parts/` - modular manuscript source.
- `README.md` - build and scope notes.

The canonical GitHub source is intentionally text-first. The complete submission source bundle used for local compilation also contains the figure PDFs; the compiled 19-page PDF is generated from that bundle rather than treated as the canonical repository source.

## Structure

Introduction -> Related Work -> Theory -> Numerical Experiments and Analysis -> Discussion -> Conclusion -> Data Availability -> References -> Appendices.

## Build

With the manuscript figure assets available in a local `figures/` subdirectory:

```bash
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
pdflatex -interaction=nonstopmode -halt-on-error EIQL_PRXQ_final.tex
```

The editorial pass dated 2026-08-16 changes presentation only; it introduces no new theorem or scientific claim. The matching local submission bundle compiles to 19 pages in the current REVTeX two-column layout.
