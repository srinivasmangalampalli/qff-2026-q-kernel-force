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

These are **compilation metrics**, not physical processor measurements. This small circuit fits both architectures without routing overhead, so the present experiment does **not** demonstrate an A/B performance difference. A meaningful extension would compare a larger interaction pattern over multiple transpiler seeds, while controlling layout, gate basis and noise assumptions.

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
- Notebook: `notebooks/main.ipynb`
- Processor definitions: `processors/processor_A.json`, `processors/processor_B.json`
- Classification and transpilation tables: `results/`
- Processor topology diagrams: `assets/processor_A_topology.png`, `assets/processor_B_topology.png`
- Bell validation script: `generate_bell_evidence.py` (requires execution)

## 11. Next steps and integrity statement
Priorities are (1) execute and archive Bell-state evidence, (2) repeat larger, topology-sensitive quantum-kernel compilation benchmarks over several seeds, (3) compare ideal versus noisy A/B classification using clearly specified, identical or processor-specific noise assumptions, and (4) confirm all official PS-Q2 rubric requirements. The present results must not be presented as measured quantum-hardware performance or quantum advantage. This report was prepared with AI assistance and requires author verification before submission.
