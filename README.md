# QFF 2026 — Quantum Kernel Force

## Project Overview
Comparison of quantum kernel support vector machines (QSVM)
with classical RBF and polynomial SVMs using Qiskit.

## Methods
- Datasets: sklearn Digits (0 vs 1) and make_moons
- Quantum feature maps: ZZFeatureMap
- Quantum kernels: fidelity-based, ideal simulation
- Classical baselines: RBF and polynomial SVM
- Model selection: cross-validation
- Repeated experiments: five make_moons seeds
- Processor comparison: Qiskit transpilation for A and B

## Main Results
Five-seed tuned make_moons mean test accuracy:

| Model | Mean Accuracy |
|---|---:|
| Classical RBF SVM | 100.0% |
| Quantum Kernel SVM | 90.4% |
| Classical Polynomial SVM | 87.2% |

No quantum advantage was observed.

## Processor Benchmark
A representative two-qubit fidelity circuit was transpiled
for both supplied processor configurations.

| Processor | Depth | CX Gates | SWAP Gates |
|---|---:|---:|---:|
| A | 27 | 6 | 0 |
| B | 27 | 6 | 0 |

These are compilation metrics, not measured hardware performance.

## Technical Report and Experimental Evidence

The [Phase 1 Technical Report](report.md) explains the PS-Q2
problem statement, methodology, processor architectures,
performance penalties, experimental findings, and limitations.

### Processor Architecture

| Processor A | Processor B |
|---|---|
| ![Processor A](assets/processor_A_topology.png) | ![Processor B](assets/processor_B_topology.png) |

### Bell-State Validation

A two-qubit Bell state was simulated using 4,096 shots
for each processor configuration.

| Processor A | Processor B |
|---|---|
| ![Bell A](assets/bell_state/processor_A_bell_histogram.png) | ![Bell B](assets/bell_state/processor_B_bell_histogram.png) |

Both simulations produced 2,009 counts of `00` and
2,087 counts of `11`, consistent with the expected Bell-state
measurement distribution.

These results use ideal simulation, not physical hardware.
The Bell-state experiment can be reproduced using
`generate_bell_evidence.py`.

## Limitations
- Quantum experiments use ideal simulation.
- Noise pilot uses illustrative noise, not calibrated processor noise.
- Five-seed tuned comparison is limited to make_moons.
- The quantum feature-map design was not independently tuned.
- No physical quantum processor was used.

## Project Files
- `notebooks/main.ipynb`: verified notebook
- `processors/`: processor configurations
- `results/`: experiment tables and plots
- `requirements.txt`: Python dependencies

## Reproduction
Install dependencies from `requirements.txt`, launch Jupyter,
and run `notebooks/main.ipynb` from the first cell.
