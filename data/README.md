# Data policy

This repository primarily stores **reproducible code and compact result summaries** rather than large generated datasets.

## Synthetic data

The multimodal medical experiment generates synthetic Blood/MRI/ECG data from fixed random seeds. The raw generated CSV files are intentionally not versioned because they are large and can be regenerated from the script in:

`classical_sanity/synthetic_medical/synthetic_medical_eiql_experiment.py`

Compact summary tables may be versioned under the corresponding experiment directory.

## Published experimental architectures

The Chen et al. benchmark in this repository is a **simulation based on the published interaction architecture and parameters**, with additional hidden local SU(2) rotations introduced by EIQL to create an unknown-decoder task. It is not a copy of, or reanalysis of, the original laboratory raw data.

Likewise, the Saini-Behera and Zhu et al. papers are used for literature positioning and proposed hardware benchmarks; their raw data are not redistributed here.
