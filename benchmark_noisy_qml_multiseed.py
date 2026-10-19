import csv
import json
import os
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "2"

import numpy as np
from qiskit import transpile
from qiskit.circuit.library import zz_feature_map
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "noisy_qml_multiseed.csv"
SEEDS = [11, 21, 42]
SHOTS = 256

digits = load_digits()
mask = digits.target < 2
X, y = digits.data[mask], digits.target[mask]

feature_map = zz_feature_map(
    feature_dimension=4, reps=2, entanglement="full"
)

noise = NoiseModel()
noise.add_all_qubit_quantum_error(
    depolarizing_error(0.001, 1), ["sx", "x"]
)
noise.add_all_qubit_quantum_error(
    depolarizing_error(0.005, 2), ["cx"]
)
noise.add_all_qubit_readout_error(
    ReadoutError([[0.99, 0.01], [0.01, 0.99]])
)


def kernel_circuit(a, b):
    qc = feature_map.assign_parameters(a)
    qc.compose(
        feature_map.assign_parameters(b).inverse(),
        inplace=True
    )
    qc.measure_all()
    return qc


def estimate_kernel(left, right, simulator, config, coupling, seed):
    values = np.zeros((len(left), len(right)))
    depths = []
    cx_counts = []

    for i, a in enumerate(left):
        for j, b in enumerate(right):
            circuit = kernel_circuit(a, b)
            compiled = transpile(
                circuit,
                basis_gates=config["basis_gates"],
                coupling_map=coupling,
                optimization_level=config["optimization_level"],
                seed_transpiler=seed
            )

            result = simulator.run(
                compiled,
                shots=SHOTS,
                seed_simulator=seed,
                max_parallel_threads=2
            ).result()

            values[i, j] = (
                result.get_counts().get("0" * 4, 0) / SHOTS
            )
            depths.append(compiled.depth())
            cx_counts.append(compiled.count_ops().get("cx", 0))

    return (
        values,
        float(np.mean(depths)),
        float(np.mean(cx_counts))
    )


def correct_training_kernel(kernel):
    kernel = (kernel + kernel.T) / 2
    np.fill_diagonal(kernel, 1.0)

    eigenvalues, eigenvectors = np.linalg.eigh(kernel)
    min_eigenvalue = float(eigenvalues.min())

    if min_eigenvalue < 0:
        clipped = np.maximum(eigenvalues, 0)
        kernel = (eigenvectors * clipped) @ eigenvectors.T
        kernel = (kernel + kernel.T) / 2

    return kernel, min_eigenvalue


rows = []

for seed in SEEDS:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=24,
        test_size=12,
        stratify=y,
        random_state=seed
    )

    pca = PCA(n_components=4, random_state=seed)
    X_train = pca.fit_transform(X_train)
    X_test = pca.transform(X_test)

    scaler = MinMaxScaler(feature_range=(0, np.pi / 2))
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    for name in ("A", "B"):
        config = json.loads(
            (ROOT / "processors" / f"processor_{name}.json").read_text()
        )
        edges = [tuple(edge) for edge in config["coupling_edges"]]
        coupling = CouplingMap(
            couplinglist=edges + [(b, a) for a, b in edges]
        )

        for condition in ("ideal", "noisy"):
            simulator = AerSimulator(
                method="matrix_product_state",
                noise_model=noise if condition == "noisy" else None,
                max_parallel_threads=2
            )

            train_kernel, depth, cx = estimate_kernel(
                X_train, X_train, simulator, config, coupling, seed
            )
            test_kernel, _, _ = estimate_kernel(
                X_test, X_train, simulator, config, coupling, seed
            )

            train_kernel, min_eigenvalue = correct_training_kernel(
                train_kernel
            )

            model = SVC(kernel="precomputed", C=1.0)
            model.fit(train_kernel, y_train)
            predictions = model.predict(test_kernel)

            row = {
                "seed": seed,
                "processor": name,
                "condition": condition,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "shots": SHOTS,
                "accuracy": round(
                    accuracy_score(y_test, predictions), 4
                ),
                "mean_train_circuit_depth": round(depth, 2),
                "mean_train_cx_gates": round(cx, 2),
                "min_eigenvalue_before_correction": round(
                    min_eigenvalue, 6
                )
            }
            rows.append(row)
            print(row, flush=True)

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", newline="\n") as file:
    writer = csv.DictWriter(
        file, fieldnames=rows[0], lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)

print("Saved:", OUT)
print("Multi-seed simulated pilot; no hardware advantage claim.")
