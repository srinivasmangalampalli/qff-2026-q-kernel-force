# QFF 2026 — Phase 1 Technical Report: PS-Q2 Quantum Kernel Classifier

## 1. Problem statement and objective
This submission studies whether a fidelity-based quantum kernel support vector classifier (QSVC) provides useful classification performance on two small binary datasets compared with classical support vector machines, and how the supplied Processor A and Processor B coupling graphs affect compilation of the quantum feature-map/kernel circuits. The quantum method is not claimed to outperform the best classical model.

## 2. Datasets and preprocessing
- **Digits 0 versus 1:** 360 samples; 270 train and 90 test. Four features obtained with PCA, then MinMax scaling to [0, pi/2]. Preprocessing is fitted on training data only.
- **make_moons:** 100 synthetic samples, noise 0.1, with stratified 75/25 train/test split. Five independent seeds (10, 20, 30, 40, 50) are used for the reported tuned repeated comparison.

## 3. Methods and controlled comparisons
The quantum model uses a Qiskit ZZFeatureMap (two repetitions; linear entanglement) and a fidelity-based quantum kernel passed to an SVM with a precomputed kernel. Digits uses four feature-map qubits and make_moons uses two. Classical controls are RBF and polynomial SVMs. Hyperparameters are selected by cross-validation; the tuned classical models use preprocessing inside the cross-validation pipeline. The quantum results are ideal-simulator results unless expressly labelled otherwise.

## 4. Processor A and Processor B: definitions
Both processor definitions use the basis gates `rz`, `sx`, `x`, `cx` and transpiler optimization level 1, with a recorded transpiler seed of 42.

**Processor A:** 5 physical qubits with undirected couplings (0,1), (1,2), (1,3), (3,4). It is a sparse, tree-like architecture. The limited connectivity can force additional routing operations when the logical circuit needs interactions between qubits without a direct edge.

**Processor B:** 9 physical qubits with undirected couplings (0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0). It has more physical qubits and alternative paths. This can reduce routing for some circuits, but it does **not** guarantee fewer gates for every workload.

![Processor A coupling map](assets/processor_A_topology.png)

![Processor B coupling map](assets/processor_B_topology.png)

### Processor architecture diagrams

**Processor A — 5-qubit connectivity**

![Processor A topology](assets/processor_A_topology.png)

**Processor B — 9-qubit connectivity**

![Processor B topology](assets/processor_B_topology.png)

These diagrams represent the coupling connections defined in `processors/processor_A.json` and `processors/processor_B.json`. They are processor topology models, not photographs of physical quantum hardware.

## 5. What causes processor penalties?
A quantum circuit may request a two-qubit interaction between qubits that are not adjacent on the hardware coupling graph. The compiler may then need a different initial placement, SWAP routing, or a longer sequence of native gates. **More SWAPs, CX gates and circuit depth** typically create more opportunities for physical noise and decoherence. In the common decomposition, a SWAP can cost three CX gates before further optimization. This is a hardware-cost explanation, not a claim of a fixed scoring penalty or a measured hardware error rate. Processor B's extra unused qubits do not automatically improve a small two-qubit circuit.

## 6. Recorded classification results
Five-seed tuned `make_moons` mean test accuracies:

| Model | Mean test accuracy |
|---|---:|
| Classical RBF SVM | 100.0% |
| Quantum kernel SVM | 90.4% |
| Classical polynomial SVM | 87.2% |

The quantum model did **not** outperform the tuned classical RBF baseline in these experiments. The quantum model's recorded standard deviation across five seeds was 4.56 percentage points; the polynomial model's was 8.20 points. Five splits on a small dataset are not enough to establish general superiority.

## 7. Recorded A/B processor comparison
A representative two-qubit **full fidelity circuit** was transpiled on both processor configurations:

| Metric | Processor A | Processor B |
|---|---:|---:|
| Compiled circuit depth | 27 | 27 |
| CX count | 6 | 6 |
| SWAP count | 0 | 0 |

These are **compilation metrics**, not physical processor measurements. The original two-qubit circuit produced identical depth and CX counts on both processors, so this particular benchmark did not reveal an architectural difference. However, the extended four-qubit benchmark in Section 12 showed that Processor B achieved 26.6% lower mean circuit depth and 9.1% fewer CX gates for full entanglement across five transpiler seeds. Both processors remained identical for linear entanglement. These findings concern circuit compilation only; they do not establish improved noisy classification accuracy.

