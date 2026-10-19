
import csv
import json
import time
from pathlib import Path
from statistics import mean, stdev

from qiskit import transpile
from qiskit.circuit.library import zz_feature_map
from qiskit.transpiler import CouplingMap

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "qml_processor_architecture.csv"

SEEDS = [11, 21, 31, 41, 42]
ROWS = []

for processor_name in ["A", "B"]:
    config_path = ROOT / "processors" / f"processor_{processor_name}.json"
    config = json.loads(config_path.read_text())

    edges = [tuple(edge) for edge in config["coupling_edges"]]
    coupling = CouplingMap(
        couplinglist=edges + [(b, a) for a, b in edges]
    )

    for entanglement in ["linear", "full"]:
        feature_map = zz_feature_map(
            feature_dimension=4,
            reps=2,
            entanglement=entanglement
        )

        for seed in SEEDS:
            start = time.perf_counter()

            compiled = transpile(
                feature_map,
                basis_gates=config["basis_gates"],
                coupling_map=coupling,
                optimization_level=config["optimization_level"],
                seed_transpiler=seed
            )

            elapsed = time.perf_counter() - start
            ops = compiled.count_ops()

            row = {
                "processor": processor_name,
                "physical_qubits": config["qubits"],
                "logical_qubits": 4,
                "entanglement": entanglement,
                "seed": seed,
                "depth": compiled.depth(),
                "cx_gates": ops.get("cx", 0),
                "swap_gates": ops.get("swap", 0),
                "total_operations": sum(ops.values()),
                "transpilation_seconds": round(elapsed, 6)
            }

            ROWS.append(row)
            print(
                f"{processor_name} | {entanglement:6} | "
                f"seed={seed} | depth={row['depth']} | "
                f"CX={row['cx_gates']} | SWAP={row['swap_gates']}"
            )

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=ROWS[0].keys())
    writer.writeheader()
    writer.writerows(ROWS)

print("\n--- Summary (mean ± sample SD across seeds) ---")

for entanglement in ["linear", "full"]:
    for processor_name in ["A", "B"]:
        group = [
            row for row in ROWS
            if row["processor"] == processor_name
            and row["entanglement"] == entanglement
        ]

        def stats(key):
            values = [row[key] for row in group]
            return f"{mean(values):.2f} ± {stdev(values):.2f}"

        print(
            f"{processor_name} | {entanglement:6} | "
            f"depth={stats('depth')} | "
            f"CX={stats('cx_gates')} | "
            f"SWAP={stats('swap_gates')}"
        )

print(f"\nSaved: {OUT}")
