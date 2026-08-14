# Version 3 figures

The manuscript figures are generated outputs rather than primary source data. Recreate them with the canonical experiment scripts and copy the PNGs into this directory before compiling `paper/EIQL_v3.tex`.

Expected filenames:

- `eiql_v21_frontier.png` — from `experiments/04_revised_objective/`
- `eiql_v21_search_convergence.png` — from `experiments/04_revised_objective/`
- `eiql_noisy_nisq_disagreement.png` — from `experiments/05_noisy_nisq/`
- `eiql_chen_multistart_vs_oracle.png` — from `experiments/06_chen2019/`
- `eiql_vs_tomography_equal_budget.png` — from `experiments/07_resource_benchmark/`
- `eiql_vs_tomography_settings_scaling.png` — from `experiments/07_resource_benchmark/`

A later reproducibility cleanup should replace the manual copy step with a single Makefile/script target.
