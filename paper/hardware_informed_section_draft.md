# Draft integration for the current identifiability manuscript

This is a prose/figure plan for replacing or expanding the current numerical section of **Identifiability of Environmental Records in Quantum Darwinism: Learning Readouts from Redundancy and Intervention**. It is intentionally phrased as simulation evidence, not hardware validation.

## X. Hardware-informed numerical experiments

The analytical results above concern identifiability at the population level and, for the binary case, provide an explicit finite-shot perturbation guarantee. We therefore test four distinct operational questions using finite measurement records rather than direct access to the underlying density operators: statistical scaling of the binary connected-operator estimator, robustness to controlled violations of conditional independence, the two-view/three-view multiclass transition, and end-to-end recovery in an explicit system-environment collision model. These tests are numerical experiments; no quantum-hardware data are used.

### A. Finite-shot binary recovery

We first test the finite-shot two-fragment estimator underlying Theorem 2. In each realization, a balanced latent record prepares two conditionally independent qubit records with independently randomized local orientations. The learner receives only same-event randomized Pauli-shadow snapshots and forms the paired connected-operator estimator used in the proof. We vary the local Bloch contrast over \(c\in\{0.50,0.75,1.00\}\) and the number of independent event pairs over \(N\in\{512,2048,8192,32768,131072\}\).

The empirical Hilbert-Schmidt angular error decreases approximately as \(N^{-1/2}\). Log-log fits to the median error give slopes about \(-0.489\), \(-0.519\), and \(-0.489\) for \(c=0.50,0.75,1.00\), respectively. Moreover, the rescaled quantity \(c^2\sqrt{N}\,\sin\angle(\widehat U,\Delta)\) is approximately constant across the tested regimes (about \(3.75\pm0.36\)), consistent with the \(c^{-2}\) signal-conditioning implied by the rank-one singular value. For example, at \(c=1\) the median sin-angle error decreases from about \(0.170\) at 1024 physical events to about \(0.011\) at 262144 events.

The explicit concentration bound of Theorem 2 is substantially more conservative than the observed errors. We therefore use the simulation to validate the predicted statistical and contrast scaling, not to claim that the worst-case constants are tight.

### B. Controlled violation of conditional independence

We next introduce a tunable conditional inter-fragment correlation while preserving the local conditional marginals. The perturbation is chosen so that the deviation from the product-record model can be quantified by the conditional mutual information

\[
\nu=I(E_i:E_j\mid X).
\]

As the perturbation increases, the population leading singular direction of the connected operator rotates away from the ideal Helstrom contrast direction, and the finite-shot estimator follows the same degradation. Across the tested range, the population sin-angle error is well described by

\[
\sin\theta_{\rm pop}\simeq 1.61\sqrt{\nu}+0.024,
\]

with \(R^2\approx0.995\). This is consistent with the square-root dependence entering the Pinsker-based perturbation term in the robust binary theorem. The finite-shot median approaches the population degradation; at the largest tested perturbation the population and finite-shot sin-angle errors are approximately \(0.445\) and \(0.447\), respectively.

The corresponding Pinsker-Wedin upper bound remains deliberately worst-case and becomes uninformative before empirical recovery fails. We therefore distinguish the algebraic condition needed for a positive perturbative denominator from the stronger condition that the resulting sin-angle bound be below the trivial upper bound of one.

### C. Exact two-view ambiguity and finite-shot three-view recovery

The multiclass experiment uses the exact commuting three-class counterexample from Appendix B. The two distinct latent decompositions agree in their observed two-view distribution to approximately \(1.4\times10^{-17}\) in maximum absolute entry while inducing different optimal local MAP decoders, \((0,1,2)\) and \((1,1,2)\). Increasing the number of two-view samples cannot remove this population-level ambiguity.

We then append a representative well-conditioned third stochastic view and reconstruct the latent response law by a spectral three-view method. The reconstruction routine uses only empirical moments; the true latent response matrix is used only after reconstruction to apply the common permutation needed for evaluation, as allowed by the identifiability statement. The probability of exact MAP-decoder recovery rises from 0.20 at \(10^3\) samples to 0.475 at \(3\times10^3\), 0.6875 at \(10^4\), 0.925 at \(3\times10^4\), and 1.00 at \(10^5\) samples. Over the same range the spectral failure probability decreases to zero, while the reconstruction errors of the conditional response matrix and latent weights decrease toward the expected finite-sample regime.

This experiment should be read as a finite-shot illustration of the qualitative identifiability transition: two views can remain ambiguous even with exact population statistics, whereas a suitably conditioned third view can restore latent and decoder recovery. It is not a universal sample-complexity theorem for arbitrary multiclass records.

