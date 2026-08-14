# Iris classical sanity check

This experiment was a deliberately non-quantum sanity check for the shared-information inductive bias.

The four Iris features were split into two views:

- sepal length/width;
- petal length/width.

A label-free shared representation was learned with a CCA-style multiview construction and then clustered into three groups. Species labels were used only for evaluation / cluster alignment.

Across 100 stratified train/test splits:

| Method | Mean test accuracy | SD |
|---|---:|---:|
| shared latent, 1D | 0.7992 | 0.0516 |
| shared latent, 2D | 0.8296 | 0.0413 |
| KMeans on all 4 standardized features | 0.8260 | 0.0412 |
| supervised logistic reference | 0.9562 | 0.0244 |

This is **not evidence for EIQL as a quantum framework** and does not establish an advantage over classical multiview learning. It was used only to verify that the redundancy/shared-information idea behaves sensibly on a small real classical dataset.