## 8. Noise pilot and limitations
An illustrative Aer noise pilot on 20 training and 10 testing digits examples used one-qubit depolarizing error 0.001, two-qubit depolarizing error 0.005, readout error 0.01 and 1024 shots. Both ideal and noisy versions classified all 10 test examples correctly; average kernel deviation was approximately 0.012549. The pilot is too small to claim noise robustness and is **not** a calibrated Processor A/B noise comparison. No physical processor was used.

## 9. Bell-state validation — verified simulation

A Bell state was prepared using a Hadamard gate followed by a controlled-X gate, with measurements on both qubits.

The target state is:

`|Phi+> = (|00> + |11>) / sqrt(2)`

The circuit was transpiled using the coupling maps of Processor A and Processor B and simulated with Qiskit Aer using 4,096 shots and a fixed random seed.

| Measurement | Processor A | Processor B |
|---|---:|---:|
| 00 | 2009 (49.05%) | 2009 (49.05%) |
| 01 | 0 (0%) | 0 (0%) |
| 10 | 0 (0%) | 0 (0%) |
| 11 | 2087 (50.95%) | 2087 (50.95%) |
| Circuit depth | 5 | 5 |

The observed distribution is consistent with the expected Bell-state measurement probabilities of 50% for `00` and 50% for `11`.

### Bell-state evidence

**Processor A**

![Processor A Bell-state histogram](assets/bell_state/processor_A_bell_histogram.png)

**Processor B**

![Processor B Bell-state histogram](assets/bell_state/processor_B_bell_histogram.png)

The corresponding circuit diagrams and measurement counts are saved in `assets/bell_state/`.

These are ideal simulator results, not physical quantum hardware measurements. They do not establish a noise or fidelity advantage for either processor.

## 10. Reproducibility and evidence locations

- Main classification notebook: `notebooks/main.ipynb`
- Processor definitions: `processors/processor_A.json`, `processors/processor_B.json`
- Classification results and existing benchmarks: `results/`
- Processor topology diagrams: `assets/processor_A_topology.png`, `assets/processor_B_topology.png`
- Bell-state validation script: `generate_bell_evidence.py`
- Bell-state histograms and measurement counts: `assets/bell_state/`
- Extended architecture benchmark: `benchmark_qml_processors.py`
- Architecture benchmark measurements: `results/qml_processor_architecture.csv`
- Figure-generation script: `plot_qml_processors.py`
- Circuit-depth figure: `results/figures/qml_processor_depth.png`
- CX-gate figure: `results/figures/qml_processor_cx.png`

All processor architecture measurements are simulation-based compilation results, not physical quantum-hardware measurements.

## 11. Next steps and integrity statement

Completed work includes Bell-state validation using ideal Qiskit Aer simulation and an extended four-qubit ZZ feature-map architecture benchmark across five transpiler seeds. The benchmark results and figures are documented in Section 12.

Remaining priorities are (1) compare ideal versus noisy A/B quantum-kernel classification using clearly specified noise assumptions, (2) investigate routing and placement effects, and (3) verify compliance with the official PS-Q2 evaluation requirements.

The results must not be presented as physical quantum-hardware measurements or proof of quantum advantage. This report was prepared with AI assistance and requires author verification before submission.

## 12. Extended QML Processor Architecture Benchmark

### 12.1 Objective

This experiment evaluates how processor connectivity affects the compilation of four-qubit ZZ feature-map circuits used in quantum-kernel classification.

Two entanglement configurations were tested:
- Linear entanglement, matching the main Digits classifier.
- Full entanglement, as an additional topology-sensitive benchmark.

### 12.2 Experimental Setup

- Logical qubits: 4
- Feature map: `zz_feature_map`
- Repetitions: 2
- Basis gates: RZ, SX, X, CX
- Optimization level: 1
- Transpiler seeds: 11, 21, 31, 41, 42
- Processors: A (5 physical qubits) and B (9 physical qubits)

Each processor-entanglement combination was transpiled five times.

### 12.3 Results

Values are mean +/- sample standard deviation across five transpiler seeds.

| Entanglement | Metric | Processor A | Processor B |
|---|---|---:|---:|
| Linear | Circuit depth | 23.00 +/- 0.00 | 23.00 +/- 0.00 |
| Linear | CX gates | 12.00 +/- 0.00 | 12.00 +/- 0.00 |
| Full | Circuit depth | 61.00 +/- 0.00 | 44.80 +/- 1.79 |
| Full | CX gates | 33.00 +/- 0.00 | 30.00 +/- 0.00 |

