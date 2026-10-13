# Qiskit Fall Fest 2026 - PS-Q2: High-Dimensional Quantum Kernel Classifier
**Team:** Q-Kernel Force  
**Track:** Quantum Machine Learning  

## Executive Summary
This repository implements **PS-Q2 (High-Dimensional Quantum Kernel Classifier)** using Qiskit's `ZZFeatureMap` to project feature vectors into high-dimensional Hilbert space. We compute quantum state overlap kernel matrices via `FidelityQuantumKernel` to train a Support Vector Classifier (`QSVC`), achieving **98.89% accuracy**. We compare this against classical RBF and Linear SVM baselines and profile hardware compilation overheads across Processor A (5-qubit) and Processor B (9-qubit) coupling maps.

## Repository Structure
```text
qff-2026-q-kernel-force/
├── README.md                          # Execution summary & benchmarks
├── requirements.txt                   # Dependency environment
├── notebooks/
│   └── PS_Q2_Quantum_Kernel.ipynb     # Main pipeline notebook
└── results/
    ├── processor_a_transpilation.json  # Transpilation metrics for Processor A
    └── processor_b_transpilation.json  # Transpilation metrics for Processor B