### D. Explicit system-environment collision experiment

Finally, we use an end-to-end virtual experiment generated from explicit microscopic dynamics rather than inserting conditional environmental record states by hand. A system qubit initialized in \(|+\rangle\) sequentially interacts with five environment ancillas initially in \(|0\rangle\) through controlled-\(R_y(\theta)\) collisions,

\[
U_{SE_j}(\theta)=|0\rangle\!\langle0|_S\otimes I_{E_j}
+|1\rangle\!\langle1|_S\otimes R_y(\theta)_{E_j}.
\]

Each environmental fragment is subsequently conjugated by an independently drawn unknown local \(SU(2)\) rotation. After tracing out the system, the learner receives only local Pauli outcomes collected with the 27-setting orthogonal-array schedule, with a symmetric readout-flip probability \(q=0.02\). No system outcome, collision branch label, or hidden local basis is supplied to the decoder estimator.

The primary recovery criterion is deliberately strict: a run succeeds only if **every one of the five recovered fragment axes** lies within \(5^\circ\) of its local Helstrom direction. The resulting phase diagram is plotted against the local trace distinguishability

\[
D=\tfrac12\|\rho_{j,1}-\rho_{j,0}\|_1=\sin(\theta/2)
\]

and the number of shots per Pauli setting. Recovery improves jointly with record distinguishability and measurement budget, producing a clear finite-resource transition. The earlier mean-axis-error criterion is retained only as a supplementary diagnostic. Internal checks verify global-state normalization, balanced branch weights, and agreement between the dynamically generated local trace distance and \(\sin(\theta/2)\) to numerical precision.

This benchmark is hardware-informed rather than hardware-calibrated: the measurement restrictions, finite shots, hidden local bases, and readout flips are operationally motivated, but the noise parameters are not fitted to a particular device.

### E. Relation to the external Chen-derived benchmark

The Chen-derived six-photon benchmark serves a different purpose and should be retained in compressed form. The collision experiment above tests an explicit internally controlled dynamical model, whereas the Chen benchmark tests the unknown-readout task on an architecture motivated by an independently published Quantum-Darwinism experiment. The latter remains a simulation based on the published interaction architecture and does not reanalyze raw experimental events.

## Recommended main-text figure structure

**Figure X — Theory-matched finite-shot tests.** Three panels: (a) binary finite-shot scaling, preferably plotting a rescaled \(c^2\sqrt{N}\) error or otherwise making the \(N^{-1/2}\) scaling visible; (b) population and finite-shot decoder error versus \(\sqrt{I(E_i:E_j\mid X)}\), together with the perturbative trend; (c) exact two-view ambiguity plus the finite-shot probability of three-view MAP-decoder recovery.

**Figure Y — End-to-end virtual collision experiment.** Heat map of the strict success probability \(P[\max_j\theta_j\le5^\circ]\) versus local trace distinguishability \(D\) and shots per 27-setting orthogonal-array Pauli schedule. State explicitly in the caption that \(q=0.02\) symmetric readout flips are included and that the global \(S+E\) state is generated by sequential controlled-\(R_y\) collisions.

The existing Chen-derived figure can then be reduced to one external-architecture panel or moved partly to the supplement/appendix if space is tight.

## Claims that the numerical evidence supports

1. Finite-shot binary decoder recovery follows the predicted \(N^{-1/2}\) statistical scaling and is consistent with the expected contrast conditioning of the connected-operator estimator.
2. Controlled conditional correlations generate an approximately square-root degradation with \(I(E_i:E_j\mid X)\) over the tested perturbative regime, while the rigorous Pinsker-Wedin bound remains conservative.
3. An exact two-view multiclass ambiguity persists at population level, whereas a well-conditioned third view can restore reliable finite-sample decoder and latent-response recovery.
4. Under explicit sequential system-environment collisions, hidden local bases, finite Pauli measurements, and modest readout flips, environment-only decoder recovery exhibits a clear finite-resource operating region.

## Claims to avoid

Do not describe these simulations as hardware validation, device-calibrated noise modeling, a universal sample-complexity advantage, a tight verification of the finite-shot upper bound, or a proof that arbitrary correlated/non-Markovian environments remain identifiable.

## Reproducibility paths

- `experiments/09_finite_shot_theorem2/theorem2_finite_shot.py`
- `experiments/10_conditional_correlation/conditional_correlation_stress.py`
- `experiments/11_multiclass_views/multiclass_two_vs_three.py`
- `experiments/12_collision_virtual/collision_phase_diagram.py`
- `.github/workflows/hardware-informed-experiments.yml`