### 12.4 Circuit Depth Comparison

![Processor A vs B circuit depth](results/figures/qml_processor_depth.png)

### 12.5 Two-Qubit Gate Comparison

![Processor A vs B CX gates](results/figures/qml_processor_cx.png)

### 12.6 Interpretation

For linear entanglement, both processors produce identical circuit depth and CX counts.

For full entanglement, Processor B reduces mean circuit depth by approximately 26.6% and CX count by 9.1% relative to Processor A.

The denser connectivity of Processor B is a plausible explanation for the reduced compilation overhead. However, this experiment alone does not isolate connectivity from all transpiler placement and routing decisions.

The final transpiled circuits contain zero explicit SWAP gates. This does not establish zero routing overhead because routing operations can be decomposed into the target basis gates.

### 12.7 Limitations

- These are transpilation results, not quantum-hardware measurements.
- Five transpiler seeds measure compiler variability, not hardware uncertainty.
- Full entanglement is an additional benchmark and does not replace the original linear-entanglement classifier.
- No noisy classification accuracy advantage has been established.

### 12.8 Reproducibility

- Script: `benchmark_qml_processors.py`
- Raw measurements: `results/qml_processor_architecture.csv`
- Plot generator: `plot_qml_processors.py`
- Figures: `results/figures/`

Run the benchmark using the project's Qiskit environment, then execute the plotting script to regenerate the figures.

## 13. Noisy Processor A/B Quantum-Kernel Classification Pilot

### 13.1 Objective

This pilot investigates whether differences in compiled quantum-kernel circuit complexity between Processor A and Processor B correspond to differences in classification accuracy under identical illustrative noise assumptions.

### 13.2 Experimental setup

- Dataset: scikit-learn Digits, classes 0 and 1
- Training samples: 12
- Testing samples: 6
- Preprocessing: four-component PCA followed by MinMax scaling to [0, pi/2], fitted only on training data
- Quantum feature map: four-qubit ZZ feature map, two repetitions, full entanglement
- Classifier: SVM with a sampled, precomputed fidelity kernel and C=1.0
- Measurement shots: 256 per fidelity circuit
- Dataset, transpiler and simulator seed: 42
- Simulator: Qiskit Aer matrix-product-state simulator
- Basis gates: rz, sx, x, cx
- Processor connectivity: supplied Processor A and B coupling graphs

The ideal condition uses finite-shot simulation without an explicit noise model. The noisy condition uses the same circuit compilation settings with illustrative depolarizing errors of 0.001 for one-qubit gates and 0.005 for CX gates, plus a symmetric 1% readout error.

### 13.3 Recorded results

| Metric | Processor A | Processor B |
|---|---:|---:|
| Ideal test accuracy | 83.33% | 83.33% |
| Noisy test accuracy | 66.67% | 66.67% |
| Mean training-kernel circuit depth | 110.75 | 88.25 |
| Mean training-kernel CX count | 63.17 | 55.17 |

Processor B produced approximately 20.3% lower mean circuit depth and 12.7% fewer mean CX gates in this pilot.

Both processors correctly classified five of six test samples in the ideal condition and four of six under the illustrative noise model.

### 13.4 Interpretation

Processor B required fewer compiled operations for the tested full-entanglement fidelity circuits. Nevertheless, both processors achieved the same test accuracy in the ideal and noisy conditions.

The pilot therefore demonstrates a compilation-cost difference, not a measured classification-accuracy advantage.

### 13.5 Limitations

- Only six test samples and one dataset split were evaluated.
- Only one transpiler seed and one simulator seed were used.
- Finite-shot sampling introduces statistical variation even in the ideal condition.
- The noise parameters are illustrative and are not calibrated to physical Processor A or Processor B hardware.
- The experiment does not establish quantum advantage, statistical significance, or physical hardware performance.
- Full entanglement was selected to probe processor connectivity; the original main Digits classifier uses linear entanglement.

### 13.6 Reproducibility

- Experiment script: `benchmark_noisy_qml.py`
- Raw results: `results/noisy_qml_processor_pilot.csv`
- Processor configurations: `processors/processor_A.json` and `processors/processor_B.json`
